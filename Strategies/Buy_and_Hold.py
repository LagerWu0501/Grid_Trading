from .Strategy import Strategy
from matplotlib import pyplot as plt
from binance.client import Client
from datetime import datetime
import time

class Buy_and_Hold(Strategy):
    def __init__(self, parameters):
        super().__init__(parameters)

    def back_test(self, data, if_plot = True):
        open_price = data["open"][0]
        close_price = data["close"][len(data) - 1]
        diff = close_price - open_price
        if (if_plot):
            fig, ax = plt.subplots()
            ax.yaxis.grid(True, which = 'major')
            plt.plot(data["close"], color = "lightsteelblue")
            plt.scatter([0], [open_price], color = "black")
            plt.scatter([len(data) - 1], [close_price], color = "red")
            plt.show()
        return diff / open_price, 2, [[0], [open_price]], [[len(data) - 1], [close_price]]
    
    def intime_test(self, symbol, timeframe, time_len, if_plot = True):
        # init
        client = Client()
        money = self.start_money
        storage = self.start_storage
        prices = []
        self.print_state(money, storage, 0, 0)
        # get price and buy
        buy_price = float(client.get_ticker(symbol=symbol)["lastPrice"])
        prices.append(buy_price)
        storage += money / buy_price
        money -= money
        self.print_state(money, storage, buy_price, 1)
        # sleep
        pt = datetime.strptime(time_len,'%H:%M:%S,%f')
        total_seconds = pt.second + pt.minute*60 + pt.hour*3600
        pt = datetime.strptime(timeframe,'%H:%M:%S,%f')
        timeframe_seconds = pt.second + pt.minute*60 + pt.hour*3600
        while total_seconds >= timeframe_seconds:
            total_seconds -= timeframe_seconds
            prices.append(float(client.get_ticker(symbol=symbol)["lastPrice"]))
            time.sleep(timeframe_seconds)
        # get price and sell
        sell_price = float(client.get_ticker(symbol=symbol)["lastPrice"])
        prices.append(sell_price)
        money += storage * sell_price
        storage -= storage
        self.print_state(money, storage, sell_price, 2)
        if (if_plot):
            fig, ax = plt.subplots()
            ax.yaxis.grid(True, which = 'major')
            plt.plot(prices, color = "lightsteelblue")
            plt.scatter([0], buy_price, color = "black")
            plt.scatter(len(prices) - 1, sell_price, color = "red")
            plt.show()
        return
    
    