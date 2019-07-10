import talib


def initialize(context): 
    SetBarInterval('DCE|F|I|1909', 'M', 1, 1)
    #SetBarInterval('ZCE|F|TA|1909', 'M', 1, 1)
    #SetBarInterval('INE|F|SC|1908', 'M', 1, 1)
    #SetBarInterval('SHFE|F|RB|1910', 'M', 1, 1)

def handle_data(context):
    LogInfo("DCE", ExchangeTime("DCE"), ExchangeStatus("DCE"))
    LogInfo("ZCE", ExchangeTime("ZCE"), ExchangeStatus("ZCE"))
    LogInfo("SHFE", ExchangeTime("SHFE"), ExchangeStatus("SHFE"))
    LogInfo("INE", ExchangeTime("INE"), ExchangeStatus("INE"))
