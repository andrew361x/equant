# 1.基于期限结构判断正向市场结构，反向市场结构，其他市场结构
# 2.正向市场，只做空；反向市场，只做多
# 3.交易近月合约
# 4.8月最后一天，平掉9月合约，移仓1月合约；12月最后一天，平掉1月合约，移仓5月合约；4月最后一天，平掉5月合约，移仓9月合约

import talib
import numpy as np
import pandas as pd
from EsSeries import NumericSeries
import os, os.path
import json
import datetime
from pandas.tseries.offsets import BDay  #工作日

#g_params['shortLength'] = 3            #短周期
#g_params['longLength'] = 10            #长周期

p1=39
p2=147
contractSymbol = "RB"
contractExchange = "SHFE"

symbolindex = contractExchange + "|Z|" + contractSymbol + "|INDEX"# 基准合约
symbol01 = contractExchange + "|F|" + contractSymbol +"|2101"
symbol05 = contractExchange + "|F|" + contractSymbol +"|2005"
symbol09 = contractExchange + "|F|" + contractSymbol +"|2010"

spotFileName = os.path.abspath( os.path.join(os.getcwd(), "..",'files',contractSymbol,  contractSymbol + "_spotprice.csv") )
contractCfgPath = os.path.abspath( os.path.join(os.getcwd(), "..",'files',"contractConfig.json") )

barInteval = 30
barType = 'M'

spotdata = None
spotSeries = NumericSeries(name="spotSeries")

# symbolset = set([symbol01, symbol05, symbol09])

m01CloseSeries = NumericSeries(name="m01CloseSeries")
m05CloseSeries = NumericSeries(name="m05CloseSeries")
m09CloseSeries = NumericSeries(name="m09CloseSeries")

#m01VolSeries = NumericSeries(name="m01VolSeries")
#m05VolSeries = NumericSeries(name="m05VolSeries")
#m09VolSeries = NumericSeries(name="m09VolSeries")

m01HoldingSeries = NumericSeries(name="m01HoldingSeries")
m05HoldingSeries = NumericSeries(name="m05HoldingSeries")
m09HoldingSeries = NumericSeries(name="m09HoldingSeries")

orderTimeSeries = NumericSeries(name="orderTimeSeries")  # 当前实际交易时间序列
orderIndexSeries = NumericSeries(name="orderIndexSeries")  # 交易索引序列

tradeContractSeries = NumericSeries(name="tradeContractSeries")  # 当前交易的合约名称序列
termStructureSeries = NumericSeries(name="termStructureSeries")  # 当前期限结构序列

# datetimeSeries = NumericSeries(name="datetimeSeries")  # 当前bar时间序列
tradeDateSeries = NumericSeries(name="tradeDateSeries")  # 当前日期序列

# maxVolContractSeries = NumericSeries(name="maxVolContractSeries")   # 最大成交量的合约序列

def initialize(context):
     # 必须订阅品种 周期，然后Close无法获取数据 ，但是handledata会每次都回调  因为对获取到的数据进行了替换，所以这里获取一根数据速度就会快点
    SetBarInterval(symbolindex, barType, barInteval, 1)
    SetBarInterval(symbol01, barType, barInteval, 1)
    SetBarInterval(symbol05, barType, barInteval, 1)
    SetBarInterval(symbol09, barType, barInteval, 1)
    SetOrderWay(2)
    
    margin = 0.1    # 保证金 统一按照10%
    tradefree = 0.0  # 手续费,不收费

    try:
        with open(contractCfgPath, encoding='utf-8') as f:
            cfg = json.load(f)
            margin = float(cfg[contractSymbol]['margin'])
            tradefree = float(cfg[contractSymbol]['commission'])
            LogInfo(f"获取{contractSymbol}的保证金:{margin} 和佣金{tradefree}")
    except Exception as e:
        LogInfo(f"获取{contractSymbol}的保证金和佣金的数据 失败,因为 {e}")
        margin = 0.1    # 保证金 统一按照10%
        tradefree = 0.0  # 手续费,不收费

    # 保证金 统一按照10%
    SetMargin(0, margin, symbolindex)
    SetMargin(0, margin, symbol01)
    SetMargin(0, margin, symbol05)
    SetMargin(0, margin, symbol09)
    
    # 手续费,统一按照 万分之1.1
    SetTradeFee('A', 1, tradefree, contractNo=symbolindex)
    SetTradeFee('A', 1, tradefree, contractNo=symbol01)
    SetTradeFee('A', 1, tradefree, contractNo=symbol05)
    SetTradeFee('A', 1, tradefree, contractNo=symbol09)
    
    #设置滑点
    #SetSlippage(1)  

    # 使用全局变量
    global spotdata,spotFileName
    try:
        spotdata = pd.read_csv(spotFileName, index_col=0,header=0, parse_dates=True)
        spotdata.columns = ['spotprice']  # ['现货价格']
        spotdata.index.name = 'datetime'
        spotdata.sort_index(inplace=True)
    except:
        spotdata = pd.DataFrame()  # 不存在就是空的
    LogInfo(spotFileName)
    LogInfo(spotdata.shape)

