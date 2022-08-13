from datetime import datetime
class Strategy:
    def __init__(self, parameters):
        ## Parameters for general strategies
        self.name = parameters["name"]
        self.start_money = parameters["start_money"]
        self.start_storage = parameters["start_storage"]
        self.trading_fee_rate = parameters["trading_fee_rate"]
        self.buy_unit = parameters["buy_unit"]

    def back_test(self, data, parameters = None, if_plot = True):
        pass
        
    def intime_test(self, symbol, timeframe, time_len):
        pass

    def print_state(self, current_money, current_storage, current_price, trading_count, guarantee_money = None):
        if (trading_count == 0):
            print("*-------------Initial State-------------*")
        else:
            print("*---------------------------------------*")
        print("| >> strategy:", self.name)
        print("| >> money:", current_money)
        print("| >> storage:", current_storage)
        print("| >> guarantee money:", guarantee_money)
        print("| >> trading count:", trading_count)
        print("| Total value:", current_money + current_storage * current_price)
        print("| Profit:", (current_money + current_storage * current_price - self.start_money) / self.start_money)
        print("| Current price:", current_price)
        print("| Time:", datetime.now())
        print()
        return

