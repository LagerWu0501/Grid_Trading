from .Strategy import Strategy
from matplotlib import pyplot as plt

class Grid(Strategy):
    def __init__(self, parameters):
        super().__init__(parameters)
        ## Parameters about Grids
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

        buy_index = self.get_lower_line(data["open"][0])
        sell_index = self.get_higher_line(data["open"][0])
        if (self.initial_setup["type"] == "long"):
            storage += money * (self.initial_setup["poriton"]) / data["open"][0]
            money -= money * (self.initial_setup["poriton"]) * (1 + self.trading_fee_rate)
        elif (self.initial_setup["type"] == "short"):
            storage -= money * (self.initial_setup["poriton"]) / data["open"][0]
            money -= money * (self.initial_setup["poriton"]) * (1 + self.trading_fee_rate)
        guarantee_money_lock = []
        buy_record = [[],[]]
        sell_record = [[],[]]
        for i in range(len(data)):
            current_upper_index = self.get_higher_line(data["close"][i])
            current_lower_index = self.get_lower_line(data["close"][i])
            while current_upper_index <= buy_index:
                # buy
                if (self.trading_logistic == "long" or self.trading_logistic == "both"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] < 0):
                        guarantee_money += -1 * guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()
                    elif (guarantee_money < self.grid[buy_index] * self.buy_unit * (1 + self.trading_fee_rate)):
                        break
                    else:
                        guarantee_money_lock.append(self.grid[buy_index] * self.buy_unit * (1 + self.trading_fee_rate))
                        guarantee_money -= self.grid[buy_index] * self.buy_unit * (1 + self.trading_fee_rate)

                    storage += self.buy_unit
                    money -= self.grid[buy_index] * self.buy_unit * (1 + self.trading_fee_rate)
                    trading_count += 1
                    buy_record[0].append(i)
                    buy_record[1].append(self.grid[buy_index])

                elif (self.trading_logistic == "short"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] < 0):
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()

                        storage += self.buy_unit
                        money -= self.grid[buy_index] * self.buy_unit * (1 + self.trading_fee_rate)
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
                    elif (guarantee_money < self.grid[sell_index] * self.buy_unit * (1 + self.trading_fee_rate)):
                        break
                    else:
                        guarantee_money_lock.append(-1 * self.grid[sell_index] * self.buy_unit * (1 + self.trading_fee_rate))
                        guarantee_money -= self.grid[sell_index] * self.buy_unit * (1 + self.trading_fee_rate)

                    storage += self.buy_unit
                    money -= self.grid[sell_index] * self.buy_unit * (1 + self.trading_fee_rate)
                    trading_count += 1
                    sell_record[0].append(i)
                    sell_record[1].append(self.grid[sell_index])

                elif (self.trading_logistic == "long"):
                    if (len(guarantee_money_lock) > 0 and guarantee_money_lock[len(guarantee_money_lock) - 1] > 0):
                        guarantee_money += guarantee_money_lock[len(guarantee_money_lock) - 1]
                        guarantee_money_lock.pop()

                        storage += self.buy_unit
                        money -= self.grid[sell_index] * self.buy_unit * (1 + self.trading_fee_rate)
                        trading_count += 1
                        sell_record[0].append(i)
                        sell_record[1].append(self.grid[sell_index])

                buy_index = sell_index - 1
                sell_index += 1
        profit = (money + storage * data["close"][len(data) - 1] - self.start_money) / self.start_money 
        if (if_plot):
            fig, ax = plt.subplots()
            ax.set_yticks(self.grid, minor=False)
            ax.yaxis.grid(True, which = 'major')
            plt.plot(data["close"], color = "lightsteelblue")
            plt.scatter(buy_record[0], buy_record[1], color = "black")
            plt.scatter(sell_record[0], sell_record[1], color = "red")
            plt.show()

        return profit, trading_count, buy_record, sell_record