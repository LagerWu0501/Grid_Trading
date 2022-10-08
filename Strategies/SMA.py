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
        self.trading_fee = 0

    def trade(self, side, price, money, storage):
        amount = 0
        new_money = money
        new_storage = storage

        if (self.trading_logistic == "long"):
            if (self.trading_unit == "all_in"):
                if (side == -1 and storage > 0):
                    amount = -1 * storage
                elif (side == 1 and money > 0):
                    amount = money / price
            elif (self.trading_unit == "same_unit"):
                if (side == -1 and storage >= self.unit):
                    amount = -1 * self.unit
                elif (side == 1 and money >= self.unit * price):
                    amount = self.unit
            elif (self.trading_unit == "same_money"):
                if (side == -1 and storage >= self.unit / price):
                    amount = -1 * self.unit / price
                elif (side == 1 and money >= self.unit):
                    amount = self.unit / price

        elif (self.trading_logistic == "short"):
            if (self.trading_unit == "all_in"):
                if (side == -1 and money > 0):
                    amount = -1 * money / price
                elif (side == 1 and storage < 0):
                    amount = storage
            elif (self.trading_unit == "same_unit"):
                if (side == -1 and money >= self.unit * price):
                    amount = -1 * self.unit
                elif (side == 1 and storage <= -1 * self.unit):
                    amount = self.unit
            elif (self.trading_unit == "same_money"):
                if (side == -1 and money > self.unit):
                    amount = -1 * self.unit / price
                elif (side == 1 and money >= self.unit):
                    amount = self.unit

        elif (self.trading_logistic == "both"):
            if (self.trading_unit == "all_in"):
                if (side * storage < 0):
                    temp_money = money + storage * price
                    amount = temp_money / price
                    amount -= side * storage
                else:
                    amount = money / price
                amount *= side

            elif (self.trading_unit == "same_unit"):
                if (side == -1):
                    amount = -1 * self.unit
                    if (storage >= self.unit):
                        amount += -1 * self.unit
                elif (side == 1 and storage <= -1 * self.unit):
                    amount = self.unit
                    if (storage <= -1 * self.unit):
                        amount += self.unit
            elif (self.trading_unit == "same_money"):
                if (side == -1):
                    amount = -1 * self.unit / price
                    if (storage > 0):
                        amount -= storage
                elif (side == 1):
                    amount = self.unit / price
                    if (storage <= 0):
                        amount -= storage
        else:
            print("trading logistic error.")
        new_money -= amount * price
        new_storage += amount
        self.trading_fee += abs(amount * price) * self.trading_fee_rate

        # print("n", new_money, new_storage)
        # print("===========================")
        return new_money, new_storage, price, 

    def back_test(self, data, parameters=None, if_plot=True):
        self.trading_fee = 0
        ## All in 
        if (self.name == "SMA"):
            short_sma = data["close"].rolling(self.short_period).mean()
            long_sma = data["close"].rolling(self.long_period).mean()
        elif (self.name == "EMA"):
            short_sma = data["close"].ewm(span = self.short_period, adjust = False).mean()
            long_sma = data["close"].ewm(span = self.long_period, adjust = False).mean()

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
            temp_profit = (money + storage * extracted_data["close"][i])
            if (temp_profit > max_profit):
                max_profit = temp_profit
                min_profit = np.inf
            if (temp_profit < min_profit):
                min_profit = temp_profit
                if ((max_profit - min_profit) / max_profit > MDD):
                    MDD = (max_profit - min_profit) / max_profit

        # print(money, data["close"][len(data) - 1] * storage)
        profit = ((money + data["close"][len(data) - 1] * storage - self.trading_fee) - self.start_money - self.start_storage * data["open"][0]) / (self.start_money + self.start_storage * data["open"][0])
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