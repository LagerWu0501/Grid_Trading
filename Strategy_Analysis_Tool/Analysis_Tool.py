import numpy as np
import pandas as pd
# from Strategies import *
# from Strategies.Strategy import Strategy
import Strategies
from Strategies import *

class Analysis_tool():
    def Shape_Ratio(strategy, dataset, risk_free_rate):
        profits = []
        for data in dataset:
            profits.append(strategy.back_test(data))
        return (np.average(profits) - risk_free_rate) / np.std(profits)

    def MDD():
        pass

