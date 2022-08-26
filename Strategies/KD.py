from .Strategy import Strategy
import matplotlib.pyplot as plt
from binance.client import Client
import pandas as pd
import numpy as np

class KD(Strategy):
    def __init__(self, data, parameter):
        super().__init__(parameter)

    def calculate_KD(self, data, parameter)->list:
        # n : 9 or 14 days
        # RSV : (今日收盤價 - 最近 n 天的最低價) / (最近 n 天最高價 - 最近 n 天最低價) * 100
        # 今日 k 值 : 昨日 k 值 * (2/3) + 今日 RSV * (1/3)
        # 今日 D 值 : 昨日 D 值 * (2/3) + 今日 K 值 * (1/3)
        current_max_price = []  # start from the ninth day
        current_min_price = []
        RSV = [] # n = 9
        K_value = []
        D_value = []
        
        ## min & max price in 9 current days
        for i in range(len(data)):
            current_max_price[i] = data["high"][i]
            current_min_price[i] = data["low"][i]
            K_value.append(50) # if there is no K/D value then add 50
            D_value.append(50)
            if i + 1 >= 9:
                current_max_price.append(max(range(data["high"][i + 1 - 9], data["high"][i])))
                current_min_price.appned(min(range(data["low"][i + 1 - 9], data["low"][i])))
                RSV.append((data["close"][i] - current_min_price[i]) / (current_max_price[i] - current_min_price[i]) * 100)
                K_value.append(K_value[i - 1] * (2/3) + RSV[i] * (1/3))
                D_value.append(D_value[i - 1] * K_value[i] * (1/3))
    
        return RSV, K_value, D_value
        
        
    def enable_to_buy(self, data, money, i)->bool:
        if (money - data["close"][i] * self.buy_unit * (1 + self.trading_fee_rate) >= 0):
            return True
        else:
            return False


    def back_test(self, data, parameter, if_plot = TRUE):
        money = self.start_money
        storage = self.start_storage
        buy_record = [[], []]
        sell_record = [[], []]
        RSV, K, D = self.calculate_KD(data, parameter)
        
        for i in range(len(data)):
            if i + 1 >= 9:
                # Buy
                if self.enable_to_buy(data, money, i) == True:
                    if (K[i] > 80 and D[i] < 20) or (D[i] < 15):
                        money -= data["close"][i] * self.buy_unit * (1 + self.trading_fee_rate) >= 0
                        storage += self.buy_unit
                        buy_record[0].append(i)
                        buy_record[1].append(data["close"][i])
                
                # Sell
                if storage > 0:
                    if (K[i] > 80 and D[i] > 70) or (D[i] > 85):
                        money += data["close"][i] * self.buy_unit * (1 - self.trading_fee_rate)
                        storage -= self.buy_unit
                        sell_record[0].append(i)
                        sell_record[1].append(data["close"][i])
                        
            if if_plot == True:
                pass
                
                
            
    
    def intime_test(self):
        pass
        