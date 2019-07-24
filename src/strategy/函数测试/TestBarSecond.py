import talib


def initialize(context): 
    SetBarInterval("NYMEX|F|CL|1908", 'T', 5, 2000)


def handle_data(context):
    pass
