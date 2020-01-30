import talib
#import numpy as np
#import pandas as pd
#from EsSeries import NumericSeries
import os, os.path
import json

p1=5
p2=20
contractSymbol = "RU"
contractExchange = "SHFE"

symbolindex = contractExchange + "|Z|" + contractSymbol + "|INDEX"#基准合约
mainContract = contractExchange + "|Z|" + contractSymbol +"|MAIN"
contractCfgPath = os.path.abspath( os.path.join(os.getcwd(), "..",'files',"contractConfig.json") )


barInteval = 30
barType = 'M'

def initialize(context): 
     # 必须订阅品种 周期，然后Close无法获取数据 ，但是handledata会每次都回调  因为对获取到的数据进行了替换，所以这里获取一根数据速度就会快点
    SetBarInterval(symbolindex,barType,barInteval,10)
    SetBarInterval(mainContract,barType,barInteval,10) 
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
    SetMargin(0, margin, mainContract)
    
    # 手续费,统一按照 万分之1.1
    SetTradeFee('A', 1, tradefree, contractNo=symbolindex)
    SetTradeFee('A', 1, tradefree, contractNo=mainContract)
    
    #设置滑点
    #SetSlippage(1)
    

def handle_data(context):
    #tim = context.dateTimeStamp()
    #LogInfo('quote time: %s.%s %s' % (tim[:8], tim[8:12], context.contractNo()))  

    currentContract =  context.contractNo()
    if(currentContract!=symbolindex):
        return
     
    ## 只有index合约才会进入
    if len(Close(symbolindex,barType,barInteval)) < p2:
       return
    
    #LogInfo(spot[context.tradeDate])
    # 使用talib计算均价
    ma1 = talib.EMA(Close(symbolindex,barType,barInteval), p1)
    ma2 = talib.EMA(Close(symbolindex,barType,barInteval), p2) 
    GoldenCross = CrossOver(ma1,ma2)
    DeathCross = CrossUnder(ma1,ma2)
    # 绘制指标图形
    PlotNumeric("ma1", ma1[-1], RGB_Red())
    PlotNumeric("ma2", ma2[-1], RGB_Green())    
    
    GoldenCross = CrossOver(ma1,ma2)
    DeathCross = CrossUnder(ma1,ma2)
    #PlotVertLine(RGB_Red(), main=True)
    
    flag = (GoldenCross or DeathCross ) 

    # 执行下单操作
    if MarketPosition(mainContract) <= 0 and GoldenCross:
        Buy(share=1, price=Close(mainContract,barType,barInteval)[-1],contractNo=mainContract)
        PlotIcon(Close(mainContract,barType,barInteval)[-1],1,main=True)
    if MarketPosition(mainContract) >= 0 and DeathCross:
        SellShort(share=1, price=Close(mainContract,barType,barInteval)[-1],contractNo=mainContract)
        PlotIcon(Close(mainContract,barType,barInteval)[-1],2,main=True)
    
    # 绘制指标图形
    PlotNumeric("ma1", ma1[-1], RGB_Red())
    PlotNumeric("ma2", ma2[-1], RGB_Green())    
    PlotNumeric("fit", NetProfit() + FloatProfit(symbolindex) - TradeCost(), RGB_Red(), False)

def hisover_callback(context):
    LogInfo("hisover_callback")
    pass


def exit_callback(context):
    LogInfo("exit_callback")
    pass
