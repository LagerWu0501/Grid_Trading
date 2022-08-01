from binance.client import Client

## Input Binance API_key and Secret_key
API_key = input("Input your API key : ")
Secret_key = input("Input your Secret key : ")


Binance = {"API_key" : API_key,
           "API_secret" : Secret_key}

client = Client(Binance["API_key"], Binance["API_secret"])


## Grid strategy parameter

parameters = {
    "name":"grid",                                    ## str
    "start_money" : 1000.0,                           ## float    
    "start_storage" : 0.0,                            ## float
    "trading_fee_rate" : 0.002,                       ## float
    "buy_unit" : 0.0001,                              ## float
    "grid_number" : 50,                               ## int  
    "equal_Diff_or_Ratio" : "DIFF",                   ## "DIFF", "RATIO"
    "trading_logistic":"long",                        ## "long", "short", "both"
    "initial_setup":{"type":"long", "protion":0.5},   ## "type": "long", "short" | "None". "portion" : float
    "lowest_price" : 3000.0,                          ## float
    "highest_price" : 20000.0                         ## float
}


## Binance API parameter
symbol = "BTCUSDT"
coin = "BTC"




## Other parameter
trade_count = 0  # 每個資料集的總交易次數，初始值為0
every_random_walk = []  # 放入每一個走勢變動資料的陣列
walk_money = []  # 每個走勢變化對於現金變化的陣列
toSell_list = []  # 策略開啟時的初始值以"上"每一個區間價的陣列
toBuy_list = []  # 策略開啟時的初始值以"下"每一個區間價的陣列
grid_float_net_value = []  # 淨利陣列
Buy_and_Hold_float_net_value = []
