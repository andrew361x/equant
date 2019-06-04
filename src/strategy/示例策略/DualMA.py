import talib

p1=5
p2=20

def initialize(context): 
    SetBarInterval("SHFE|F|RB|1910", 'M', 1,  2000)
    SetActual()

def handle_data(context):
    # 使用talib计算均价
    ma1 = talib.MA(Close(), timeperiod=p1, matype=0)
    ma2 = talib.MA(Close(), timeperiod=p2, matype=0)
    
    # 绘制指标图形
    PlotNumeric("ma1", ma1[-1], color=RGB_Red())
    PlotNumeric("ma2", ma2[-1], color=RGB_Green())    
    PlotNumeric("fit", NetProfit(), RGB_Red(), False)

    # 执行下单操作
    if MarketPosition() <= 0 and ma1[-1] > ma2[-1]:
        Buy(1, Close()[-1])
    if MarketPosition() >= 0 and ma1[-1] < ma2[-1]:
        SellShort(1, Close()[-1])
