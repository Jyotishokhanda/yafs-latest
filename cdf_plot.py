import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df1 = pd.read_csv("baseline_random.csv")

latencies4 = df1["total_latency"].values