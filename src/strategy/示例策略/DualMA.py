#-*-coding:utf-8
import talib

buyPos = 0
sellPos = 0

def initialize(context):
    SetBarInterval("SHFE|F|CU|1907", 'M',1, 2000)

def handle_data(context):
    global buyPos, sellPos
    
    ma1 = talib.MA(Close(), timeperiod=5)
    ma2 = talib.MA(Close(), timeperiod=20)
    
    #记录指标
    PlotNumeric('MA1', ma1[-1], color=RGB_Red())
    PlotNumeric('MA2', ma2[-1], color=RGB_Green())
    
    PlotNumeric('Zero', 0, color=RGB_Red(), main=False)
        
    if MarketPosition() != 1 and ma1[-1] > ma2[-1]:
        Buy(1, Open()[-1])               # 买开仓
        buyPos += 1
        
    if MarketPosition() != -1 and ma1[-1] < ma2[-1]:
        SellShort(1, Open()[-1])         # 卖开仓
        sellPos += 1