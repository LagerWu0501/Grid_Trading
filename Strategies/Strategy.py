import numpy as np
import pandas as pd


class Strategy:
    def __init__(self, parameters):
        ## Parameters for general strategies
        self.name = parameters["name"]
        self.start_money = parameters["start_money"]
        self.start_storage = parameters["start_storage"]
        self.trading_fee_rate = parameters["trading_fee_rate"]
        self.buy_unit = parameters["buy_unit"]

    def back_test(self, data, parameters = None):
        pass
        