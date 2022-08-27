from datetime import datetime
class Strategy:
    def __init__(self, parameters):
        ## Parameters for general strategies
        self.name = parameters["name"]                          # The strategy's name
        self.start_money = parameters["start_money"]            # The initial money for the strategy
        self.start_storage = parameters["start_storage"]        # The initial storage for the strategy
        self.trading_fee_rate = parameters["trading_fee_rate"]  # The trading fee rate while making a trade
        self.unit = parameters["unit"]                          # The unit to "buy" or "sell" in a single trade

    def back_test(self, data, parameters = None, if_plot = True):
        ## It's just a frame for backtest method. Each strategy can have its own backtest method.
        pass
        
    def realtime_test(self, symbol, timeframe, time_len):
        ## It's just a frame for realtime test method. Each strategy can have its own backtest method.
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