def handle_data(context):
    # cb = CurrentBar()
    # tim = context.dateTimeStamp()
    # LogInfo('quote time: %s.%s %s' % (tim[:8], tim[8:12], context.contractNo()))
    global spotdata, spotSeries, orderTimeSeries, tradeContractSeries, termStructureSeries
    # global datetimeSeries
    global tradeDateSeries
    global m01CloseSeries, m05CloseSeries, m09CloseSeries
    # global m01VolSeries, m05VolSeries, m09VolSeries, maxVolContractSeries
    global m01HoldingSeries, m05HoldingSeries, m09HoldingSeries

    currentContract = context.contractNo()
    if(currentContract != symbolindex):
        return
    
    # 只有index合约才会进入
    # tim = context.dateTimeStamp()
    # LogInfo('quote time: %s.%s' % (tim[:8], tim[8:12]))

    spotSeries[-1] = spotSeries[-1]
    m01CloseSeries[-1] = m01CloseSeries[-1]
    m05CloseSeries[-1] = m05CloseSeries[-1]
    m09CloseSeries[-1] = m09CloseSeries[-1]
    m01HoldingSeries[-1] = m01HoldingSeries[-1]
    m05HoldingSeries[-1] = m05HoldingSeries[-1]
    m09HoldingSeries[-1] = m09HoldingSeries[-1]

    orderTimeSeries[-1] = np.nan
    tradeContractSeries[-1] = tradeContractSeries[-1]
    termStructureSeries[-1] = termStructureSeries[-1]

    tradeDateSeries[-1] = datetime.datetime.strptime(context.tradeDate(),'%Y%m%d')
    dateTimeStamp = datetime.datetime.strptime(context.dateTimeStamp(),'%Y%m%d%H%M%S%f')

    #m01VolSeries[-1] = np.nan
    #m05VolSeries[-1] = np.nan
    #m09VolSeries[-1] = np.nan
    #maxVolContractSeries[-1] = maxVolContractSeries[-1]

    if (np.isnan(orderIndexSeries[-1])):
        orderIndexSeries[-1] = 0
    else:
        orderIndexSeries[-1] = orderIndexSeries[-1]

        # LogInfo(spotdata.loc[context.tradeDate()].values[0])

    data1 = Close(symbol01, barType, barInteval)
    data5 = Close(symbol05, barType, barInteval)
    data9 = Close(symbol09, barType, barInteval)

    # LogInfo(BarCount(symbol01,barType,barInteval) )
    # LogInfo(BarCount(symbol05,barType,barInteval) )
    # LogInfo(BarCount(symbol09,barType,barInteval) )
    #LogInfo("datetimestamp %s >>> len(data1) %d, len(data5) %d, len(data9) %d " %(datetimeSeries[-1], len(data1), len(data5), len(data9)) )
    # if len(data1) == len(data5) and len(data5) == len(data9):
    if len(data1) == 0 or len(data5) == 0 or len(data9) == 0:
        return
    else:
        m01CloseSeries[-1] = data1[-1]
        m05CloseSeries[-1] = data5[-1]
        m09CloseSeries[-1] = data9[-1]

        # 日线级别判断成交量
        if len(tradeDateSeries) < 2 or ((len(tradeDateSeries) >= 2) and tradeDateSeries[-1] != tradeDateSeries[-2]):

            if tradeDateSeries[-1] in spotdata.index:
                spotSeries[-1] = spotdata.loc[tradeDateSeries[-1]].iloc[0]

            #tmp1 = HisData(Enum_Data_Vol(), Enum_Period_Day(),1, symbol01, 100)
            # tmp2 = HisBarsInfo(symbol01,'D',1)# , 100)

            # 在新一天的第一个30分钟调用Vol
            #vol1 = TotalQty(symbol01, barType, barInteval)
            #if len(vol1) < 2:
                #m01VolSeries[-1] = np.nan
            #else:
                #m01VolSeries[-1] = vol1[-2]

            #vol5 = TotalQty(symbol05, barType, barInteval)
            #if len(vol5) < 2:
                #m05VolSeries[-1] = np.nan
            #else:
                #m05VolSeries[-1] = vol5[-2]
            #vol9 = TotalQty(symbol09, barType, barInteval)
            #if len(vol9) < 2:
                #m09VolSeries[-1] = np.nan
            #else:
                #m09VolSeries[-1] = vol9[-2]

            ## 比较昨天的累计成交量的大小
            #if m01VolSeries[-1] > m05VolSeries[-1] and m01VolSeries[-1] > m09VolSeries[-1]:
                #maxVolContractSeries[-1] = symbol01
            #elif m05VolSeries[-1] > m01VolSeries[-1] and m05VolSeries[-1] > m09VolSeries[-1]:
                #maxVolContractSeries[-1] = symbol05
            #elif m09VolSeries[-1] > m01VolSeries[-1] and m09VolSeries[-1] > m05VolSeries[-1]:
                #maxVolContractSeries[-1] = symbol09
            #else:
                #maxVolContractSeries[-1] = maxVolContractSeries[-1]

    # LogInfo("m01:%d m05:%d m09:%d"%(BarCount(symbol01,barType,barInteval),BarCount(symbol05,barType,barInteval),BarCount(symbol09,barType,barInteval) ) )

    # LogInfo(context.dateTimeStamp()) #20161202000000000
    # LogInfo(context.tradeDate())     #20161202
    # LogInfo(str(context.tradeDate()))     #20161202
    # LogInfo(spotdata.loc[context.tradeDate()])     #20161202

    if len(Close(symbolindex, barType, barInteval)) < p2:
        return

    # LogInfo(spot[context.tradeDate])
    # 使用talib计算均价
    ma1 = talib.EMA(Close(), p1)
    ma2 = talib.EMA(Close(), p2)
    # LogInfo(ma1)

    # 绘制指标图形
    PlotNumeric("ma1", ma1[-1], RGB_Red())
    PlotNumeric("ma2", ma2[-1], RGB_Green())
    #PlotNumeric("fit", NetProfit() + FloatProfit() - TradeCost(), RGB_Red(), False)
    # LogInfo(type(ma1))

    PlotNumeric("spotSeries", spotSeries[-1], RGB_Purple(), False)
    PlotNumeric("m01CloseSeries", m01CloseSeries[-1], RGB_Red(), False)
    PlotNumeric("m05CloseSeries", m05CloseSeries[-1], RGB_Green(), False)
    PlotNumeric("m09CloseSeries", m09CloseSeries[-1], RGB_Gray(), False)

    # termStructureSeries[-1] =0 # 默认期限结构为other
    month = tradeDateSeries[-1].month
    # LogInfo("datetime:%s month:%d  spotSeries: %f, m01CloseSeries: %f, m05CloseSeries: %f, m09CloseSeries: %f"%(datetimeSeries[-1],month,spotSeries[-1], m01CloseSeries[-1], m05CloseSeries[-1], m09CloseSeries[-1]) )

    # LogInfo("m01CloseSeries\n")
    # LogInfo(m01CloseSeries.getdata() )
    # LogInfo("m05CloseSeries\n")
    # LogInfo(m05CloseSeries.getdata() )
    # LogInfo("m09CloseSeries\n")
    # LogInfo(m09CloseSeries.getdata() )

    #LogInfo("contract:%s datetime:%s month:%d  spotSeries: %f, m01CloseSeries: %f, m05CloseSeries: %f, m09CloseSeries: %f"%(context.contractNo(),context.dateTimeStamp(),month,spotSeries, m01CloseSeries, m05CloseSeries, m09CloseSeries) )
    #LogInfo("month:%s  spotSeries: %s, m01CloseSeries: %s, m05CloseSeries: %s, m09CloseSeries: %s"%(type(month),type(spotSeries), type(m01CloseSeries), type(m05CloseSeries), type(m09CloseSeries)) )
    # 9月到12月  合约顺序 1 5 9
    if (month > 9) and (month <= 12):
        # LogInfo(month)
        tradeContractSeries[-1] = symbol01  # 交易一月份
        tradePrice = m01CloseSeries[-1]  # 交易价格
        if spotSeries[-1] > 0:
            # LogInfo(spotSeries[-1])
            if (spotSeries[-1] > m01CloseSeries[-1]) and (m01CloseSeries[-1] > m05CloseSeries[-1]) and (m05CloseSeries[-1] > m09CloseSeries[-1]):
                # LogInfo("反向市场")
                termStructureSeries[-1] = -1  # 反向市场
            elif spotSeries[-1] < m01CloseSeries[-1] and m01CloseSeries[-1] < m05CloseSeries[-1] and m05CloseSeries[-1] < m09CloseSeries[-1]:
                # LogInfo("正向市场")
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
        else:
            if m01CloseSeries[-1] > m05CloseSeries[-1] and m05CloseSeries[-1] > m09CloseSeries[-1]:
                termStructureSeries[-1] = -1  # 反向市场
            elif m01CloseSeries[-1] < m05CloseSeries[-1] and m05CloseSeries[-1] < m09CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
    # 1月到4月  合约顺序  5 9 1
    elif (month > 1) and (month <= 4):
        tradeContractSeries[-1] = symbol05  # 交易5月份
        tradePrice = m05CloseSeries[-1]  # 交易价格
        if spotSeries[-1] > 0:
            if spotSeries[-1] > m05CloseSeries[-1] and m05CloseSeries[-1] > m09CloseSeries[-1] and m09CloseSeries[-1] > m01CloseSeries[-1]:
                termStructureSeries[-1] = -1  # 反向市场
            elif spotSeries[-1] < m05CloseSeries[-1] and m05CloseSeries[-1] < m09CloseSeries[-1] and m09CloseSeries[-1] < m01CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
        else:
            if m05CloseSeries[-1] > m09CloseSeries[-1] and m09CloseSeries[-1] > m01CloseSeries[-1]:
                termStructureSeries[-1] = -1  # 反向市场
            elif m05CloseSeries[-1] < m09CloseSeries[-1] and m09CloseSeries[-1] < m01CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
    # 6月到8月  合约顺序  9 1 5
    elif (month >= 6) and (month <= 8):
        tradeContractSeries[-1] = symbol09  # 交易9月份
        tradePrice = m09CloseSeries[-1]  # 交易价格
        if spotSeries[-1] > 0:
            if spotSeries[-1] > m09CloseSeries[-1] and m09CloseSeries[-1] > m01CloseSeries[-1] and m01CloseSeries[-1] > m05CloseSeries[-1]:
                termStructureSeries[-1] = -1  # 反向市场
            elif spotSeries[-1] < m09CloseSeries[-1] and m09CloseSeries[-1] < m01CloseSeries[-1] and m01CloseSeries[-1] < m05CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
        else:
            if m09CloseSeries[-1] > m01CloseSeries[-1] and m01CloseSeries[-1] > m05CloseSeries[-1]:
                termStructureSeries[-1] = -1  # 反向市场
            elif m09CloseSeries[-1] < m01CloseSeries[-1] and m01CloseSeries[-1] < m05CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
    elif (month == 9):  # 专门针对九月份行情的处理
        tradeContractSeries[-1] = symbol01  # 交易一月份
        tradePrice = m01CloseSeries[-1]  # 交易价格
        if spotSeries[-1] > 0:
            # LogInfo(spotSeries[-1])
            if (spotSeries[-1] > m01CloseSeries[-1]) and (m01CloseSeries[-1] > m05CloseSeries[-1]):
                # LogInfo("反向市场")
                termStructureSeries[-1] = -1  # 反向市场
            elif (spotSeries[-1] < m01CloseSeries[-1]) and (m01CloseSeries[-1] < m05CloseSeries[-1]):
                # LogInfo("正向市场")
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
        else:
            if (m01CloseSeries[-1] > m05CloseSeries[-1]):
                termStructureSeries[-1] = -1  # 反向市场
            elif (m01CloseSeries[-1] < m05CloseSeries[-1]):
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
    elif (month == 1) :  # 专门针一月份行情的处理
        tradeContractSeries[-1] = symbol05  # 交易5月份
        tradePrice = m05CloseSeries[-1]  # 交易价格
        if spotSeries[-1] > 0:
            if spotSeries[-1] > m05CloseSeries[-1] and m05CloseSeries[-1] > m09CloseSeries[-1] :
                termStructureSeries[-1] = -1  # 反向市场
            elif spotSeries[-1] < m05CloseSeries[-1] and m05CloseSeries[-1] < m09CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
        else:
            if m05CloseSeries[-1] > m09CloseSeries[-1] :
                termStructureSeries[-1] = -1  # 反向市场
            elif m05CloseSeries[-1] < m09CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
    elif (month == 5):  # 专门针五月份行情的处理
        tradeContractSeries[-1] = symbol09  # 交易9月份
        tradePrice = m09CloseSeries[-1]  # 交易价格
        if spotSeries[-1] > 0:
            if spotSeries[-1] > m09CloseSeries[-1] and m09CloseSeries[-1] > m01CloseSeries[-1] :
                termStructureSeries[-1] = -1  # 反向市场
            elif spotSeries[-1] < m09CloseSeries[-1] and m09CloseSeries[-1] < m01CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
        else:
            if m09CloseSeries[-1] > m01CloseSeries[-1]:
                termStructureSeries[-1] = -1  # 反向市场
            elif m09CloseSeries[-1] < m01CloseSeries[-1]:
                termStructureSeries[-1] = 1  # 正向市场
            else:
                termStructureSeries[-1] = 0  # 无法判断期限结构
    else:
        termStructureSeries[-1] = -2  # 不去判断期限结构的月份
        tradeContractSeries[-1] = ''  # 不去交易哪个合约

    # if termStructureSeries[-1]!=0:
    PlotNumeric("termStructure",termStructureSeries[-1], RGB_Purple(), True, True)

    # if  termStructureSeries[-1] ==1:
    #     PlotIcon(termStructureSeries[-1],3,True)  #正向市场 向上箭头
    # if termStructureSeries[-1] ==-1:
    #     PlotIcon(termStructureSeries[-1],1,True)  #反向市场 笑脸

    GoldenCross = CrossOver(ma1, ma2)
    DeathCross = CrossUnder(ma1, ma2)

    # LogInfo(tradeContractSeries[-1])
    # PlotText(Close(),tradeContractSeries[-1],RGB_Red(),True)
    # if tradeContractSeries[-1]
        
    if (month == 8) and ((tradeDateSeries[-1]+BDay(1)).month==9) and dateTimeStamp.hour == 15:  # 专门针对临近交割月的九月合约未平仓订单的处理
        #把九月合约的持仓换到一月合约上
        if m09HoldingSeries[-1]>0  and BuyPosition(symbol09)>0:
            Sell(share=BuyPosition(symbol09),price=m09CloseSeries[-1], contractNo=symbol09)
            m09HoldingSeries[-1] = 0
            Buy(share=1, price=m01CloseSeries[-1],contractNo=symbol01, needCover=True)
            m01HoldingSeries[-1] = 1
            orderTimeSeries[-1] = dateTimeStamp
            PlotIcon(Close()[-1],12,main=True)
        elif m09HoldingSeries[-1]<0  and SellPosition(symbol09)>0:
            BuyToCover(share=SellPosition(symbol09),price=m09CloseSeries[-1], contractNo=symbol09)
            m09HoldingSeries[-1] = 0
            SellShort(share=1, price=m01CloseSeries[-1],contractNo=symbol01, needCover=True)
            m01HoldingSeries[-1] = -1
            orderTimeSeries[-1] = dateTimeStamp
            PlotIcon(Close()[-1],13,main=True)
    elif (month == 12) and ((tradeDateSeries[-1]+BDay(1)).month==1) and dateTimeStamp.hour == 15:  # 专门针对临近交割月的一月合约未平仓订单的处理
        #把一月合约的持仓换到五月合约上
        if m01HoldingSeries[-1]>0  and BuyPosition(symbol01)>0:
            Sell(share=BuyPosition(symbol01),price=m01CloseSeries[-1], contractNo=symbol01)
            m01HoldingSeries[-1] = 0
            Buy(share=1, price=m05CloseSeries[-1],contractNo=symbol05, needCover=True)
            m05HoldingSeries[-1] = 1
            orderTimeSeries[-1] = dateTimeStamp
            PlotIcon(Close()[-1],12,main=True)
        elif m01HoldingSeries[-1]<0  and SellPosition(symbol01)>0:
            BuyToCover(share=SellPosition(symbol01),price=m01CloseSeries[-1], contractNo=symbol01)
            m01HoldingSeries[-1] = 0
            SellShort(share=1, price=m05CloseSeries[-1],contractNo=symbol05, needCover=True)
            m05HoldingSeries[-1] = -1
            orderTimeSeries[-1] = dateTimeStamp
            PlotIcon(Close()[-1],13,main=True)
    elif (month == 4) and ((tradeDateSeries[-1]+BDay(1)).month==5) and dateTimeStamp.hour == 15:  # 专门针对临近交割月的五月合约未平仓订单的处理
        #把五月合约的持仓换到九月合约上
        if m05HoldingSeries[-1]>0  and BuyPosition(symbol05)>0:
            Sell(share=BuyPosition(symbol05),price=m05CloseSeries[-1], contractNo=symbol05)
            m05HoldingSeries[-1] = 0
            Buy(share=1, price=m09CloseSeries[-1],contractNo=symbol09, needCover=True)
            m09HoldingSeries[-1] = 1
            orderTimeSeries[-1] = dateTimeStamp
            PlotIcon(Close()[-1],12,main=True)
        elif m05HoldingSeries[-1]<0  and SellPosition(symbol05)>0:
            BuyToCover(share=SellPosition(symbol05),price=m05CloseSeries[-1], contractNo=symbol05)
            m05HoldingSeries[-1] = 0
            SellShort(share=1, price=m09CloseSeries[-1],contractNo=symbol09, needCover=True)
            m09HoldingSeries[-1] = -1
            orderTimeSeries[-1] = dateTimeStamp
            PlotIcon(Close()[-1],13,main=True)
            
            
    flag = (GoldenCross or DeathCross) and (termStructureSeries[-1] == 1 or termStructureSeries[-1] == -1)
    # 执行下单操作
    # 无论当前期限结构的状态(正向市场,反向市场,other)
    if GoldenCross or DeathCross:
        if (not np.isnan(m01HoldingSeries[-1])) and m01HoldingSeries[-1] != 0:
            if SellPosition(symbol01) > 0:
                BuyToCover(share=SellPosition(symbol01), price=m01CloseSeries[-1], contractNo=symbol01)  
                m01HoldingSeries[-1] = 0
                orderTimeSeries[-1] = dateTimeStamp
                orderIndexSeries[-1] = orderIndexSeries[-1] + 1
            if BuyPosition(symbol01) > 0:
                Sell(share=BuyPosition(symbol01),price=m01CloseSeries[-1], contractNo=symbol01)
                m01HoldingSeries[-1] = 0
                orderTimeSeries[-1] = dateTimeStamp
                orderIndexSeries[-1] = orderIndexSeries[-1] + 1
            # if  SellPosition(symbol01)== 0 and  BuyPosition(symbol01)== 0:
                #m01HoldingSeries[-1] = 0
                #orderTimeSeries[-1] = dateTimeStamp

        if (not np.isnan(m05HoldingSeries[-1])) and m05HoldingSeries[-1] != 0:
            if SellPosition(symbol05) > 0:
                BuyToCover(share=SellPosition(symbol05), price=m05CloseSeries[-1], contractNo=symbol05) 
                m05HoldingSeries[-1] = 0
                orderTimeSeries[-1] = dateTimeStamp
                orderIndexSeries[-1] = orderIndexSeries[-1] + 1
            if BuyPosition(symbol05) > 0:
                Sell(share=BuyPosition(symbol05),price=m05CloseSeries[-1], contractNo=symbol05)
                m05HoldingSeries[-1] = 0
                orderTimeSeries[-1] = dateTimeStamp
                orderIndexSeries[-1] = orderIndexSeries[-1] + 1
            # if  SellPosition(symbol05)== 0 and  BuyPosition(symbol05)== 0:
                #m05HoldingSeries[-1] = 0
                #orderTimeSeries[-1] = dateTimeStamp

        if (not np.isnan(m09HoldingSeries[-1])) and m09HoldingSeries[-1] != 0:
            if SellPosition(symbol09) > 0:
                BuyToCover(share=SellPosition(symbol09), price=m09CloseSeries[-1], contractNo=symbol09)  
                m09HoldingSeries[-1] = 0
                orderTimeSeries[-1] = dateTimeStamp
                orderIndexSeries[-1] = orderIndexSeries[-1] + 1
            if BuyPosition(symbol09) > 0:
                Sell(share=BuyPosition(symbol09),price=m09CloseSeries[-1], contractNo=symbol09)
                m09HoldingSeries[-1] = 0
                orderTimeSeries[-1] = dateTimeStamp
                orderIndexSeries[-1] = orderIndexSeries[-1] + 1
            # if  SellPosition(symbol09)== 0 and  BuyPosition(symbol09)== 0:
                #m09HoldingSeries[-1] = 0
                #orderTimeSeries[-1] =dateTimeStamp

    if (np.isnan(m01HoldingSeries[-1]) or m01HoldingSeries[-1] == 0) and (np.isnan(m05HoldingSeries[-1]) or m05HoldingSeries[-1] == 0) and (np.isnan(m09HoldingSeries[-1]) or m09HoldingSeries[-1] == 0):
        if termStructureSeries[-1] == 1:  # 正向市场  只做空
            if DeathCross:  # 死叉
                SellShort(share=1, price=tradePrice,contractNo=tradeContractSeries[-1], needCover=True)
                PlotIcon(tradePrice,2,main=True)
                orderTimeSeries[-1] = dateTimeStamp
                if tradeContractSeries[-1] == symbol01:
                    m01HoldingSeries[-1] = -1
                elif tradeContractSeries[-1] == symbol05:
                    m05HoldingSeries[-1] = -1
                elif tradeContractSeries[-1] == symbol09:
                    m09HoldingSeries[-1] = -1

        if termStructureSeries[-1] == -1:  # 反向市场  只做多
            if GoldenCross:  # 金叉
                Buy(share=1, price=tradePrice,contractNo=tradeContractSeries[-1], needCover=True)
                PlotIcon(tradePrice,1,main=True)
                orderTimeSeries[-1] = dateTimeStamp
                if tradeContractSeries[-1] == symbol01:
                    m01HoldingSeries[-1] = 1
                elif tradeContractSeries[-1] == symbol05:
                    m05HoldingSeries[-1] = 1
                elif tradeContractSeries[-1] == symbol09:
                    m09HoldingSeries[-1] = 1

def hisover_callback(context):
    LogInfo("hisover_callback")
    pass


def exit_callback(context):
    LogInfo("exit_callback")
    pass
