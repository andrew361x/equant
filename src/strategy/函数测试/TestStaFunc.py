import talib

rd=0

def initialize(context): 
    SetBarInterval('SHFE|F|CU|1907', 'M',1, 100)


def handle_data(context):
    global rd
    close = Close()
    ret, smas = SMA(close, 12, 2)
    PlotNumeric("SMA", smas[-1], color=RGB_Brown())
    LogInfo("round:%d, len:%d, sma:%f, cl:%f\n" %(rd, len(close), smas[-1], close[-1]))

    opcs, opos, oposs, otrans = ParabolicSAR(High(), Low(), 0.02, 0.2)
    PlotNumeric("SAR1-oParClose", opcs[-1], color=RGB_Red())
    PlotNumeric("SAR2-oParOpen", opos[-1], color=RGB_Blue())
    PlotNumeric("SAR3-oPosition", oposs[-1], color=RGB_Red(), main=False)
    PlotNumeric("SAR4-oTransition", otrans[-1], color=RGB_Blue(), main=False)
    LogInfo("round:%d, opc:%f, opo:%f, opos:%d, otran:%d\n" %(rd, opcs[-1], opos[-1], oposs[-1], otrans[-1]))
    rd = rd+1
