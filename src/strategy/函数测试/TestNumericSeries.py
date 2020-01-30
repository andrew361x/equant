import talib
from EsSeries import NumericSeries

aa = NumericSeries()
bb = NumericSeries()
cc = NumericSeries()

def initialize(context): 
    SetBarInterval("SHFE|Z|RB|MAIN", 'D', 1, 10)


def handle_data(context):
    global aa, bb,cc
    LogInfo(context.dateTimeStamp())
    LogInfo(">"*50)
    LogInfo(CurrentBar())
    LogInfo(">a"*50)
    LogInfo(aa)
    LogInfo(len(aa))
    LogInfo(">b"*50)
    LogInfo(bb)
    LogInfo(len(bb))
    LogInfo(">c"*50)
    LogInfo(cc)
    LogInfo(len(cc))
    aa[-1] = Close()[-1]
    bb[-1] = Open()[-1]
    cc[-1] = min(aa[-1],bb[-1])
    # PlotNumeric("cc", cc[-3])
    LogInfo(cc[-3])
    LogInfo("<a"*50)
    LogInfo(aa)
    LogInfo(len(aa))
    LogInfo("<b"*50)
    LogInfo(bb)
    LogInfo(len(bb))
    LogInfo("<c"*50)
    LogInfo(cc)
    LogInfo(len(cc))
    LogInfo("<"*50)
