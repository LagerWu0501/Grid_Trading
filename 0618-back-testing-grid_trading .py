from re import I
from tkinter import NO
import matplotlib.pyplot as plt  # 導入畫圖(module)
import random  # 導入隨機(module)
from re import S
from matplotlib import markers
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import openpyxl as xl
'''
當用戶輸入以下四個自訂參數時：
1.開啟策略交易前，當前最新報價：舉例42000
2.網格數量：80
3.每格期望報酬率：0.0036
4.手續費費率：0.001

將會計算出下列衍生參數：
1.每格價差多少元
2.天單邊界：最上面的邊界值
3.地單邊界：最下方的邊界值
4.生成賣單陣列
5.生成買單陣列
6.生成初始資金池總額
7.生成初始庫存總額
'''
# ----------------------------------------------------------------
grid_number = 50  # 總網格數 建議值 40~200格
expected_ROI_perGrid = 0.01  # 預期每網格的報酬率 建議值為0.003以上
expected_perGrid = 500 #預期每個網格等差區間
tx_fee_rate = 0.000  # 交易手續費率 多數交易所為千分之一或千分之二
tx_unit = 0.01  # 每單位網格上成交的單位數 可從0.1 調整到任意正整數
simu_days = 1  # 預定要模擬的交易日數  探討短期效果 <10天，中期10~20天，長期 20天以上
per_dots_oneDay = 43200  # 每日生成的數據點數
monte_carlo_simu_num = 1
#-----------------------------------------------------------------
real_dataset =True #選擇是否使用真實資料
equal_ratio = False #True為等差區間False為等比區間
start_year =2020
start_month =("%02d" %6) #確保前面自動補0的寫法 直接輸入0#會成為8進制
start_day=("%02d" %4)
end_year=2021
end_month=("%02d" %2)
end_day=("%02d" %6)
'''
真實資料、時段、網格建立方式設定區
'''
# ----------------------------------------------------------------
'''
以下為衍生參數
'''
simulation_total_points = per_dots_oneDay * simu_days
# ----------------------------------------------------------------
'''
為交易計算過程的所需變數
'''
count = 1  # 從第一回合開始模擬到 等於 monte_carlo_simu_num 值為止
cash_num = []  # 建立放現金部位的空陣列
grid_ROI_list = []  # 報酬率的空陣列
trade_num = []  # 計算交易次數的空陣列
inventory_box = []  # 庫存部位的空陣列
grid_netincome = []  # 淨利部位的空陣列
martin_roi_list = []
martin_net_income_list = []
buy_hold_netincome=[]
buy_hold_ROI=[]
# --------------------------
trade_count = 0  # 每個資料集的總交易次數，初始值為0

every_random_walk = []  # 放入每一個走勢變動資料的陣列
walk_money = []  # 每個走勢變化對於現金變化的陣列
toSell_list = []  # 策略開啟時的初始值以"上"每一個區間價的陣列
toBuy_list = []  # 策略開啟時的初始值以"下"每一個區間價的陣列
grid_float_net_value = []  # 淨利陣列
Buy_and_Hold_float_net_value = []
steps = simulation_total_points  # 資料集步數設定值

# ----------------------------------------------------------------
def refresh_init_condition():
    '''
    以下為重置計算過程的所需變數
    '''
    global martin_float_net_value_list,martin_buy_record_list,martin_sell_cauculation_list,martin_net_income_list\
    ,martin_buy_cauculation_list,martin_sell_record_list,trade_count\
    , every_random_walk, toSell_list, toBuy_list, grid_net_income, walk_money,grid_in_record_list,grid_out_record_list\
    , martin_roi_list,buy_hold_netincome,buy_hold_ROI
    trade_count = 0  # 每個資料集的總交易次數，初始值為0
    every_random_walk = []  # 放入每一個走勢變動資料的陣列
    walk_money = []  # 每個走勢變化對於現金變化的陣列
    toSell_list = []  # 策略開啟時的所有掛賣toSell的賣單陣列
    toBuy_list = []  # 策略開啟時的所有掛買toBuy的賣單陣列
    grid_net_income = []  # 淨利陣列
    grid_in_record_list=[]
    grid_out_record_list=[]
    martin_float_net_value_list = []
    martin_buy_record_list = []
    martin_sell_record_list = []
    martin_buy_cauculation_list = []
    martin_sell_cauculation_list = []
    
