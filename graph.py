import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df1 = pd.read_csv("baseline_random_8.csv")
df2 = pd.read_csv("baseline_max_residual_memory_8.csv")
df3 = pd.read_csv("baseline_min_prop_8.csv")
df4 = pd.read_csv("Obtained Results.csv")

df1 = df1[df1["Latency"] < 2300]
l1 = df1["Latency"].values
print(len(l1))
latencies1 = l1

df2 = df2[df2["Latency"] < 2300]
l2 = df2["Latency"].values
latencies2 = l2

df3 = df3[df3["Latency"] < 2300]
l3 = df3["Latency"].values
latencies3 = l3

latencies4 = df4["total_latency"].values
print(max(latencies4))
print(min(latencies4))
print()
print(len(latencies1))

latencies1 = [np.mean(latencies1[i:i+5]) for i in range(0,len(latencies1),5)]
latencies2 = [np.mean(latencies2[i:i+5]) for i in range(0,len(latencies2),5)]
latencies3 = [np.mean(latencies3[i:i+5]) for i in range(0,len(latencies3),5)]

print(len(latencies1))
print(len(latencies2))
print(len(latencies3))
print(len(latencies4))
# temp_latencies = [np.mean(latencies[i:i+200]) for i in range(0,len(latencies),200)]
temp_latencies1 = [np.mean(latencies1[i:i+400]) for i in range(0,len(latencies1),400)]
temp_latencies1 = temp_latencies1[:30]

temp_latencies2 = [np.mean(latencies2[i:i+400]) for i in range(0,len(latencies2),400)]
temp_latencies2 = temp_latencies2[:30]

temp_latencies3 = [np.mean(latencies3[i:i+400]) for i in range(0,len(latencies3),400)]
temp_latencies3 = temp_latencies3[:30]
# temp_latencies3 = [x+2 for x in temp_latencies3]

temp_latencies4 = [np.mean(latencies4[i:i+400]) for i in range(0,len(latencies4),400)]

print(len(temp_latencies1))
print(len(temp_latencies2))
print(len(temp_latencies3))
print(len(temp_latencies4))

# plt.figure(figsize=(20,20))
plt.rc('font',size=20)

plt.plot(np.arange(len(temp_latencies1)), temp_latencies1, color='r',label='Baseline: Random with r=8')
plt.plot(np.arange(len(temp_latencies2)), temp_latencies2, color='g',label='Baseline: Max Residual Memory Device with r=8')
plt.plot(np.arange(len(temp_latencies3)), temp_latencies3, color='y',label='Baseline: Min Propagation Device with r=8')
plt.plot(np.arange(len(temp_latencies4)), temp_latencies4, color='b', label='Our Proposed Method')

# Adding legend, which helps us recognize the curve according to it's color
plt.ylabel("Latency")
plt.xlabel("Episode")
plt.legend(fontsize=12)
# plt.title("Latency vs Episode")
# plt.show()
plt.savefig("Comp_8.pdf",bbox_inches='tight')

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