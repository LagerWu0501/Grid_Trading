import numpy as np
import pandas as pd
import Strategies
from matplotlib import pyplot as plt

class Analysis_tool():
    def Shape_Ratio(strategy, dataset, risk_free_rate, window_size = 2000, window_off = 10):
        profits = []
        for i in range(0, len(dataset) - window_size, window_off):
            data = dataset.loc[i : i + window_size]
            data.reset_index(inplace = True)
            profit, _, _, _, _ = strategy.back_test(data, if_plot = False) 
            profits.append(profit)
        return (np.average(profits) - risk_free_rate) / np.std(profits), np.average(profits)
    

