import talib

code = 'NYMEX|F|CL|1909'
P    = 10

#测试波峰波谷函数
def initialize(context): 
    SetBarInterval(code, 'M', 1, 2000)

def handle_data(context):
    pivot_h = SwingHigh(Close(), P, 1, 2)
    pivot_l = SwingLow(Close(), P, 1, 2)

    PlotNumeric('Close', Close()[-1], color=RGB_Purple())
    LogInfo("HHH", Date(), Time(), pivot_h)
    LogInfo("LLL", Date(), Time(), pivot_l)

    if pivot_h > 0:
        PlotNumeric("High", pivot_h, color=RGB_Red())
    if pivot_l > 0:
        PlotNumeric("Low",  pivot_l, color=RGB_Green())
    
    
