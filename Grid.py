import numpy as np
import pandas as pd

class Strategy():
    def __init__(self, parameters):
        ## Parameters about Grids
        self.grid_number = parameters["grid_number"]
        self.equal_Diff_or_Ratio = parameters["equal_Diff_or_Ratio"]
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
        ## Parameters about trading
        self.start_money = parameters["start_money"]
        self.storage = 0  # The storage is set to be 0 from the beginning
        self.trading_fee_rate = parameters["trading_fee_rate"]
        self.buy_unit = parameters["buy_unit"]

    def get_grid_position(self, price):
        if (price < self.grid[0]):
            return -1
        grid_position = 0
        for i in range(self.grid_number + 1):
            if price >= self.grid[i]:
                grid_position = i
            else:
                return grid_position
        return grid_position

    def back_test_longOnly(self, data):
        grid_position = self.get_grid_position(data["open"][0])
        trading_count = 0
        money = self.start_money
        storage = 0
        for i in range(len(data)):
            new_grid_position = self.get_grid_position(data["close"][i])
            if grid_position < new_grid_position:
                for j in range(grid_position + 1, new_grid_position + 1):
                    if (storage >= self.buy_unit):
                        storage -= self.buy_unit
                        money += self.grid[j] * self.buy_unit * (1 - self.trading_fee_rate)
                        trading_count += 1

            elif grid_position > new_grid_position:
                for j in range(grid_position, new_grid_position, -1):
                    if (money >= self.grid[j] * self.buy_unit):
                        storage += self.buy_unit
                        money -= self.grid[j] * self.buy_unit * (1 + self.trading_fee_rate)
                        trading_count += 1

            grid_position = new_grid_position
        return (money + storage * data["close"][len(data) - 1] - self.start_money) / self.start_money

class Grid(Strategy):
    def __init__(self, parameters):
        super().__init__(parameters)
    def get_grid_position(self, price):
        return super().get_grid_position(price)
    def back_test_longOnly(self, data):
        return super().back_test_longOnly(data)