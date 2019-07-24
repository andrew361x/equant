import talib


def initialize(context): 
    SetBarInterval("NYMEX|F|CL|1908", 'M', 1, 1000)


def handle_data(context):
    date = CurrentDate()
    time = CurrentTime()
    diff = TimeDiff(time)    

    LogInfo(date, time, diff)
