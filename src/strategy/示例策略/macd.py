import talib

fast = 12 # 快周期
slow = 26 # 慢周期
back = 9  # dea周期
qty = 1   # 下单量

def initialize(context): 
    # K线稳定后发单
    SetBarInterval("NYMEX|F|CL|1909", 'M', 1, 200)
    SetOrderWay(2)
    SetActual()

def handle_data(context):
    # 等待数据就绪，否则计算果结为异常值
    if len(Close()) < slow + back - 1:
        return

    # 计算MACD   
    diff, dea, macd = talib.MACD(Close(), fast, slow, back)

    # 突破下单
    if MarketPosition() != 1 and macd[-1] > 0.01:
        Buy(qty, Open()[-1]) 
    elif MarketPosition() != -1 and macd[-1] < -0.01:
        SellShort(qty, Open()[-1]) 

    # 绘制MACD曲线
    PlotNumeric('diff', diff[-1], RGB_Red(), False, False)
    PlotNumeric('dea', dea[-1], RGB_Blue(), False, False)    
    PlotStickLine('macd', 0, macd[-1], RGB_Red() if macd[-1] > 0 else RGB_Blue(), False, False) 
    # 绘制盈亏曲线
    PlotNumeric("profit", NetProfit() + FloatProfit(), 0xcccccc, False, True) 

