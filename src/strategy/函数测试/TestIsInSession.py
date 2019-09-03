import talib

code1 = 'SHFE|F|AG|1912'
code2 = 'SHFE|F|RB|2001'
code3 = 'ZCE|F|AP|001'
code4 = 'ZCE|F|SR|001'
code5 = 'DCE|F|I|2001'
code6 = 'DCE|F|C|2001'
code7 = 'CFFEX|F|IF|1909'
code8 = 'INE|F|SC|1910'


def initialize(context): 
    SetActual()
    SetBarInterval(code1, 'M', 1, 200)


def handle_data(context):
    if context.triggerType() == 'H':
        return

    LogInfo('It is not in Session', code1, IsInSession(code1), CurrentTime(), ExchangeTime('SHFE'), ExchangeStatus('SHFE'))
    LogInfo('It is not in Session', code2, IsInSession(code2), CurrentTime(), ExchangeTime('SHFE'), ExchangeStatus('SHFE'))
    LogInfo('It is not in Session', code3, IsInSession(code3), CurrentTime(), ExchangeTime('ZCE'), ExchangeStatus('ZCE'))
    LogInfo('It is not in Session', code4, IsInSession(code4), CurrentTime(), ExchangeTime('ZCE'), ExchangeStatus('ZCE'))
    LogInfo('It is not in Session', code5, IsInSession(code5), CurrentTime(), ExchangeTime('DCE'), ExchangeStatus('DCE'))
    LogInfo('It is not in Session', code6, IsInSession(code6), CurrentTime(), ExchangeTime('DCE'), ExchangeStatus('DCE'))
    LogInfo('It is not in Session', code7, IsInSession(code7), CurrentTime(), ExchangeTime('CFFEX'), ExchangeStatus('CFFEX'))
    LogInfo('It is not in Session', code8, IsInSession(code8), CurrentTime(), ExchangeTime('INE'), ExchangeStatus('INE'))
    LogInfo('Tradedate:', CalcTradeDate('ZCE|F|SR|001', 20190830110000000))

    if IsInSession(code1):
        #Sell(1, Close()[-1])
        pass
