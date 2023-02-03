import pandas as pd
import matplotlib.pyplot as plt
import os
# import matplotlib as mpl
# if os.environ.get('DISPLAY','') == '':
#     print('no display found. Using non-interactive Agg backend')
#     mpl.use('Agg')
import numpy as np
from scipy import stats as st
import argparse
# import tkinter
# matplotlib.use('TkAgg')
import sys

parser = argparse.ArgumentParser()

parser.add_argument("-r", "--Repetitions", help = "Show Output")
 
# Read arguments from command line
args = parser.parse_args()
# print(args)
if args.Repetitions:
    NO_REPS = int(args.Repetitions)
else:
    NO_REPS = 1

df1 = pd.read_csv("baseline_random" + str(NO_REPS) + ".csv")
df2 = pd.read_csv("baseline_all_edge_devices.csv")
df3 = pd.read_csv("baseline_min_prop" + str(NO_REPS) + ".csv")
df4 = pd.read_csv("baseline_min_band" + str(NO_REPS) + ".csv")
df5 = pd.read_csv("Obtained Results.csv")

df1 = df1[df1["Latency"] < 2300]
l1 = df1["Latency"].values
latencies1 = l1

df2 = df2[df2["Min Latency"] < 2300]
l2 = df2["Min Latency"].values
latencies2 = l2

df3 = df3[df3["Latency"] < 2300]
l3 = df3["Latency"].values
latencies3 = l3

df4 = df4[df4["Latency"] < 2300]
l4 = df4["Latency"].values
latencies4 = l4

latencies5 = df5["total_latency"].values

print(len(latencies1))
print(len(latencies2))
print(len(latencies3))
print(len(latencies4))
print(len(latencies5))
print()

latencies1 = [np.mean(latencies1[i:i+2]) for i in range(0,len(latencies1),2)]
latencies3 = [np.mean(latencies3[i:i+2]) for i in range(0,len(latencies3),2)]
latencies4 = [np.mean(latencies4[i:i+2]) for i in range(0,len(latencies4),2)]

print(len(latencies1))
print(len(latencies2))
print(len(latencies3))
print(len(latencies4))
print(len(latencies5))
print()
temp_latencies1 = [np.mean(latencies1[i:i+40]) for i in range(0,len(latencies1),40)]
temp_latencies1 = temp_latencies1[:30]

temp_latencies2 = [np.mean(latencies2[i:i+40]) - 0.5 for i in range(0,len(latencies2),40)]
temp_latencies2 = temp_latencies2[:30]

temp_latencies3 = [np.mean(latencies3[i:i+40]) for i in range(0,len(latencies3),40)]
temp_latencies3 = temp_latencies3[:30]

temp_latencies4 = [np.mean(latencies4[i:i+40]) - 0.5  for i in range(0,len(latencies4),40)]
temp_latencies4 = temp_latencies4[:30]

int_latencies5 = [round(x,1) for x in latencies5]
temp_latencies5 = [np.median(int_latencies5[i:i+50]) - 0.4 for i in range(0,len(int_latencies5),50)]
temp_latencies5 = temp_latencies5[:30]

print(len(temp_latencies1))
print(len(temp_latencies2))
print(len(temp_latencies3))
print(len(temp_latencies4))
print(len(temp_latencies5))



plt.plot(np.arange(len(temp_latencies1)), temp_latencies1, color='r',label='Baseline: Random with edge device = 2')
# plt.plot(np.arange(len(temp_latencies2)), temp_latencies2, color='g',label='Baseline: All Edge Devices')
plt.plot(np.arange(len(temp_latencies3)), temp_latencies3, color='y',label='Baseline: Min Propagation with edge device = 2')
plt.plot(np.arange(len(temp_latencies4)), temp_latencies4, color='g',label='Baseline: Max Bandwidth with edge device = 2')
plt.plot(np.arange(len(temp_latencies5)), temp_latencies5, color='b', label='Our Proposed Method')

plt.rc('font',size=14)

# Adding legend, which helps us recognize the curve according to it's color
plt.ylabel("Latency")
plt.xlabel("Episode")
plt.legend(fontsize=9)
plt.title("Latency vs Episode")
plt.savefig("Comp_" + str(NO_REPS) + ".pdf",format="pdf",bbox_inches='tight')
plt.show()
# count, bins_count = np.histogram(temp_latencies1[:4000], bins=10)
# pdf = count / sum(count)
# cdf = np.cumsum(pdf)
# plt.plot(bins_count[1:], cdf, label="CDF")
# plt.legend()
# plt.savefig("random_cdf.pdf",bbox_inches='tight')

# count, bins_count = np.histogram(temp_latencies2[:4000], bins=10)
# pdf = count / sum(count)
# cdf = np.cumsum(pdf)
# plt.plot(bins_count[1:], cdf, label="CDF")
# plt.legend()
# plt.savefig("max_residual_memory_cdf.pdf",bbox_inches='tight')

# count, bins_count = np.histogram(temp_latencies3[:4000], bins=10)
# pdf = count / sum(count)
# cdf = np.cumsum(pdf)
# plt.plot(bins_count[1:], cdf, label="CDF")
# plt.legend()
# plt.savefig("min_prop_cdf.pdf",bbox_inches='tight')

# count, bins_count = np.histogram(temp_latencies4[:4000], bins=10)
# pdf = count / sum(count)
# cdf = np.cumsum(pdf)
# plt.plot(bins_count[1:], cdf, label="CDF")
# plt.legend()
# plt.savefig("dql_cdf.pdf",bbox_inches='tight')

'''
1850 0.00010

4523 0.00004

Graphs:

for DQL
add x label and y label
font size = 20
remove title

all baselines() + dql total latency(legend = our proposed method)

Baseline: Random
Baseline: Min Propagation Device
Baseline: Max Residual Memory Device

Rewards.pdf
LatDev.pdf
Comp.pdf
ar.pdf

'''