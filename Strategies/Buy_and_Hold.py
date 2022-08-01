from calendar import c
from Strategy import Strategy
import datetime

class Buy_and_Hold(Strategy):
    def back_test(self, data):
        self.open_price = data["open"][0]
        self.close_price = data["close"][len(data) - 1]
        diff = self.open_price - self.close_price
        return diff / self.open_price
    
    