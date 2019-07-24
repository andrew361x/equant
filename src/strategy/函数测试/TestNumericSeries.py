import talib
from NumericSeries import NumericSeries

aa = NumericSeries()
bb = NumericSeries()
cc = NumericSeries()

def initialize(context): 
    SetBarInterval("NYMEX|F|CL|1908", 'M', 1, 2000)


def handle_data(context):
    global aa, bb,cc
    aa[-1] = Close()[-1]
    bb[-1] = Open()[-1]
    cc[-1] = min(aa[-1],bb[-1])
    PlotNumeric("cc", cc[-3])
