import talib

code = 'NYMEX|F|CL|1910'

user_no = 'Q437104345'
order_count = 0
order_list = []

def initialize(context): 
    SetActual()
    SetUserNo(user_no)
    SetBarInterval(code, 'M', 1, 100)


def handle_data(context):
    global order_count

    if context.triggerType() == 'H':
        return
    if order_count < 10:
        ret, lid = A_SendOrder(Enum_Sell(), Enum_Entry(), 1, Close()[-1] + 5*PriceTick())
        order_count += 1

        if ret == 0:
            order_list.append(lid)

def exit_callback(context):
    for lid in order_list:
        status = A_OrderStatus(user_no, lid)
        LogInfo(user_no, code, status)

    DeleteAllOrders()
