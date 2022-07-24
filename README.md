# Grid_Trading

## Package usage
The package Grid.py is a script that define a grid and it's back testing method.
If you want to use it, you have to first import it
```py
import Grid
```
or 
```py
from Grid import Grid
```

Then determines the parameters
```py
parameters = {
    "grid_number" : 50,
    "equal_Diff_or_Ratio" : "DIFF", 
    "lowest_price" : 3000, 
    "highest_price" : 20000,
    "start_money" : 1000,
    "trading_fee_rate" : 0.002,
    "buy_unit" : 0.0001
}
```

Initialize the Grid object.
```py
mygrid = Grid(parameters)
```

After setting all those stuffs, you can call the back testing method under the Grid object.
```py
profit = mygrid.back_test_longOnly(data)
```

## Parameters explanation
* grid_number: The number of grids.
* equal_Diff_or_Ratio: This parameter determine whether the grids are in equal difference or equal ratio.
* lowest_price: The lowest price of the grids.
* highest_price: The highest price of the grids.
* start_money: The money we have before we apply the grid trading strategy.
* trading_fee_rate: The service charge while trading in the trading office.
* buy_unit: The amount we buy/sell in each grid
* data: the dataset required while calling "back_test_longOnly" method. **And please make sure that the dataframe contains at least the open price and close price.**
(example)
![](https://i.imgur.com/0ArDwn9.png)














