#-*-coding:utf-8
import talib
import numpy as np


def initialize(context):
    SetBarInterval("SHFE|F|CU|1907", 'M',1, 2000)
    
def handle_data(context):
   
    ma1 = talib.MA(Close(), timeperiod=5, matype=0)
    ma2 = talib.MA(Close(), timeperiod=20, matype=0)

    diff = ma1[-1] - ma2[-1]

    PlotNumeric("ICON",diff, color=RGB_Brown(),main=False)
    if diff == 0:
        PlotIcon(diff, 14)    
    elif diff > 0: 
        PlotIcon(diff, 15)
    else:
        PlotIcon(diff, 9)
