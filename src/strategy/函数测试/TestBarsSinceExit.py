import talib


def initialize(context): 
    SetBarInterval('ZCE|F|TA|909', 'M', 1, 200)


def handle_data(context):
    cb = CurrentBar()
    LogInfo(f"[{cb}][K线{cb}初始情况]: 最近一个平仓位置到当前位置的Bar计数: {BarsSinceExit()}")

    if cb % 5 == 0:
        
        LogInfo(f"[{cb}][K线{cb}当前持仓情况]: {MarketPosition()}")

        if MarketPosition() == 1:
            SellShort(1, Close()[-1])
            LogInfo(f"[{cb}][K线{cb}平买仓又开卖仓后]: 最近一个平仓位置到当前位置的Bar计数: {BarsSinceExit()}")

        else:
            SellShort(1, Close()[-1])
            LogInfo(f"[{cb}][K线{cb}开卖仓后]: 最近一个平仓位置到当前位置的Bar计数: {BarsSinceExit()}")


    if cb % 30 == 0:
        Buy(1, Close()[-1])
        LogInfo(f"[{cb}][K线{cb}当前持仓情况]: {MarketPosition()}")
        LogInfo(f"[{cb}][K线{cb}平卖仓又开买仓后]: 最近一个平仓位置到当前位置的Bar计数: {BarsSinceExit()}")


