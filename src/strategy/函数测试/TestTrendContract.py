import talib

code = "DCE|Z|I|MAIN"

def initialize(context): 
    SetBarInterval(code, 'M', 1, 2000)
    pass


def handle_data(context):
    GetTrendContract(code)
    LogInfo(code, GetTrendContract(code))
