from yafs.selection import Selection
from yafs.distribution import deterministicDistribution
from yafs.population import *
import networkx as nx
from yafs.topology import Topology
import random
import numpy as np
import time
from yafs.utils import fractional_selectivity
from yafs.stats import Stats
from simplePlacement import CloudPlacement
from yafs.topology import Topology
from yafs.placement import *
from yafs.population import *
from yafs.application import Application, Message
import argparse
import sys
import random
import pandas as pd


HISTORY_LENGTH = 5


def create_application():
    # APPLICATION
    a = Application(name="SimpleCase")

    # (S) --> (ServiceA) --> (A)
    a.set_modules([{"Sensor": {"Type": Application.TYPE_SOURCE}},
                   {"ServiceA": {"Type": Application.TYPE_MODULE}},
                   {"Actuator": {"Type": Application.TYPE_SINK}}
                   ])
    """
    Messages among MODULES (AppEdge in iFogSim)
    """
    m_a = Message("M.A", "Sensor", "ServiceA",
                  instructions=20*10 ^ 6, bytes=1000)
    m_b = Message("M.B", "ServiceA", "Actuator",
                  instructions=10*10 ^ 6, bytes=750)

    """
    Defining which messages will be dynamically generated # the generation is controlled by Population algorithm
    """
    a.add_source_messages(m_a)

    """
    MODULES/SERVICES: Definition of Generators and Consumers (AppEdges and TupleMappings in iFogSim)
    """
    # MODULE SERVICES
    a.add_service_module("ServiceA", m_a, m_b,
                         fractional_selectivity, threshold=1.0)

    return a


