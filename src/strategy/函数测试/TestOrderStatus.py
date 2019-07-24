import talib

sentOrder = True
localIdList = []

def initialize(context): 
    SetBarInterval("NYMEX|F|CL|1908", 'M', 1, 200)
    SetActual()


def handle_data(context):
    global sentOrder, localIdList
    if context.triggerType() == 'H':
        return

    if sentOrder:
        for i in range(10):
            ret, localId = A_SendOrder(Enum_Buy(), Enum_Entry(), 1, Q_Last())
            if ret == 0: localIdList.append(localId)
        sentOrder = False

    for lid in localIdList:
        LogInfo("ORDER", lid, A_GetOrderNo(lid), A_OrderStatus(lid))
    
