import talib

qty = 2

def initialize(context): 
    SetBarInterval('SHFE|F|CU|1908', 'M', 1, 200)


def handle_data(context):
    cb = CurrentBar()
    LogInfo(f"[{cb}][K线{cb}初始情况]: 第一个建仓位置到当前位置的Bar计数: {BarsSinceEntry()}")

    if cb % 5 == 0:
        
        LogInfo(f"[{cb}][K线{cb}当前持仓情况]: {MarketPosition()}")

        if MarketPosition() == -1:
            Buy(1, Close()[-1])
            LogInfo(f"[{cb}][K线{cb}平卖仓又开买仓后]: 第一个建仓位置到当前位置的Bar计数: {BarsSinceEntry()}")

        else:
            Buy(1, Close()[-1])
            LogInfo(f"[{cb}][K线{cb}开买仓后]: 第一个建仓位置到当前位置的Bar计数: {BarsSinceEntry()}")


    if cb % 30 == 0:
        SellShort(1, Close()[-1])
        LogInfo(f"[{cb}][K线{cb}平买仓又开卖仓后]: 第一个建仓位置到当前位置的Bar计数: {BarsSinceEntry()}")

    
    

