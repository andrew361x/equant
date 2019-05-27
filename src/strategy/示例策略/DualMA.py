import talib

p1=5
p2=20

def initialize(context): 
    SetBarInterval("ZCE|F|TA|909", 'M', 1, "20190510")
    SetActual()

def handle_data(context):
    # 数据根数小于p2时不执行判断，因为这段时间算出的ma2为无效值
    if len(Close()) < p2:
        return;     
    
    # 使用talib计算均价
    ma1 = talib.MA(Close(), timeperiod=p1, matype=0)
    ma2 = talib.MA(Close(), timeperiod=p2, matype=0)
    
    # 绘制指标图形
    PlotNumeric("ma1", ma1[-1], color=0xFF0000)
    PlotNumeric("ma2", ma2[-1], color=0x00aa00)    
    PlotNumeric("fit", NetProfit(), 0xFF0000, False)

    # 执行下单操作
    if MarketPosition() <= 0 and ma1[-1] > ma2[-1]:
        Buy(1, Close()[-1])
    if MarketPosition() >= 0 and ma1[-1] < ma2[-1]:
        SellShort(1, Close()[-1])























































































































































