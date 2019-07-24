import talib


def initialize(context): 
    SetBarInterval('DCE|F|I|1909', 'M', 3, 2000)


def handle_data(context):
    ta_sma = talib.SMA(Close(), timeperiod=5)
    _,es_sma = SMA(Close(), 5, 1)

    LogInfo("SMA", ta_sma[-1], es_sma[-1])

    PlotNumeric('ta_sma', ta_sma[-1], color=RGB_Red())
    PlotNumeric('es_sma', es_sma[-1], color=RGB_Blue())
