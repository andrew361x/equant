import talib


def initialize(context): 
    SetBarInterval('NYMEX|F|CL|1910', 'M', 1, 100)


def handle_data(context):
    LogInfo(Close()[-1])

def exit_callback(context):
    LogInfo("CCCCCCCCCCC")
