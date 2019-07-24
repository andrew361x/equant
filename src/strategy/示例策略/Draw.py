import talib

code1 = "SHFE|F|ZN|1907"
bar = 0

def initialize(context): 
    SetBarInterval(code1, 'M', 5, "20190520")
    SetActual()

def handle_data(context):    
    PlotNumeric("last", Close()[-1], 0x000000) 
    if context.strategyStatus() == 'C':         
        bid = Q_BidPrice()
        ask = Q_AskPrice()
        PlotNumeric("bid", bid, 0x00FF00)    
        PlotNumeric("ask", ask, 0xFF0000) 
    else:
        bid = ask = Close()[-1]                  
    
    global bar
    if bar == CurrentBar():
        return
        
    if MarketPosition() != 1:
        Buy(1, bid)
    elif MarketPosition() != -1:
        SellShort(1, ask)

    bar = CurrentBar()

    PlotNumeric("profit", NetProfit() +  FloatProfit(), 0xFF00FF, False, True)      


