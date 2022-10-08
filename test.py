# %%
import numpy as np
import pandas as pd
import Strategies 
import Strategy_Analysis_Tool 
from binance.client import Client
from matplotlib import pyplot as plt


# %%
# Get data
symbol = "BTCUSDT"
timeFrame = "1h"
startDate = "2017-01-01"
endDate = "2022-08-28"
client = Client()
bars = client.get_historical_klines(symbol=symbol,interval=timeFrame,start_str=startDate, end_str = endDate)
df = pd.DataFrame(bars[:],columns=["timestamp","open","high","low","close","volume", "close_time", "quote_asset_volume", "number_of_trade", "TBB", "TBQ", "ignore"])
df["date"]=pd.to_datetime(df["timestamp"],unit="ms").astype(str)
df = df.drop(["timestamp", "close_time", "quote_asset_volume", "number_of_trade", "TBB", "TBQ", "ignore"], axis=1)
df["open"] = pd.to_numeric(df["open"])
df["high"] = pd.to_numeric(df["high"])
df["low"] = pd.to_numeric(df["low"])
df["close"] = pd.to_numeric(df["close"])
df["volume"] = pd.to_numeric(df["volume"])
df

# # %%
# # SMA strategy
# sma_parameters = {
#     "name":"SMA",                                     ## str
#     "start_money" : 1000.0,                           ## float    
#     "start_storage" : 0.0,                            ## float
#     "trading_fee_rate" : 0.002,                       ## float
#     "unit" : 0.1,                                     ## float
#     "long_period": 156,                               ## long period of SMA curve
#     "short_period": 21,                               ## short period of SMA curve
#     "trading_logistic":"both",                        ## "long", "short", "both"
#     "trading_unit": "all_in"                          ## "all_in", "same_unit" or "same_money"
# }
# sma = Strategies.SMA(sma_parameters)

# # %%
# sharpe_ratio, expected_return = Strategy_Analysis_Tool.Analysis_tool.Shape_Ratio(sma, df, 0.02, window_size=10000, window_off=1000)
# print("*--------------------------------*")
# print("strategy:", sma.name)
# print("expected return:", expected_return * 100)
# print("sharpe ratio:", sharpe_ratio)
# profit, trading_count, buy_record, sell_record, MDD = sma.back_test(df)
# print("*--------------------------------*")
# print("strategy:", sma.name)
# print("trading count:", trading_count)
# print("profit:", profit * 100)
# print("MDD:", MDD)

# # %%
# # SMA strategy
# sma_parameters = {
#     "name":"SMA",                                     ## str
#     "start_money" : 1000.0,                           ## float    
#     "start_storage" : 0.0,                            ## float
#     "trading_fee_rate" : 0.002,                       ## float
#     "unit" : 0.1,                                     ## float
#     "long_period": 162,                               ## long period of SMA curve
#     "short_period": 22,                               ## short period of SMA curve
#     "trading_logistic":"both",                        ## "long", "short", "both"
#     "trading_unit": "all_in"                          ## "all_in", "same_unit" or "same_money"
# }
# sma = Strategies.SMA(sma_parameters)

# # %%
# sharpe_ratio, expected_return = Strategy_Analysis_Tool.Analysis_tool.Shape_Ratio(sma, df, 0.02, window_size=10000, window_off=1000)
# print("*--------------------------------*")
# print("strategy:", sma.name)
# print("expected return:", expected_return * 100)
# print("sharpe ratio:", sharpe_ratio)
# profit, trading_count, buy_record, sell_record, MDD = sma.back_test(df)
# print("*--------------------------------*")
# print("strategy:", sma.name)
# print("trading count:", trading_count)
# print("profit:", profit * 100)
# print("MDD:", MDD)

# %% [markdown]
# # Brute force and find the best parameters

# %%
# SMA strategy
sma_parameters = {
    "name":"SMA",                                     ## str
    "start_money" : 1000.0,                           ## float    
    "start_storage" : 0.0,                            ## float
    "trading_fee_rate" : 0.002,                       ## float
    "unit" : 0.001,                                   ## float
    "long_period": 100,                               ## long period of SMA curve
    "short_period": 30,                               ## short period of SMA curve
    "trading_logistic":"both",                        ## "long", "short", "both"
    "trading_unit": "all_in"                          ## "all_in", "same_unit" or "same_money"
}
sma = Strategies.SMA(sma_parameters)

# %%
index = 0
sharpe = []
expected = []
for long_period in range(50, 300):
    for short_period in range(5, 40):
        sma_parameters["long_period"] = long_period
        sma_parameters["short_period"] = short_period
        sma = Strategies.SMA(sma_parameters)

        sharpe_ratio, expected_return = Strategy_Analysis_Tool.Analysis_tool.Shape_Ratio(sma, df, 0.02, window_size=10000, window_off=1000)
        # print("*--------------------------------*")
        # print("index:", index)
        # print("strategy:", sma.name)
        # print("long_period:", sma.long_period)
        # print("short_period:", sma.short_period)
        # print("expected return:", expected_return * 100)
        # print("sharpe ratio:", sharpe_ratio)
        sharpe.append(sharpe_ratio)
        expected.append(expected_return)
        index += 1

