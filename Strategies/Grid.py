from .Strategy import Strategy
from matplotlib import pyplot as plt
from binance.client import Client
from datetime import datetime
import numpy as np
import time

class Grid(Strategy):
    def __init__(self, parameters):
        super().__init__(parameters)
        ## Parameters specified for Grids
        ## >> grid_number: The number of grids
        ## >> equal_Diff_or_Ratio: The type of difference between grids. Equal difference or equal ratio.
        ## >> trading_logistic: "long", "short" or "both" mode. 
        ##     "long" mode: The strategy would buy when getting buying signal while it sell when getting selling signal and the position is built.
        ##     "short" mode: The strategy would sell when getting selling signal while it buy when getting buying signal and the position is built.  
        ## >> initial_setup: This setup determines whether to build position with a portion of money.
        ##     initial_setup = {"type": ["long" or "short", side of the position], "portion": [(float) portion of money you wish to use]}
        ## >> lowest_price: The lowerbound of the grids.
        ## >> highest_price: The upperbound of the grids.
        self.grid_number = parameters["grid_number"]                    
        self.equal_Diff_or_Ratio = parameters["equal_Diff_or_Ratio"]
        self.trading_logistic = parameters["trading_logistic"]
        self.initial_setup = parameters["initial_setup"]
        self.lowest_price, self.highest_price = parameters["lowest_price"], parameters["highest_price"]
        ## Setup the grid        
        self.grid = []
        dif = self.highest_price - self.lowest_price
        if (self.equal_Diff_or_Ratio == "DIFF"):
            for i in range(self.grid_number + 1):
                self.grid.append(self.lowest_price + i * dif / self.grid_number)
        elif (self.equal_Diff_or_Ratio == "RATIO"):
            ratio = (self.highest_price / self.lowest_price)**(1/self.grid_number)
            for i in range(self.grid_number + 1):
                self.grid.append(self.lowest_price * ratio**i)

    def get_lower_line(self, price):
        if (price < self.grid[0]):
            return -1
        line_index = 0
        for i in range(self.grid_number + 1):
            if price >= self.grid[i]:
                line_index = i
            else:
                return line_index
        return line_index

    def get_higher_line(self, price):
        if (price < self.grid[0]):
            return 0
        line_index = 1
        for i in range(self.grid_number + 1):
            if price >= self.grid[i]:
                line_index = i + 1
            else:
                return line_index
        return line_index

    def back_test(self, data, if_plot = True):
        # initialize backtest object
        trading_count = 0
        money = self.start_money 
        guarantee_money = money
        storage = self.start_storage 
        
        guarantee_money_lock = []
        buy_record = [[],[]]
        sell_record = [[],[]]

        max_profit = 0
        min_profit = np.inf
        MDD = 0

        buy_index = self.get_lower_line(data["open"][0])
        sell_index = self.get_higher_line(data["open"][0])
        if (self.initial_setup["type"] == "long"):
            storage += money * (self.initial_setup["portion"]) / data["open"][0]
            money -= money * (self.initial_setup["portion"]) * (1 + self.trading_fee_rate)
            guarantee_money_lock.append(self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate))
            guarantee_money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)
        elif (self.initial_setup["type"] == "short"):
            storage -= money * (self.initial_setup["portion"]) / data["open"][0]
            money += money * (self.initial_setup["portion"]) * (1 + self.trading_fee_rate)
            guarantee_money_lock.append(-1 * self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate))
            guarantee_money -= self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)
        for i in range(len(data)):
            current_upper_index = self.get_higher_line(data["close"][i])
            current_lower_index = self.get_lower_line(data["close"][i])
            while current_upper_index <= buy_index:
                # buy
                if (self.trading_logistic == "long" or self.trading_logistic == "both"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] < 0):
                        guarantee_money += -1 * guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()
                    elif (guarantee_money < self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)):
                        break
                    else:
                        guarantee_money_lock.append(self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate))
                        guarantee_money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)

                    storage += self.unit
                    money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)
                    trading_count += 1
                    buy_record[0].append(i)
                    buy_record[1].append(self.grid[buy_index])

                elif (self.trading_logistic == "short"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] < 0):
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()

                        storage += self.unit
                        money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)
                        trading_count += 1
                        buy_record[0].append(i)
                        buy_record[1].append(self.grid[buy_index])

                sell_index = buy_index + 1
                buy_index -= 1
            
            while current_lower_index >= sell_index:
                # sell
                if (self.trading_logistic == "short" or self.trading_logistic == "both"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] > 0):
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()
                    elif (guarantee_money < self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)):
                        break
                    else:
                        guarantee_money_lock.append(-1 * self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate))
                        guarantee_money -= self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)

                    storage -= self.unit
                    money += self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)
                    trading_count += 1
                    sell_record[0].append(i)
                    sell_record[1].append(self.grid[sell_index])

                elif (self.trading_logistic == "long"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] > 0):
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()

                        storage += self.unit
                        money -= self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)
                        trading_count += 1
                        sell_record[0].append(i)
                        sell_record[1].append(self.grid[sell_index])

                buy_index = sell_index - 1
                sell_index += 1
            
            temp_profit = (guarantee_money + storage * data["close"][i])
            if (temp_profit > max_profit):
                max_profit = temp_profit
                min_profit = np.inf
            if (temp_profit < min_profit):
                min_profit = temp_profit
                if ((max_profit - min_profit) / max_profit > MDD):
                    MDD = (max_profit - min_profit) / max_profit


        profit = (money + storage * data["close"][len(data) - 1] - self.start_money) / self.start_money 
        if (if_plot):
            fig, ax = plt.subplots()
            ax.set_yticks(self.grid, minor=False)
            ax.yaxis.grid(True, which = 'major')
            plt.plot(data["close"], color = "lightsteelblue")
            plt.scatter(buy_record[0], buy_record[1], color = "black")
            plt.scatter(sell_record[0], sell_record[1], color = "red")
            plt.show()

        return profit, trading_count, buy_record, sell_record, MDD
    
    def realtime_test(self, symbol, timeframe, time_len, if_plot = True):
        # initialize strategy
        client = Client()
        trading_count = 0
        money = self.start_money
        storage = self.start_storage
        guarantee_money = money
        
        pt = datetime.strptime(timeframe,'%H:%M:%S,%f')
        timeframe_seconds = pt.second + pt.minute*60 + pt.hour*3600
        pt = datetime.strptime(time_len,'%H:%M:%S,%f')
        time_len_seconds = pt.second + pt.minute*60 + pt.hour*3600

        prices = []
        buy_record = [[],[]]
        sell_record = [[],[]]
        ## because we are using the concept of contract, so we need to add the guarantee lock to ensure the backtest method can act correctly just like in realtime trading.
        guarantee_money_lock = []
        index = 0
        # initialize money setup
        price = float(client.get_ticker(symbol=symbol)["lastPrice"])
        prices.append(price)

        buy_index = self.get_lower_line(price = price)
        sell_index = self.get_higher_line(price = price)
        if (self.initial_setup["type"] == "long" and self.initial_setup["portion"] > 0):
            ## lock the guarantee money
            guarantee_money_lock.append(self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate))
            guarantee_money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)

            # recording the trade
            storage += money * (self.initial_setup["portion"]) / price
            money -= money * (self.initial_setup["portion"]) * (1 + self.trading_fee_rate)
            buy_record[0].append(index)
            buy_record[1].append(self.grid[buy_index])
            trading_count += 1
            
        elif (self.initial_setup["type"] == "short" and self.initial_setup["portion"] > 0):
            ## lock the guarantee money
            guarantee_money_lock.append(-1 * self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate))
            guarantee_money -= self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)

            # recording the trade
            storage -= money * (self.initial_setup["portion"]) / price
            money -= money * (self.initial_setup["portion"]) * (1 + self.trading_fee_rate)
            sell_record[0].append(index)
            sell_record[1].append(self.grid[sell_index])
            trading_count += 1
        index += 1
        self.print_state(money, storage, price, trading_count, guarantee_money)
        while time_len_seconds >= timeframe_seconds:
            time.sleep(timeframe_seconds)
            time_len_seconds -= timeframe_seconds
            price = float(client.get_ticker(symbol=symbol)["lastPrice"])
            prices.append(price)

            current_upper_index = self.get_higher_line(price)
            current_lower_index = self.get_lower_line(price)
            while current_upper_index <= buy_index:
                # buy
                if (self.trading_logistic == "long" or self.trading_logistic == "both"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] < 0):
                        ## unlock the guarantee money (balanced)
                        guarantee_money += -1 * guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()
                    elif (guarantee_money < self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)):
                        break
                    else:
                        ## lock the guarantee money
                        guarantee_money_lock.append(self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate))
                        guarantee_money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)

                    # recording the trade
                    storage += self.unit
                    money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)
                    trading_count += 1
                    buy_record[0].append(index)
                    buy_record[1].append(self.grid[buy_index])

                    self.print_state(money, storage, price, trading_count, guarantee_money)

                elif (self.trading_logistic == "short"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] < 0):
                        ## unlock the guarantee money (balanced)
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()

                        # recording the trade
                        storage += self.unit
                        money -= self.grid[buy_index] * self.unit * (1 + self.trading_fee_rate)
                        trading_count += 1
                        buy_record[0].append(index)
                        buy_record[1].append(self.grid[buy_index])

                        self.print_state(money, storage, price, trading_count, guarantee_money)

                sell_index = buy_index + 1
                buy_index -= 1
            
            while current_lower_index >= sell_index:
                # sell
                if (self.trading_logistic == "short" or self.trading_logistic == "both"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] > 0):
                        ## unlock the guarantee money (balanced)
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()
                    elif (guarantee_money < self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)):
                        break
                    else:
                        ## lock the guarantee money
                        guarantee_money_lock.append(-1 * self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate))
                        guarantee_money -= self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)

                    # recording the trade
                    storage += self.unit
                    money -= self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)
                    trading_count += 1
                    sell_record[0].append(index)
                    sell_record[1].append(self.grid[sell_index])

                    self.print_state(money, storage, price, trading_count, guarantee_money)

                elif (self.trading_logistic == "long"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] > 0):
                        ## unlock the guarantee money (balanced)
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()

                        # recording the trade
                        storage += self.unit
                        money -= self.grid[sell_index] * self.unit * (1 + self.trading_fee_rate)
                        trading_count += 1
                        sell_record[0].append(index)
                        sell_record[1].append(self.grid[sell_index])

                        self.print_state(money, storage, price, trading_count, guarantee_money)

                buy_index = sell_index - 1
                sell_index += 1
            index += 1

        if (if_plot):
            fig, ax = plt.subplots()
            ax.set_yticks(self.grid, minor=False)
            ax.yaxis.grid(True, which = 'major')
            plt.plot(prices, color = "lightsteelblue")
            plt.scatter(buy_record[0], buy_record[1], color = "black")
            plt.scatter(sell_record[0], sell_record[1], color = "red")
            plt.show()
        return