from .Strategy import Strategy
import matplotlib.pyplot as plt
from binance.client import Client
import time

class KD(Strategy):
    def __init__(self, parameter):
        super().__init__(parameter)

    def calculate_KD(self, parameter):
        pass
    
    def back_test(self, data, if_plot = TRUE):
        money = self.start_money
        storage = self.start_storage
        current_nine_price = []
        max_price = 0
        min_price = 0
        buy_record = [[], []]
        sell_record = [[], []]
    
        ## 最近九天的最低價
        for i in range(len(data)):
            current_nine_price.append(data["low"][i])
            if len(current_nine_price) >= 9:
                max_price = max(current_nine_price)
                min_price = min(current_nine_price)