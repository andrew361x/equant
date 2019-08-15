import talib
import EsTalib
import EsTalib2
from EsSeries import NumericSeries

ue_sma  = NumericSeries()
ue_sma2 = NumericSeries()

def initialize(context): 
    SetBarInterval('DCE|F|I|1909', 'M', 3, 2000)


def handle_data(context):
    global ue_sma
    ta_sma = talib.SMA(Close(), timeperiod=5)
    es_sma = SMA(Close(), 5, 5)
    ue_sma[-1]  = EsTalib.U_SMA(ue_sma, Close(), 5, 5)
    ue_sma2[-1] = EsTalib2.U_SMA(Close(), 5, 5)

    LogInfo("SMA", ta_sma[-1], es_sma[-1], ue_sma[-1], ue_sma2[-1])

    PlotNumeric('ta_sma', ta_sma[-1], color=RGB_Red())
    PlotNumeric('es_sma', es_sma[-1], color=RGB_Blue())
    PlotNumeric('ue_sma', ue_sma[-1], color=RGB_Green())
    PlotNumeric('ue_sma2', ue_sma2[-1], color=RGB_Purple())
