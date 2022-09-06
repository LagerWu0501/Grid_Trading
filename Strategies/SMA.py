from .Strategy import Strategy
from matplotlib import pyplot as plt
from binance.client import Client
from datetime import datetime
import numpy as np
import time


class SMA(Strategy):
    def __init__(self, parameters):
        super().__init__(parameters)
        self.long_period = parameters["long_period"]
        self.short_period = parameters["short_period"]
        self.trading_logistic = parameters["trading_logistic"]
        self.trading_unit = parameters["trading_unit"]

    def trade(self, side, price, money, storage):
        amount = 0
        if (self.trading_logistic == "long"):
            if (self.trading_unit == "all_in"):
                if (side == "sell" and storage > 0):
                    amount = -1 * storage
                elif (side == "buy" and money > 0):
                    amount = money / price
            elif (self.trading_unit == "same_unit"):
                if (side == "sell" and storage >= self.unit):
                    amount = -1 * self.unit
                elif (side == "buy" and money >= self.unit * price):
                    amount = self.unit
            elif (self.trading_unit == "same_money"):
                if (side == "sell" and storage >= self.unit / price):
                    amount = -1 * self.unit / price
                elif (side == "buy" and money >= self.unit):
                    amount = self.unit / price

        elif (self.trading_logistic == "short"):
            if (self.trading_unit == "all_in"):
                if (side == "sell" and money > 0):
                    amount = -1 * money / price
                elif (side == "buy" and storage < 0):
                    amount = storage
            elif (self.trading_unit == "same_unit"):
                if (side == "sell" and money >= self.unit * price):
                    amount = -1 * self.unit
                elif (side == "buy" and storage <= -1 * self.unit):
                    amount = self.unit
            elif (self.trading_unit == "same_money"):
                if (side == "sell" and money > self.unit):
                    amount = -1 * self.unit / price
                elif (side == "buy" and money >= self.unit):
                    amount = self.unit

        elif (self.trading_logistic == "both"):
            if (self.trading_unit == "all_in"):
                if (side == "sell"):
                    amount = -1 * storage
                    if (storage > 0):
                        temp_money = money - amount * price
                        amount += temp_money / price
                elif (side == "buy"):
                    amount = storage
                    if (storage < 0):
                        temp_money = money - amount * price
                        amount += temp_money / price
            elif (self.trading_unit == "same_unit"):
                if (side == "sell"):
                    amount = -1 * self.unit
                    if (storage >= self.unit):
                        amount += -1 * self.unit
                elif (side == "buy" and storage <= -1 * self.unit):
                    amount = self.unit
                    if (storage <= -1 * self.unit):
                        amount += self.unit
            elif (self.trading_unit == "same_money"):
                if (side == "sell"):
                    amount = -1 * self.unit / price
                    if (storage > 0):
                        amount -= storage
                elif (side == "buy"):
                    amount = self.unit / price
                    if (storage <= 0):
                        amount -= storage
        else:
            print("trading logistic error.")
        money -= amount * price
        storage += amount
        return money, storage, price

    def back_test(self, data, parameters=None, if_plot=True):
        ## All in 
        short_sma = data["close"].rolling(self.short_period).mean()
        long_sma = data["close"].rolling(self.long_period).mean()
        signal = short_sma > long_sma
        signal = signal.astype(int).diff()
        # signal -- 0 == do nothing, 1 == buy, -1 == sell
        extracted_data = data.loc[(signal != 0) & (~signal.isna())]
        signal = signal[signal != 0].dropna()

        money = self.start_money
        storage = self.start_storage
        
        trading_count = 0
        buy_record = [[], []]
        sell_record = [[], []]
        max_profit = 0
        min_profit = np.inf
        MDD = 0
        indice = signal.index.to_list()
        
        for i in indice:
            if (i < self.long_period):
                continue
            money, storage, record = self.trade(signal[i], extracted_data["close"][i], money, storage)
            if (record > 0):
                buy_record[0].append(i)
                buy_record[1].append(record)
                trading_count += 1
            elif (record < 0):
                sell_record[0].append(i)
                sell_record[1].append(record)
                trading_count += 1
            temp_profit = (money + storage * data["close"][len(data) - 1])
            if (temp_profit > max_profit):
                max_profit = temp_profit
                min_profit = np.inf
            if (temp_profit < min_profit):
                min_profit = temp_profit
                if ((max_profit - min_profit) / max_profit > MDD):
                    MDD = (max_profit - min_profit) / max_profit

        profit = ((money + data["close"][len(data) - 1] * storage) - self.start_money - self.start_storage * data["open"][0]) / (self.start_money + self.start_storage * data["open"][0])
        if (if_plot):
            fig, ax = plt.subplots()
            ax.yaxis.grid(True, which = 'major')
            plt.plot(data["close"], color = "lightsteelblue")
            plt.plot(short_sma)
            plt.plot(long_sma)
            plt.scatter(buy_record[0], buy_record[1], color = "black")
            plt.scatter(sell_record[0], sell_record[1], color = "red")
            plt.show()
        return profit, trading_count, buy_record, sell_record, MDD