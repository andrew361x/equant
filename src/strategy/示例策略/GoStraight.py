import talib


N = 35
N0 = 47
N1 = 49
N2 = 29

p = 20

def initialize(context): 
    SetBarInterval("ZCE|F|CF|001", 'M', 1, 2000)
    pass


def handle_data(context):
    MA1 = talib.MA(Close(), timeperiod=p)
    MA2 = talib.MIN(Low(), timeperiod=p)
    MA3 = talib.MAX(High(), timeperiod=p)
    #LogInfo(MA2)
    #LogInfo(MA3)
    MA4 = talib.MA(Close(), timeperiod=N1)
    MA5 = talib.MA(Close(), timeperiod=N2)
    if len(MA2) < 55 or len(MA3) < 67:
        return

    if MarketPosition() == 0:
        if (Close()[-1] > MA1[-1]) and (MA5[-1] > MA4[-1]) and (Close()[-1] > MA3[-N0]):
            Buy(1, Close()[-1])
        elif (MA1[-1] > Close()[-1]) and (MA5[-1] < MA4[-1]) and (Close()[-1] < MA4[-1]):
            SellShort(1, Close()[-1])
        else:
            pass

    else:
        if Close()[-1] < MA2[-N]:
            Sell(1, Close()[-1])
        elif Close()[-1] > MA3[-N0]:
            BuyToCover(1,Close()[-1])    #买平仓
        else:
            pass

