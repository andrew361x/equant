import talib


def initialize(context): 
    #SetBarInterval("SHFE|F|AL|1908", 'M', 1, 200)
    SetBarInterval("NYMEX|F|CL|1910", 'M', 1, 200)


def handle_data(context):

    #LogInfo('Tradedate:', CalcTradeDate('ZCE|F|SR|001', 20190830093000000))
    #LogInfo('Tradedate:', CalcTradeDate('ZCE|F|SR|001', 20190830230000000))
    tradedate = CalcTradeDate('ZCE|F|SR|001', 20190904230000000)
    LogInfo('TradeTime:', TradeSessionBeginTime('ZCE|F|SR|001', tradedate, 0), TradeSessionEndTime('ZCE|F|SR|001', tradedate, -1))
   