# %%
print(np.argmax(expected), np.argmax(sharpe))
expected_index = np.argmax(expected)
sharpe_index = np.argmax(sharpe)
print(np.max(expected) * 100)
print(np.max(sharpe))

# %%
exp_l, exp_s = 0, 0
sha_l, sha_s = 0, 0
index = 0
l = 0
for long_period in range(50, 300):
    s = 0
    for short_period in range(5, 40):
        if (index == expected_index):
            exp_l, exp_s = long_period, short_period
            print("exp", exp_l, exp_s)
        if (index == sharpe_index):
            sha_l, sha_s = long_period, short_period
            print("sha", sha_l, sha_s)
        index += 1
        s += 1
    l += 1

# %%
# exp_l, exp_s = 156, 21
# sha_l, sha_s = 162, 22

# %%
# SMA strategy
sma_parameters = {
    "name":"SMA",                                     ## str
    "start_money" : 1000.0,                           ## float    
    "start_storage" : 0.0,                            ## float
    "trading_fee_rate" : 0.002,                       ## float
    "unit" : 0.001,                                   ## float
    "long_period": exp_l,                               ## long period of SMA curve
    "short_period": exp_s,                               ## short period of SMA curve
    "trading_logistic":"both",                        ## "long", "short", "both"
    "trading_unit": "all_in"                          ## "all_in", "same_unit" or "same_money"
}
sma = Strategies.SMA(sma_parameters)

# %%
sharpe_ratio, expected_return = Strategy_Analysis_Tool.Analysis_tool.Shape_Ratio(sma, df, 0.02, window_size=10000, window_off=1000)
print("*--------------------------------*")
print("strategy:", sma.name)
print("long_period:", sma.long_period)
print("short_period:", sma.short_period)
print("expected return:", expected_return * 100)
print("sharpe ratio:", sharpe_ratio)

# %%
# SMA strategy
sma_parameters = {
    "name":"SMA",                                     ## str
    "start_money" : 1000.0,                           ## float    
    "start_storage" : 0.0,                            ## float
    "trading_fee_rate" : 0.002,                       ## float
    "unit" : 0.001,                                   ## float
    "long_period": sha_l,                               ## long period of SMA curve
    "short_period": sha_s,                               ## short period of SMA curve
    "trading_logistic":"both",                        ## "long", "short", "both"
    "trading_unit": "all_in"                          ## "all_in", "same_unit" or "same_money"
}
sma = Strategies.SMA(sma_parameters)

# %%
sharpe_ratio, expected_return = Strategy_Analysis_Tool.Analysis_tool.Shape_Ratio(sma, df, 0.02, window_size=10000, window_off=1000)
print("*--------------------------------*")
print("strategy:", sma.name)
print("long_period:", sma.long_period)
print("short_period:", sma.short_period)
print("expected return:", expected_return * 100)
print("sharpe ratio:", sharpe_ratio)

# %%
Expected_Return = np.array(expected)
Sharpe_Ratio = np.array(sharpe)
R = Expected_Return.reshape([250, 35])
S = Sharpe_Ratio.reshape([250, 35])

# %%
# %matplotlib notebook
from IPython.display import (display, display_html, display_png, display_svg)
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt
 
long_period = list(range(50, 300))
short_period = list(range(5, 40))
X, Y = np.meshgrid(long_period, short_period)

three_dim_R = R
Z = np.transpose(three_dim_R) * 100
print(np.max(Z))

plt.clf()
fig = plt.figure(figsize=(12,10))
ax = fig.add_subplot(projection ='3d')

ax.scatter(exp_l, exp_s, np.max(Z), color = "red")
ax.set_title('long and short period with Expected Return')
ax.plot_surface(X, Y, Z, cmap = plt.cm.cividis)
ax.set_xlabel("long_period")
ax.set_ylabel("short_period")
ax.set_zlabel("Expected Return (%)")


# ax.view_init(elev=2,    # 仰角
#              azim=45    # 方位角
#             )
# plt.plot()
# plt.savefig("test.svg")
plt.show()


# %%
# %matplotlib
long_period = list(range(50, 300))
short_period = list(range(5, 40))
X, Y = np.meshgrid(long_period, short_period)

three_dim_R = S
Z = np.transpose(three_dim_R) 
print(np.max(Z))

fig = plt.figure(figsize=(12,10))
ax = plt.axes(projection ='3d')
ax.scatter(sha_l, sha_s, np.max(Z), color = "black")
ax.set_title('Long and short period with Sharpe Ratio')
surf = ax.plot_surface(X, Y, Z, cmap = plt.cm.cividis)
ax.set_xlabel("long_period")
ax.set_ylabel("short_period")
ax.set_zlabel("Sharpe Ratio")

# ax.view_init(elev=2,    # 仰角
#              azim=45    # 方位角
#             )
plt.show()
# plt.savefig("test.png")

# %%



