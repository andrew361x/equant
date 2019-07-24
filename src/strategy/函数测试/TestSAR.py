import talib

runsVar = 2

def initialize(context): 
    SetBarInterval("SHFE|F|RB|1910", 'M', 1, 2000)


def handle_data(context):
    afStep  = runsVar / 100 
    afLimit = afStep  * 10
    sar = talib.SAR(High(), Low(), afStep,afLimit)

    OParCl, OParOp, OPosition, OTRansition = ParabolicSAR(High(), Low(), afStep, afLimit)
    LogInfo("SAR", Date(), Time(), sar[-1], OParCl[-1])
    PlotNumeric("SAR", sar[-1])
    PlotNumeric("ESAR", OParCl[-1], color=RGB_Blue())
