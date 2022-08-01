from Strategy import Strategy


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

    def get_grid_position_buy(self, price):
        if (price < self.grid[0]):
            return -1
        grid_position = 0
        for i in range(self.grid_number + 1):
            if price >= self.grid[i]:
                grid_position = i
            else:
                return grid_position
        return grid_position

    def get_grid_position_sell(self, price):
        if (price < self.grid[0]):
            return 0
        grid_position = 1
        for i in range(self.grid_number + 1):
            if price >= self.grid[i]:
                grid_position = i + 1
            else:
                return grid_position
        return grid_position

    def back_test(self, data, parameters = None):
        grid_position_buy = self.get_grid_position_buy(data["open"][0])
        grid_position_sell = self.get_grid_position_sell(data["open"][0])
        trading_count = 0
        money = self.start_money
        storage = 0
        for i in range(len(data)):
            new_grid_position_buy = self.get_grid_position_buy(data["close"][i])
            new_grid_position_sell = self.get_grid_position_sell(data["close"][i])
            if grid_position_buy < new_grid_position_buy:
                for j in range(grid_position_buy + 1, new_grid_position_buy + 1):
                    if (storage >= self.buy_unit):
                        storage -= self.buy_unit
                        money += self.grid[j] * self.buy_unit * (1 - self.trading_fee_rate)
                        trading_count += 1

            elif grid_position_sell > new_grid_position_sell:
                for j in range(grid_position_sell, new_grid_position_sell, -1):
                    if (money >= self.grid[j] * self.buy_unit):
                        storage += self.buy_unit
                        money -= self.grid[j] * self.buy_unit * (1 + self.trading_fee_rate)
                        trading_count += 1

            grid_position_buy = new_grid_position_buy
            grid_position_sell = new_grid_position_sell

        return (money + storage * data["close"][len(data) - 1] - self.start_money) / self.start_money