class CustomPath(Selection):

    def __init__(self, s,get_action,execution_type):

        Selection.__init__(self, s)
        self.topology = Topology()
        self.number_of_compute_nodes = 0
        self.number_of_sensor_nodes = 0
        self.pop = None
        self.app = None
        self.data = []
        self.get_action = get_action
        self.test_sensor = 0
        self.execution_type = execution_type
    def init_state(self, sim):
        self.states = []

        # self.latencies = []

        for node, val in sim.topology.nodeAttributes.items():
            if "sensor" in val["model"]:
                self.test_sensor = node
                break

    def set_population(self):

        self.app = create_application()

        self.pop = Statical("Statical")

        self.pop.set_sink_control(
            {"model": "actuator-device", "number": 1, "module": self.app.get_sink_modules()})

        dDistribution = deterministicDistribution(
            name="Deterministic", time=40)

        for i in range(self.number_of_sensor_nodes):

            self.pop.set_src_control({"model": "sensor-device-"+str(i+1), "number": 1,
                                      "message": self.app.get_message("M.A"), "distribution": dDistribution})

    def create_dynamic_links(self, t):
        
        # print("sensors around Edge 0 = ",self.data[0])
        # print("sum of sensor IDs = ",max(self.data))
        for i in range(self.number_of_sensor_nodes):

            for j in range(self.number_of_compute_nodes):

                if i < self.data[j]:
                    link = {"s": i, "d": j + self.number_of_sensor_nodes + 1, "BW": 1,
                                    "PR": random.randint(1, 10)}

                    t["link"].append(link)

        for j in range(self.number_of_compute_nodes):

            link = {"s": j + self.number_of_sensor_nodes + 1, "d": self.number_of_sensor_nodes, "BW": 1,
                    "PR": random.randint(1, 10)}

            t["link"].append(link)

        return t

    def create_dynamic_json_topology(self):
        """
        TOPOLOGY DEFINITION

        Some attributes of fog entities (nodes) are approximate

        """

        # MANDATORY FIELDS

        sensor_vicinity_data = pd.read_csv("Edge Device Vicinity Data.csv")

        sensor_vicinity_data_size = sensor_vicinity_data.shape[0]

        values = sensor_vicinity_data.sample()

        values = values.values

        values = values[0][1:]

        for val in values:

            if val > 100:
                self.data.append((val/200) + 2)
            elif val > 10 and val < 100:
                self.data.append((val/20) + 2)
            else:
                self.data.append(val + 2)

        # print("sensors = ",self.data)
        self.number_of_sensor_nodes = max(self.data)
        # print(self.number_of_sensor_nodes)
        self.number_of_compute_nodes = 10

        # print("sensors : ", self.number_of_sensor_nodes)
        # print("edges : ", self.number_of_compute_nodes)

        topology_json = {}
        topology_json["entity"] = []
        topology_json["link"] = []

        cloud_dev = {"mytag": "cloud",
                     "IPT": 2500 * 10 ^ 6, "RAM": 20000, "COST": 2, "WATT": 10.0, "devices": [], "device_bandwidth": 10, "services": set(), "unitilised_bandwidth": 0, "sensors_accessing": set(), "peak_memory": 0, "residual_memory": 20000}
        # change the number of sensors at an interval of 60 time units

        for i in range(self.number_of_sensor_nodes):

            sensor_dev = {"id": i, "model": "sensor-device-"+str(i+1),
                          "IPT": 100 * 10 ^ 6, "RAM": 4000, "COST": 3, "WATT": 40.0, "device_bandwidth": 500000}

            topology_json["entity"].append(sensor_dev)

        actuator_dev = {"id": self.number_of_sensor_nodes, "model": "actuator-device",
                        "IPT": 100 * 10 ^ 6, "RAM": 4000, "COST": 3, "WATT": 40.0}

        topology_json["entity"].append(actuator_dev)

        ID = self.number_of_sensor_nodes + 1

        for i in range(self.number_of_compute_nodes):

            cloud_dev["id"] = ID

            cloud_dev["model"] = "cloud-" + str(ID - 20)

            topology_json["entity"].append(cloud_dev.copy())

            ID += 1

        return topology_json

    def create_topology(self):

        t_json = self.create_dynamic_json_topology()

        t_json_final = self.create_dynamic_links(t_json)

        self.topology.load(t_json_final)

        self.topology.show()

    def update_topology(self, sim, app_name):

        value = {"mytag": "cloud"}  # or whatever tag
        id_cluster = self.topology.find_IDs(value)
        num_services = {}
        for one_node in id_cluster:
            # print "lol"
            # print sim.topology.nodeAttributes[one_node]["services"]
            num_services[one_node] = len(
                self.topology.nodeAttributes[one_node]["services"])
        # print num_services

    def get_path(self, sim, app_name, message, topology_src, alloc_DES, alloc_module, traffic, from_des):
        """
            Computes the minimun path among the source elemento of the topology and the localizations of the module

            Return the path and the identifier of the module deployed in the last element of that path
            """

        if self.var == 1:
            # print sim.topology.get_nodes_att()
            self.node_dict = sim.topology.get_nodes_att()
            # print(self.node_dict)
            for key, value in self.node_dict.items():
                if 'cloud' in value["model"]:
                    self.dict[key] = sim.env.now
            # print self.dict
            self.var = 0

        node_src = topology_src
        DES_dst = alloc_module[app_name][message.dst]

        curr_traff = traffic
        
        global final_node

        if message.src == "Sensor":
            new_arr = []
            new_path = []
            if node_src == self.test_sensor:
                # print("This is the test sensor")
                # State Computation
                value = {"mytag": "cloud"}
                id_cluster = sim.topology.find_IDs(value)
                # print("Updating.....")
                # print(sim.env.now)
                # print("check 1")
                current_state = dict()
                current_bandwidths = dict()
                current_prs = dict()
                cpu_utils = dict()
                memories = dict()
                current_inst = dict()
                all_links = sim.topology.get_edges()

                smallest_node = min(id_cluster)

                # print("the minimum ID of edges is : ", smallest_node)
                expected_latencies = []
                # print("id_cluster = ",id_cluster)
                for edge_node in id_cluster:
                    one_link = (self.test_sensor, edge_node)
                    if one_link not in all_links:
                        one_link = (edge_node, self.test_sensor)
                    if one_link not in all_links:
                        continue

                    expected_latencies.append(sim.get_expected_latency(node_src,edge_node,message))
                    band_val = sim.topology.get_edge(
                        one_link)[sim.topology.LINK_BW]
                    pr_val = sim.topology.get_edge(one_link)['PR']
                    current_bandwidths[edge_node-smallest_node] = (band_val, band_val)
                    current_prs[edge_node-smallest_node] = pr_val
                    current_inst[edge_node-smallest_node] = (message.inst, 2500000000 - message.inst)
                    memories[edge_node-smallest_node] = (sim.topology.nodeAttributes[edge_node]["peak_memory"],
                                           sim.topology.nodeAttributes[edge_node]["residual_memory"])
                
                # print("check 3")
                # print("expected_latencies: ",expected_latencies)
                expected_latencies.sort()
                # print("expected latencies = ",expected_latencies)
                required_latency = expected_latencies[1]
                current_state["bandwidth"] = current_bandwidths
                current_state["PR"] = current_prs
                current_state["inst"] = current_inst
                current_state["memories"] = memories
                current_state["input_size"] = message.bytes
                
                # print(current_state)

                # print current_state
                self.states.append(current_state)

                # change 5 to a global variable =  history of the states

                if len(self.states) > HISTORY_LENGTH:
                    self.states.pop(0)

                # print("printing states :")
                # print(self.states)
                #####
                # print("check 4")
                
                if self.execution_type == "baseline_all_edge_devices":
                    self.get_action(smallest_node,current_state)
                    list_node_id = [0,1,2,3,4,5,6,7,8,9]

                elif self.execution_type == "baseline_min_prop":
                    node_id = self.get_action(smallest_node,current_state)
                    list_node_id = node_id
                
                elif self.execution_type == "baseline_max_residual_memory":
                    node_id = self.get_action(smallest_node,current_state)
                    list_node_id = node_id
                
                elif self.execution_type == "baseline_min_band":
                    node_id = self.get_action(smallest_node,current_state)
                    list_node_id = node_id
                
                elif self.execution_type == "baseline_random":
                    node_id = self.get_action(smallest_node,current_state)
                    list_node_id = node_id
                    
                elif self.execution_type == "dql":    
                    list_node_id = self.get_action(current_state,required_latency)
                # print("check 5")
                
                for m in range(len(list_node_id)):
                    list_node_id[m] += smallest_node
                # print("Predicted_action = ",list_node_id)
                # print("smallest edge : ", smallest_node)
                # print("Edges : ", list_node_id)

                alloc_des_reverse = {v: k for k, v in alloc_DES.iteritems()}

                for one_node in list_node_id:

                    this_des = alloc_des_reverse[one_node]
                    this_path = list(nx.shortest_path(sim.topology.G,
                                         source=node_src, target=one_node))
                    new_arr.append(this_des)
                    new_path.append(this_path)

                bestPath =new_path
                bestDES = new_arr
                final_node = list_node_id
      
            else:

                # Select Node
                destination_nodes = set()
                for a in DES_dst:
                    destination_nodes.add(alloc_DES[a])
                # print("destination nodes : ", destination_nodes)

                min_val = 10000000
                final_node = 0
                alloc_des_reverse = {v: k for k, v in alloc_DES.iteritems()}

                value = {"mytag": "cloud"}
                id_cluster = sim.topology.find_IDs(value)
                # print("Updating.....")
                # print(sim.env.now)
                all_links = sim.topology.get_edges()

                smallest_node = min(id_cluster)
                    
                for single_node in destination_nodes:

                    one_link = (node_src, single_node)
                    if one_link not in all_links:
                        one_link = (single_node, node_src)
                    if one_link not in all_links:
                        continue

                    if self.dict[single_node] < min_val:
                        min_val = self.dict[single_node]
                        final_node = single_node

                path = list(nx.shortest_path(sim.topology.G,
                                            source=node_src, target=final_node))
                bestPath = [path]
                alloc_des_reverse = {v: k for k, v in alloc_DES.iteritems()}
                final_des = alloc_des_reverse[final_node]
                bestDES = [final_des]
                final_node = [final_node]

            for one_final_node in final_node:
                sim.topology.nodeAttributes[one_final_node]["sensors_accessing"].add(
                    node_src)


                size_bits = message.bytes

                link = (node_src, one_final_node)

                transmit = size_bits / (sim.topology.get_edge(link)
                                        [Topology.LINK_BW] * 1000000.0)

                propagation = sim.topology.get_edge(link)[Topology.LINK_PR]


                ipt = 1

                for key, value in self.node_dict[one_final_node].items():

                    if key == 'IPT':

                        ipt = float(value)

                if self.dict[one_final_node] < sim.env.now + transmit + propagation:

                    self.dict[one_final_node] = sim.env.now

                    self.dict[one_final_node] += (message.inst / ipt) + \
                        transmit + propagation

                else:

                    self.dict[one_final_node] += message.inst / ipt

        else:
            dst_node = 0
            for des in DES_dst:  
                dst_node = alloc_DES[des]

                path = list(nx.shortest_path(sim.topology.G,
                                             source=node_src, target=dst_node))

                bestPath = [path]
                bestDES = [des]

        return bestPath, bestDES
