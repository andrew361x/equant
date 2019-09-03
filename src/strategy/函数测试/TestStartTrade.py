import talib

userNo = 'Q437104345'
code = 'NYMEX|F|CL|1910'
handle_times = 1
start_flag = False

def initialize(context): 
    SetUserNo(userNo)
    SetActual()
    SetBarInterval(code, 'M', 1, 200)


def handle_data(context):
    global handle_times, start_flag
    
    if context.triggerType() == 'H':
        return

    if handle_times % 100 == 0:
        if start_flag:
            StartTrade()
            start_flag = False
            LogInfo('StartTrade')
        else:
            StopTrade()
            start_flag = True
            LogInfo('StopTrade')

    handle_times += 1
    


def exit_callback(context):
    pass
