#-*-coding:utf-8
import talib
import numpy as np

N = 5
P = 20

def initialize(context):
    SetBarInterval("DCE|F|PP|1909", 'M', 4, 10)

def handle_data(context):
    global N
    ma1 = talib.MA(Close(), timeperiod=N, matype=0)
    ma2 = talib.MA(Close(), timeperiod=P, matype=0)
	
    PlotText(Open()[-1], "A", main=True, barsback=N)
    UnPlotText(True, N+1)

