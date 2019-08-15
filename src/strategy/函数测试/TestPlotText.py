#-*-coding:utf-8
import talib
import numpy as np

N = 5
P = 20
keep = 0


def initialize(context):
    SetBarInterval("DCE|F|PP|1909", 'M', 4, 2000)

def handle_data(context):
    global N, keep
    ma1 = talib.MA(Close(), timeperiod=N, matype=0)
    ma2 = talib.MA(Close(), timeperiod=P, matype=0)

    keep += 1

    if keep % 5 == 0:
        color=RGB_Blue()
    else:
        color=RGB_Red() 

    PlotText(Open()[-1], "A", main=True, color=color, barsback=N)
    #UnPlotText(True, N+1)

