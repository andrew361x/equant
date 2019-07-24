# 套利策略，盘实运行

import talib

usr="DDY"
code1="ZCE|F|TA|909"
code2="ZCE|F|TA|001"
tp = 'M'
p = 10

p1=5
p2=20
dot=1
qty=1

bar=0

def initialize(context):
    SetBarInterval(code1, 'M', p, 1)
    SetBarInterval(code2, 'M', p, 1)
    SetTriggerType(code1, 1)
    SetTriggerType(code2, 1)
    SetActual()

def handle_data(context):
    if len(Close(code1, tp, p)) < p1 or len(Close(code2, tp, p)) < p2:
        return

    ma1 = talib.MA(Close(code1, tp, p), timeperiod=p1)
    ma2 = talib.MA(Close(code2, tp, p), timeperiod=p1)
    sma1= ma1[-1] - ma2[-1]
    ma1 = talib.MA(Close(code1, tp, p), timeperiod=p2)
    ma2 = talib.MA(Close(code2, tp, p), timeperiod=p2)
    sma2= ma1[-1] - ma2[-1]     
    
    PlotNumeric("sma1", sma1, 0x0000FF, False)
    PlotNumeric("sma2", sma2, 0xFF0000, False)
    PlotNumeric("profit", A_TotalProfitLoss() + A_ProfitLoss() - A_Cost(), 0x808080, False, True) 
    
    if context.strategyStatus() !='C':
        return
    
    global bar    
    #同一根K线上只做一笔交易
    if bar == CurrentBar():
        return

    offset = Enum_Entry()
    if sma1 > sma2 + dot * PriceTick():
        # 不允许多笔多仓
        if A_TotalPosition() > 0:
            return
        if A_SellPosition(code1) > 0 or A_SellPosition(code2) > 0:
            offset = Enum_ExitToday()
        A_SendOrder(usr, code1, '2', '0', Enum_Buy() , offset, 'T', Q_BidPrice(code1) + PriceTick(), qty)
        A_SendOrder(usr, code2, '2', '0', Enum_Sell(), offset, 'T', Q_AskPrice(code2) - PriceTick(), qty)
    elif sma1 < sma2 - dot * PriceTick():
        # 不允许多笔空仓
        if A_TotalPosition() < 0:
            return
        if A_BuyPosition(code1) > 0 or A_BuyPosition(code2) > 0:
            offset = Enum_ExitToday()
        A_SendOrder(usr, code1, '2', '0', Enum_Sell(), offset, 'T', Q_AskPrice(code2) - PriceTick(), qty)
        A_SendOrder(usr, code2, '2', '0', Enum_Buy() , offset, 'T', Q_BidPrice(code1) + PriceTick(), qty)
        
    bar == CurrentBar()

