from calendar import c
from Strategy import Strategy
import datetime

class Buy_and_Hold(Strategy):
    def back_test(self, data):
        open_price = data["open"][0]
        close_price = data["close"][len(data) - 1]
        diff = open_price - close_price
        return diff / open_price, 2, [[0], [open_price]], [[len(data) - 1], [close_price]]
    
    