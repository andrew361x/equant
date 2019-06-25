# 双均线策略，兼容历史阶段和实盘阶段的运行
import talib
from talib import MA_Type

p1 = 5
p2 = 10
p3 = 20
p4 = 40

code="ZCE|F|TA|909"
#code = "NYMEX|F|CL|1906"
usr ="DDY"
qty = 1

bar = 0

def initialize(context):
    SetBarInterval(code, 'M', 3, '20190520')
    SetOrderWay(1)
    SetTriggerType(code, 1)
    SetActual()
    
#历史测回执行逻辑
def his_trigger(ma1, ma2):
    if ma1[-1] > ma2[-1]:
        if MarketPosition() == 0:
            Buy(qty, Close()[-1])       
        elif MarketPosition() < 0:
            BuyToCover(qty, Close()[-1])
        else:
            return False
    elif ma1[-1] < ma2[-1]:
        if MarketPosition() == 0:
            SellShort(qty, Close()[-1])
        elif MarketPosition() > 0:
            Sell(qty, Close()[-1])
        else:
            return False
    return True
    
#实盘阶段执行逻辑
def tim_trigger(ma1, ma2):
    if ma1[-1] > ma2[-1]:
        if A_TotalPosition() == 0:
            A_SendOrder(Enum_Buy(), Enum_Entry(), qty, Q_BidPrice() + PriceTick())
        elif A_TotalPosition() < 0:
            A_SendOrder(Enum_Buy(), Enum_ExitToday(), qty, Q_BidPrice() + PriceTick())
        else:
            return False
    elif ma1[-1] < ma2[-1]:
        if A_TotalPosition() == 0:
            A_SendOrder(Enum_Sell(), Enum_Entry(), qty, Q_AskPrice() - PriceTick())
        elif A_TotalPosition() > 0:
            A_SendOrder(Enum_Sell(), Enum_ExitToday(), qty, Q_AskPrice() - PriceTick())
        else:
            return False
    return True
    

def handle_data(context):
    if len(Close()) < p4:
        return;
        
    ma1 = talib.MA(Close(), timeperiod=p1, matype=0)
    ma2 = talib.MA(Close(), timeperiod=p2, matype=0)
    ma3 = talib.MA(Close(), timeperiod=p3, matype=0)
    ma4 = talib.MA(Close(), timeperiod=p4, matype=0)
    
    PlotNumeric("ma1", ma1[-1], color=0xFF0000)
    PlotNumeric("ma2", ma2[-1], color=0x00aa00)
    PlotNumeric("ma3", ma3[-1], color=0x0000FF)
    PlotNumeric("ma4", ma4[-1], color=0xFF00FF)  
        
    # 盈利曲线
    if BarStatus() == 2:
        PlotNumeric("fit2", A_TotalProfitLoss(), 0xFF0000, False) 
    else:
        PlotNumeric("fit1", NetProfit(), 0x0000FF, False)
            
    global bar       
    # 同一根K线上只做一笔交易
    if bar == CurrentBar():
        return
    
    if BarStatus() == 2:
        if not tim_trigger(ma1, ma3):
            return
    else:
        if not his_trigger(ma1, ma3):
            return
   
    bar = CurrentBar()



