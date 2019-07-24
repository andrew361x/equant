import talib


def initialize(context): 
    SetBarInterval("NYMEX|F|CL|1908", 'M', 1, 200)


def handle_data(context):
    count = CountIf(Close()>Open(), 10)
    LogInfo("9999", count)
