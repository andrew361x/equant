import talib


def initialize(context): 
    SetBarInterval("NYMEX|F|CL|1908", 'M', 1, 200)


def handle_data(context):
    avail = A_Available()
    margin = A_Margin()
    assets = A_Assets()

    LogInfo(avail, margin, assets)
