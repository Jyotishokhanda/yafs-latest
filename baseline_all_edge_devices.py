import pandas as pd
from yafs.core import Sim
from yafs.application import Application, Message
from yafs.population import *
from yafs.selection import Selection
from yafs.topology import Topology
from simpleSelection import CustomPath
from simplePlacement import CloudPlacement
from yafs.stats import Stats
from yafs.distribution import deterministicDistribution
from yafs.utils import fractional_selectivity
import time
import numpy as np
import sys
import argparse
sys.dont_write_bytecode = True

base_line_data = pd.DataFrame(columns=["state","Edge_Device_0","Edge_Device_1","Edge_Device_2","Edge_Device_3","Edge_Device_4","Edge_Device_5","Edge_Device_6","Edge_Device_7","Edge_Device_8","Edge_Device_9","Min Latency"])
state_edge_device_mapper = dict()

def reward(obs_latency,src,dest):
    # print("source: ",src)
    # print("dest: ",dest - smallest_node)
    # print("latency: ",obs_latency)

    destination = (dest - smallest_node)
    if str(edges_state) not in state_edge_device_mapper.keys():
        state_edge_device_mapper[str(edges_state)] = dict()
    
    if destination in state_edge_device_mapper[str(edges_state)].keys():
        temp_latency = state_edge_device_mapper[str(edges_state)][destination]
        state_edge_device_mapper[str(edges_state)][destination] = min(temp_latency,obs_latency)

    state_edge_device_mapper[str(edges_state)][destination] = obs_latency
    # print("successfully calculated the latency")

def get_action(s_node,state):
    global smallest_node

    smallest_node = s_node
    global edges_state
    edges_state = state  

    # print("action chosen successfully")


# @profile
def main(get_action,reward,add_time, iteration, simulated_time):

    # random.seed(RANDOM_SEED)
    # np.random.seed(RANDOM_SEED)

    """
    PLACEMENT algorithm
    """
    placement = CloudPlacement(
        "onCloud")  # it defines the deployed rules: module-device
    # apply the algo on service A
    placement.scaleService({"ServiceA": 2})

    """--
    SELECTOR algorithm
    """
    # Their "selector" is actually the shortest way, there is not type of orchestration algorithm.
    # This implementation is already created in selector.class,called: First_ShortestPath
    selectorPath = CustomPath(Selection,get_action,execution_type="baseline_all_edge_devices")
    selectorPath.create_topology()
    selectorPath.set_population()

    """
    SIMULATION ENGINE
    """

    stop_time = simulated_time
    s = Sim(True,reward,selectorPath.topology, add_time,
            default_results_path="Results_" + str(iteration))
    s.deploy_app(selectorPath.app, placement, selectorPath.pop, selectorPath)
    selectorPath.init_state(s)
    s.run(stop_time, selectorPath, show_progress_monitor=False)



def driver(get_action,reward):
    start_time = time.time()

    add_time = 0

    for i in range(1):

        main(get_action,reward,add_time, i, simulated_time=230)

        add_time += 100

        m = Stats(defaultPath="Results_" + str(i))  # Same name of the results
        time_loops = [["M.A", "M.B"]]


if __name__ == '__main__':

    for i in range(30):
        print("episode running {}/{}".format(i+1,30))
        driver(get_action,reward)

    for sedm in state_edge_device_mapper.keys():

        edge_data = state_edge_device_mapper[str(sedm)]
        
        min_latency = min(list(edge_data.values()))
        avg_latency = sum(list(edge_data.values())) / len(edge_data)

        for i in range(9):
            if i not in edge_data.keys():
                edge_data[i] = avg_latency

        base_line_data = base_line_data.append({
            "state": str(sedm),
            "Edge_Device_0": edge_data[0],
            "Edge_Device_1":edge_data[1],
            "Edge_Device_2":edge_data[2],
            "Edge_Device_3":edge_data[3],
            "Edge_Device_4":edge_data[4],
            "Edge_Device_5":edge_data[5],
            "Edge_Device_6":edge_data[6],
            "Edge_Device_7":edge_data[7],
            "Edge_Device_8":edge_data[8],
            "Edge_Device_9":edge_data[9],
            "Min Latency": min_latency
        },ignore_index=True)
        # print("\n")

base_line_data.to_csv("baseline_all_edge_devices.csv",index=False)
    

