import numpy as np
import pandas as pd
import random
import Generate_parameter as gp

class Generate_price():
    ## Monte Carlo method
    def Monte_Carlo(_steps):
        global position, money_pool, token_pool, init_money_fund, init_token_buy, inventory_base, update_inventory
        position = gp.parameter["init_Market_price"]
        for g in range(_steps):
            num = random.randint(0, 9)
            _steps = num if random.randint(0, 1) else num * (-1) # 決定下一步是正或負
            if position < 0:
                position = 0 # 幣價為前一個市價加上新的隨機移步值
            else:
                position += _steps
            gp.every_random_walk.append(position) # 把步數資料放入陣列
        return gp.every_random_walk


