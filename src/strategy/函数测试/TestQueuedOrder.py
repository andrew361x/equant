import talib

sendtimes = 0
code2 = 'NYMEX|Z|CL|MAIN'

def initialize(context): 
    SetUserNo('Q437104345')
    SetBarInterval(code2, 'M', 1, 1)
    SetActual()

def handle_data(context):
    global sendtimes
    if context.triggerType == 'H':
        return
    if sendtimes < 2:
        A_SendOrder(Enum_Sell(), Enum_Entry(), 1, Q_Last() + 3 * PriceTick(), code2)
        sendtimes += 1

    queueOrders = A_AllQueueOrderNo()
    LogInfo("AAAAAA", queueOrders)

    if len(queueOrders) > 0:
        DeleteAllOrders()
