from .Strategy import Strategy
from matplotlib import pyplot as plt
from binance.client import Client

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
    
    def intime_test(self, symbol, timeframe, time_len):
        client = Client()
        money = self.start_money
        storage = self.start_storage

        pass
    
    