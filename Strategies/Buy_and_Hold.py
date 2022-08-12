from .Strategy import Strategy


class Buy_and_Hold(Strategy):
    def __init__(self, parameters):
        super().__init__(parameters)

    def back_test(self, data):
        open_price = data["open"][0]
        close_price = data["close"][len(data) - 1]
        diff = close_price - open_price
        return diff / open_price, 2, [[0], [open_price]], [[len(data) - 1], [close_price]]
    
    