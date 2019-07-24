# 套利策略 历史回测

import talib

code1="ZCE|F|TA|909"
code2="ZCE|F|TA|001"
p1=20
dot=2
qty=1

bar=0

def initialize(context):
    SetBarInterval(code1, 'M', 1, 1000)
    SetBarInterval(code2, 'M', 1, 2000)
    
def handle_data(context):
    if len(Close(code1, 'M', 1)) < p1 or len(Close(code2, 'M', 1)) < p1:
        return

    ma1 = talib.MA(Close(code1, 'M', 1), timeperiod=p1, matype=0)
    ma2 = talib.MA(Close(code2, 'M', 1), timeperiod=p1, matype=0)    
    LogInfo('ma1', Close(code1, 'M', 1)[-1], '  ma2', Close(code2, 'M', 1)[-1])
    
    print("ma1:", ma1[-1], "ma2:",ma2[-1]) 
    ma= ma1[-1] - ma2[-1]
    prc = Close(code1, 'M', 1)[-1] - Close(code2, 'M', 1)[-1]       
    
    PlotNumeric("ma1", ma1[-1], color=0xFF00FF)
    PlotNumeric("ma2", ma2[-1], color=0x0008FF)
    
    PlotNumeric("prc", prc, 0xFF0000, False)
    PlotNumeric("high", ma + dot * PriceTick(code1), 0x00aa00, False)
    PlotNumeric("low", ma - dot * PriceTick(code1), 0x0000FF, False)    
    PlotNumeric("fit", NetProfit(), 0xFF0000, False)
    
    global bar    
    #同一根K线上只做一笔交易
    print("bar is ", bar)
    if bar == CurrentBar(code1, 'M', 1):
        return

    if prc > ma + dot * PriceTick(code1):
        if MarketPosition(code1) == 0:
            Buy(qty, Close(code1, 'M', 1)[-1], code1)
            Buy(qty, Close(code2, 'M', 1)[-1], code2)
        elif MarketPosition() < 0:
            BuyToCover(qty, Close(code1, 'M', 1)[-1], code1)
            BuyToCover(qty, Close(code2, 'M', 1)[-1], code2)
        else:
            return
    elif prc < ma - dot * PriceTick(code1):
        if MarketPosition(code1) == 0:
            SellShort(qty, Close(code1, 'M', 1)[-1], code1)
            SellShort(qty, Close(code2, 'M', 1)[-1], code2)
        elif MarketPosition(code1) > 0:
            Sell(qty, Close(code1, 'M', 1)[-1], code1)
            Sell(qty, Close(code2, 'M', 1)[-1], code2)
        else:
            return
        
    bar = CurrentBar(code1, 'M', 1)
    




















