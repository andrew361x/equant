import talib

code1 = 'ZCE|F|TA|001'
code2 = 'ZCE|F|TA|005'
scode = 'SPD|s|TA|001|005'

def initialize(context): 
    SetBarInterval(scode, 'M', 1, 300)
    SetBarInterval(code1, 'M', 1, 300)
    SetBarInterval(code2, 'M', 1, 300)

def handle_data(context):
    tim = context.dateTimeStamp()
    LogInfo('quote time: %s.%s %s' % (tim[:8], tim[8:12], context.contractNo()))  

