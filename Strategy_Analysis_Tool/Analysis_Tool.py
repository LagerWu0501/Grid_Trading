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
            profit, _, _, _ = strategy.back_test(data) 
            profits.append(profit)
        return (np.average(profits) - risk_free_rate) / np.std(profits)
    def MDD():
        pass
    
    def draw_backtest(strategy, data, profit, trading_count, buy_record, sell_record):
        fig, ax = plt.subplots()
        if (strategy.strategy_object != None):
            ax.set_yticks(strategy.strategy_object, minor=False)
        ax.yaxis.grid(True, which='major')
        plt.plot(data["close"], color="lightsteelblue")
        plt.scatter(buy_record[0], buy_record[1], color="black")
        plt.scatter(sell_record[0], sell_record[1], color = "red")
        plt.show()
        return