def grid_boundry_setting(name,data_list):
    '''
    以下為建立網格交易的網格設定函數
    '''
    if equal_ratio == True:
        for i in range(1, int(grid_number//2)+1):  # 利用迴圈建立所有區間價
            toSell_list.append(data_list[0] +
                               (grid_interval * i))  # 把上區間價放入賣單陣列
            if data_list[0] - (grid_interval * i) >0:
                toBuy_list.append(data_list[0] - (grid_interval * i))  
                # 下區間價放入買單陣列
            else:
                toBuy_list.append(0)
    else:
        for i in range(1, int(grid_number//2)+1):  # 利用迴圈建立所有區間價
            toSell_list.append(data_list[0] +
                               (expected_perGrid * i))  # 把上區間價放入賣單陣列
            if data_list[0] - (expected_perGrid * i) >0:
                toBuy_list.append(data_list[0] - (expected_perGrid * i))  
                # 下區間價放入買單陣列
            else:
                toBuy_list.append(0)
    print(toBuy_list,"\n",toSell_list)

def generate_market_data(_steps):
    '''
    以下為建立蒙地卡羅模擬資料的函式
    '''
    global position, money_pool, token_pool, init_money_fund, init_token_buy, inventory_base, update_inventory
    position = init_Market_price
    for g in range(_steps):  # 建立走勢圖的迴圈
        num = random.randint(0, 9)  # 決定下一步走1~9的隨機數
        _steps = num if random.randint(0, 1) else num*-1  # 決定下一步是正還是負
        if position < 0 :
            position = 0  # 幣價為前一個市價加上新的隨機移步值              #負值bug
        else:
            position += _steps
        every_random_walk.append(position)  # 把步數資料放入陣列
    return every_random_walk

def real_data_import_close(name,dataset):
    '''
    以下為導入真實資料集"收盤價"的函式
    '''
    real_data = pd.read_csv(dataset)
    data_close_price =[]
    for s in real_data["Close"]:
        data_close_price.append(s)
    return data_close_price
#------------------------------------------------------------------

def buy_and_hold(name,data_list):
    '''
    Buy and Hold 策略函式
    '''
    global buy_hold_money_pool,buy_hold_token_pool,buy_hold_ROI,buy_hold_netincome,buy_and_hold_float_net_value
    init_Market_price = data_list[0]
    buy_hold_money_pool = total_invest_fund%init_Market_price
    buy_hold_token_pool=total_invest_fund/init_Market_price
      # 依模擬的幣種，輸入當時的幣價
    buy_and_hold_float_net_value = []
    for i in range(len(data_list)):
        buy_and_hold_float_net_value.append(buy_hold_money_pool+(buy_hold_token_pool*data_list[i]))  
    buy_hold_money_pool =  buy_hold_token_pool *data_list[-1]
    
    net = buy_hold_money_pool-total_cost
    buy_hold_netincome.append(net)
    buy_hold_ROI.append('%.2f'%(net/total_cost*100)+"%")        #計算報酬率及各項指標
    print(f"第{count}次Buy and hold策略，共{len(data_list)}步,起始位置{init_Market_price}，結束位置為:{data_list[-1]}，報酬率:{buy_hold_ROI[count-1]}")
    Buy_and_Hold_float_net_value.append(buy_hold_money_pool-init_cash_fund)

def grid_trading(name,data_list,record_marker_spacing=0):
    '''
    網格交易策略函式
    '''
    global money_pool, token_pool, grid_net_income, trade_count, lower_bound, upper_bound, toBuy_list, toSell_list, walk_money
    init_Market_price = data_list[0]
    for x in data_list:
        if x > lower_bound or x < upper_bound:
            if (x > toSell_list[0] and len(toSell_list) > 1 and token_pool >= tx_unit) or (x < toBuy_list[0] and len(toBuy_list) > 1 and money_pool >= (tx_unit * toBuy_list[0])):
                while (x > toSell_list[0] and len(toSell_list) > 1 and token_pool >= tx_unit) or (x < toBuy_list[0] and len(toBuy_list) > 1 and money_pool >= (tx_unit * toBuy_list[0])):
                    if x > toSell_list[0] and len(toSell_list) > 1:
                        toBuy_list.insert(0, toSell_list[0])  # 把越過的區間價加入"下"區間
                        grid_out_record_list.append(toSell_list[0]+toSell_list[0]*record_marker_spacing)
                        grid_in_record_list.append(None)
                        money_pool = money_pool + \
                            (tx_unit * toSell_list[0]*(1-tx_fee_rate)) # 現金以當時的價格"增加"
                        toSell_list.remove(toSell_list[0])  # 移除上區間裡價格越過的區間價
                        token_pool -= tx_unit  # 庫存-1 (賣出)                   

                # 價格超過下區間的第一個區間價，且陣列裡面還有數值的話
                    elif x < toBuy_list[0] and len(toBuy_list) > 1:
                        toSell_list.insert(0, toBuy_list[0])  # 把越過的區間價加入"上"區間
                        grid_in_record_list.append(toBuy_list[0]-toBuy_list[0]*record_marker_spacing)
                        grid_out_record_list.append(None)
                        money_pool = money_pool - \
                            (tx_unit * toBuy_list[0])  # 現金以當時的價格"減少"
                        toBuy_list.remove(toBuy_list[0])  # 移除下區間裡價格越過的區間價
                        token_pool += (tx_unit*(1-tx_fee_rate))  # 庫存+1 (買進)

                    else :
                        grid_in_record_list.append(None)
                        grid_out_record_list.append(None)

                    walk_money.append(money_pool)  # 更新現金狀況放入現金陣列裡
                    trade_count += 1  # 交易次數+1
            else :
                grid_in_record_list.append(None)
                grid_out_record_list.append(None)
            grid_float_net_value.append(money_pool + ((token_pool - init_token_buy) * x))
        else :
            grid_in_record_list.append(None)
            grid_out_record_list.append(None)
    
    inventory_box.append(token_pool)    # 該資料集剩餘庫存
    cash_num.append('%.2f'%money_pool)  # 該資料集剩餘現金
    trade_num.append(trade_count)   # 該資料集交易次數
    final_value = money_pool + token_pool * \
        data_list[-1]       # ㄧ回合結束的最終投資餘額
    print(f"第{count}次網格策略實驗，共{len(data_list)}步,網格策略停止後的剩餘現金: {money_pool:,.2f}元,加密貨幣存貨:{token_pool:,.3f},最終幣價為：{data_list[-1]:,.2f},投資終值：{final_value:,.2f}")
    net_profit = (final_value-(init_cash_fund +(init_token_buy * init_Market_price)))
    grid_netincome.append('%.2f'%net_profit)
    roi = (net_profit/(init_cash_fund +
           (init_token_buy * init_Market_price)))*100  # 計算淨利報酬率
    grid_ROI_list.append(f"{'%.2f'%roi}%")      # 把淨利以小數點後2位數顯示放進陣列

def martingale_trading(name,data_list,buy_spacing,take_profit_spacing):
    '''馬丁格爾策略函式'''
    total_cost = init_cash_fund+init_token_buy*data_list[0]
    init_Market_price = data_list[0]
    temporart_buy_list =[]
    last_buying_position = init_Market_price
    martin_money_pool = init_cash_fund
    martin_token_pool = init_token_buy
    buying_aver_price = init_Market_price 
    times = 1
    while martin_token_pool -tx_unit>tx_unit:      #建立起始倉位，庫存剩下一單位
            martin_money_pool +=(tx_unit * data_list[0])
            martin_token_pool -= (tx_unit*(1-tx_fee_rate))
    for i in data_list:
        condition1 = martin_token_pool < tx_unit
        condition2 = i < last_buying_position*(1-buy_spacing)
        condition3 = i > buying_aver_price * (1+take_profit_spacing)
        money_pool_enough = martin_money_pool-(tx_unit *times* last_buying_position*(1-buy_spacing))>0
        money_pool_enough2 = martin_money_pool-tx_unit *i>0

        if condition1 == True or condition2 == True or condition3 == True :
            if condition1 == True and money_pool_enough2 == True:#沒有就買
                last_buying_position = i 
                buying_aver_price=i
                martin_money_pool -=(tx_unit * last_buying_position)
                martin_token_pool += (tx_unit*(1-tx_fee_rate))
                martin_buy_record_list.append(last_buying_position)
                martin_buy_cauculation_list.append(last_buying_position)
                martin_sell_record_list.append(None)
                temporart_buy_list .append(i)
                # print(f"沒有就買:{last_buying_position}")

            elif condition2 == True and money_pool_enough == True:#低於設定點位&錢夠 就買進
                times *= 2
                martin_money_pool -=(tx_unit *times* (last_buying_position*(1-buy_spacing)))
                martin_token_pool += (tx_unit*times*(1-tx_fee_rate))
                last_buying_position = last_buying_position*(1-buy_spacing)
                martin_buy_record_list.append(last_buying_position)
                martin_buy_cauculation_list.append(last_buying_position)
                martin_sell_record_list.append(None)
                for time in range(times):
                    temporart_buy_list .append(i)
                buying_aver_price = sum(temporart_buy_list)/len(temporart_buy_list)
                # print(f"低於設定點位&錢夠 就買:{last_buying_position}，均價:{buying_aver_price}\
                #     倍數:{times}\n{temporart_buy_list}")
                
                
            elif condition3 == True :
                while martin_token_pool  > tx_unit:#達到要求報酬率就全麥吐司
                    martin_money_pool += (tx_unit * (buying_aver_price * (1+take_profit_spacing)))
                    martin_token_pool -= (tx_unit*(1-tx_fee_rate))
                    times = 1
                martin_sell_record_list.append(buying_aver_price * (1+take_profit_spacing))
                martin_sell_cauculation_list.append(buying_aver_price * (1+take_profit_spacing))
                martin_buy_record_list.append(None)
                temporart_buy_list =[]
                # print(f"達到要求報酬率就全麥吐司:{last_buying_position}") 
        else:
            martin_buy_record_list.append(None)
            martin_sell_record_list.append(None)
        martin_float_net_value_list.append(martin_money_pool+(martin_token_pool*i))
        try :
            buying_aver_price = sum(martin_buy_cauculation_list)/len(martin_buy_cauculation_list)
        except ZeroDivisionError:
            continue        
    net = (martin_money_pool+martin_token_pool*i)-total_cost
    martin_net_income_list.append(net)
    martin_roi_list.append('%.2f'%(net/total_cost*100)+"%")
    print(f"第{count}次馬丁格爾實驗，共{len(data_list)}步,剩餘現金: {martin_money_pool:,.2f}元,\
    加密貨幣存貨:{martin_token_pool:,.3f},最終幣價為：{data_list[-1]:,.2f},投資終值：{net:,.2f}")

#------------------------------------------------------------------

def win_lose_ratio (name,x):
    '''
    計算策略輸贏比率函式，大於1為贏較多，小於1為輸較多
    '''
    global grid_netincome ,win_ratio,win_rate,buy_hold_ROI
    win_count=0
    lose_count=0
    x = list(map(float,x))#導入陣列、資料處理
    
    for i in range(len(x)): #判斷輸贏
        if x[i]<0:
            lose_count +=1
        else :
            win_count+=1
    try:
        win_ratio = win_count/lose_count        #計算輸贏比率
    except ZeroDivisionError:
        win_ratio = 1
    try:
        win_rate = (win_count/len(x))*100
    except ZeroDivisionError:
        win_rate = 0
    print(f"{name}輸贏比率 : {'%.2f'%win_ratio}(0為全輸 1為輸贏一比一)，{name}勝率:{'%.2f'%win_rate}%")

def highest_and_lowest_ROI(name,x):
    '''
    計算資料集內，最大與最低報酬率函式
    '''
    x = list(map(lambda x: x.replace("%", ""), x))
    x = list(map(float,x))
    highest_ROI=0
    lowest_ROI=100000 
    for i in range(len(x)):
        if x[i] > highest_ROI :
            highest_ROI = x[i]
        if x[i] < lowest_ROI:
            lowest_ROI = x[i]
    print(f"{name}本回合共{monte_carlo_simu_num}筆資料，最高報酬率為:{highest_ROI}%，最低報酬率為:{lowest_ROI}%")

def net_value_list_cauculate(name,strtegy_money_pool,strtegy_token_pool):
    '''
    連續淨值計算函式
    '''
    net_value = []
    for i in range(len(every_random_walk)):
        net_value.append(strtegy_money_pool+(strtegy_token_pool*every_random_walk[i]))
    return net_value

def strategy_in_out_record(name,data_list,in_record,out_record):
    '''
    進出紀錄以圖片方式顯示
    '''
    #in進紀錄 out出紀錄  run_chart走勢圖
    fig = plt.figure()  # 建立圖片
    x=[]
    for i in  range(len(in_record)):
        x.append(i)

    photo_name = fig.add_subplot(111)
    photo_name.plot(data_list)  # 把步數丟進圖片裡
    photo_name.set_title(f"{name} strategy trade record ")  # 設定圖表名稱

    photo_name.set_xlim(left=0, right=steps)
    photo_name.set_ylim(bottom=min(data_list), top=max(data_list))

    photo_name.scatter(x,in_record,marker = "^",s = 28,color = "r")
    photo_name.scatter(x,out_record,marker = "v",s = 28,color = "g")

    plt.show()

#------------------------------------------------------------------
def dataset_time_select_close(name,data_list,start_year,start_month,start_day,end_year,end_month,end_day):
    '''
    選取真實資料範圍，並回傳該範圍收盤價
    '''
    real_data = pd.read_csv(data_list) #close
    data_close_price =[]
    data_time_list =[]
    for s in real_data["Close"]:
        data_close_price.append(s)
    for t in real_data["Timestamp"]:
        data_time_list.append(t)
    start_date = data_time_list.index(f"{start_year}-{start_month}-{start_day} 00:00:00")
    end_date = data_time_list.index(f"{end_year}-{end_month}-{end_day} 00:00:00")
    real_data = data_close_price[start_date:end_date]
    return real_data
#------------------------------------------------------------------
def compare_netincome_chart(name,net_income_1,name2,net_income_2):
    '''
    以圖表方式比較兩份策略淨值資料
    '''
    fig = plt.figure()  # 建立圖片
    steps_chart = fig.add_subplot(511)
    steps_chart.plot(every_random_walk)  # 把步數丟進圖片裡
    steps_chart.set_title("Cryptocurrency price trend generating by random walk ")  # 設定圖表名稱
    
    steps_chart.set_xlim(left=0, right=steps)
    steps_chart.set_ylim(bottom=min(every_random_walk), top=max(every_random_walk))
    
    netincome_1 = fig.add_subplot(513)
    netincome_1.plot(net_income_1)  # 把現金走勢丟進圖片裡
    netincome_1.set_title(f"{name}  net_value Run Chart")  # 設定圖表名稱
    
    netincome_1.set_xlim(left=0, right=steps)
    netincome_1.set_ylim(bottom=min(net_income_1), top=max(net_income_1))

    netincome_2 = fig.add_subplot(515)
    netincome_2.plot(net_income_2)  # 把淨利走勢丟進圖片裡
    netincome_2.set_title(f"{name2}  net_value Run Chart")

    netincome_2.set_xlim(left=0, right=steps)
    netincome_2.set_ylim(bottom=min(net_income_2), top=max(net_income_2))

#------------------------------------------------------------------
if real_dataset ==True:
    real_data = dataset_time_select_close(\
    "btc",\
    "BITUSD_1m_dataset.csv",\
    start_year,start_month,start_day,\
    end_year,end_month,end_day)
    steps = len(real_data)#取得真實資料長度

    init_Market_price = real_data[0]  # 依模擬的幣種，輸入當時的幣價
elif real_dataset ==False:
    init_Market_price = 42000
    real_data = generate_market_data(steps)  #模擬資料
#-----------------------------------------------------------------------
grid_interval = init_Market_price * expected_ROI_perGrid  # 網格間距
upper_bound = init_Market_price + \
((grid_number / 2) * grid_interval)  # 天單邊界：最上面的邊界值
lower_bound = init_Market_price - \
((grid_number / 2) * grid_interval)  # 地單邊界：最下方的邊界值
position = init_Market_price  # 資料集起始位置
#------------------------------------------------------------------------
while count <= monte_carlo_simu_num:  
    # 蒙地卡羅模擬實驗開始的迴圈
    refresh_init_condition()            
    grid_boundry_setting("BTC",real_data)  
    # 初始資金池與初始買進持有的加密貨幣總數
    init_token_buy = len(toSell_list) * tx_unit
    init_cash_fund = sum(toBuy_list) * tx_unit * (1 + tx_fee_rate)
    total_invest_fund = (init_token_buy * init_Market_price) + init_cash_fund
    money_pool = init_cash_fund
    token_pool = init_token_buy
    total_cost = init_cash_fund+init_token_buy*init_Market_price
    #-------------------------------------------------------------
    # 進入交易搓合模擬
    grid_trading("BTC",real_data,0.008)
    martingale_trading("BTC",real_data,0.1,0.15)
    buy_and_hold("bitcoin",real_data)
    
    count += 1   # 策略交易回合數+1，進入下一回合開始

#strategy_in_out_record("grid",real_data,grid_in_record_list,grid_out_record_list)
highest_and_lowest_ROI("網格策略",grid_ROI_list)
win_lose_ratio("網格策略",grid_netincome)
#highest_and_lowest_ROI("Buy&Hold策略",buy_hold_ROI)
#win_lose_ratio("Buy&Hold策略",buy_hold_netincome)
#highest_and_lowest_ROI("Martin-gale-strategy",martin_roi_list)
#win_lose_ratio("Martin-gale-strategy",martin_net_income_list)
#compare_netincome_chart("martin ",martin_float_net_value_list,\
#      "buy_and_hold ",buy_and_hold_float_net_value)

#plt.show()  # 顯示圖片
