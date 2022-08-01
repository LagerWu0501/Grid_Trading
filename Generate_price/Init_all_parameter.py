from binance.client import Client

## Input Binance API_key and Secret_key
API_key = input("Input your API key : ")
Secret_key = input("Input your Secret key : ")


Binance = {"API_key" : API_key,
           "API_secret" : Secret_key}

client = Client(Binance["API_key"], Binance["API_secret"])


## Grid strategy parameter
parameters = {
    "grid_number" : 50, #網格數, 建議值 40 ~ 200格
    "expected_ROI_perGrid" : 0.0087, # 預期每網格的報酬率
    "init_Market_price" : 500, # 依模擬的幣種輸入當時的幣價
    "tx_fee_rate" : 0.002, # 交易手續費
    "simu_days" : 1, # 預計模擬的交易日數 短期 < 10天, 中期 10~20天, 長期 20天以上
    "per_dots_oneDay" : 43200, # 每日生成數據點數
    "monte_carlo_simu_num" : 1000 # 每回合蒙地卡羅要模擬的次數
}


## Binance API parameter
symbol = "BTCUSDT"
coin = "BTC"

# timeFrame([time_scale][time])
# interval = {"minute" : {"1m" : "1m", "3m" : "3m", "5m" : "5m", "15m" : "15m", "30m" : "30m"},
#              "hour" : {"1h" : "1h", "2h" : "2h", "4h" : "4h", "6h" : "6h", "8h" : "8h", "12h" : "12h"},
#              "day" : {"1d" : "1d", "3d" : "3d"},
#              "week" : {"1w" : "1w"},
#              "month" : {"1M"}}
timeFrame = "1h"



startDate = "2019-07-22"
endDate = "2022-07-21"

## Other parameter
trade_count = 0  # 每個資料集的總交易次數，初始值為0
every_random_walk = []  # 放入每一個走勢變動資料的陣列
walk_money = []  # 每個走勢變化對於現金變化的陣列
toSell_list = []  # 策略開啟時的初始值以"上"每一個區間價的陣列
toBuy_list = []  # 策略開啟時的初始值以"下"每一個區間價的陣列
grid_float_net_value = []  # 淨利陣列
Buy_and_Hold_float_net_value = []
