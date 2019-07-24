import talib
from datetime import datetime

def initialize(context): 
    SetBarInterval('DCE|F|I|1909', 'M', 1, 1)
    #SetBarInterval('ZCE|F|TA|1909', 'M', 1, 1)
    #SetBarInterval('INE|F|SC|1908', 'M', 1, 1)
    #SetBarInterval('SHFE|F|RB|1910', 'M', 1, 1)

def handle_data(context):
    now = datetime.now()
    LogInfo("DCE", now, ExchangeTime("DCE"), ExchangeStatus("DCE"))
    LogInfo("ZCE", now,ExchangeTime("ZCE"), ExchangeStatus("ZCE"))
    LogInfo("SHFE", now,ExchangeTime("SHFE"), ExchangeStatus("SHFE"))
    LogInfo("INE", now,ExchangeTime("INE"), ExchangeStatus("INE"))
    LogInfo("CFFEX", now,ExchangeTime("CFFEX"), ExchangeStatus("CFFEX"))
