import talib


def initialize(context): 
    SetBarInterval('SHFE|F|CU|1907', 'M', 1, 1000)


def handle_data(context):
    #PlotVertLine(main=True, axis = True)
    #UnPlotVertLine()
    #PlotDot(name="Dot", value=Close()[-1], icon=1, main=True)
    #UnPlotDot("Dot")
    #PlotBar("BarExample1", Vol()[-1], 0, RGB_Red())
    #UnPlotBar("BarExample1")
    #PlotStickLine("StickLine", Close()[-1], Open()[-1], RGB_Blue(), True, True, 0)
    #UnPlotStickLine("StickLine")
    #'''
    idx1 = CurrentBar()
    p1 = Close()[-1]
    if idx1 >= 100:
        count = 1
        p2 = Close()[-2]
        PlotPartLine("PartLine", idx1, p1, count, p2, RGB_Red(), True, True, 1)
        #UnPlotPartLine("PartLine", idx1, count, True)
    #'''
    #PlotIcon(value=Close()[-1], icon=1)
    #UnPlotIcon()


