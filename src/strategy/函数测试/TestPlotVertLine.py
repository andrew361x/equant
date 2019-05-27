import talib


def initialize(context): 
    SetBarInterval('SHFE|F|CU|1907', 'M',1)


def handle_data(context):
    PlotVertLine(main=True, axis = True)




