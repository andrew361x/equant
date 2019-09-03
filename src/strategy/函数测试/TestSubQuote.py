import talib

g_CommNo1 = "NYMEX|F|CL"
g_ContNo1 = "NYMEX|F|CL|1910"

g_CommNo2 = "HKEX|F|HSI"
g_ContNo2 = "HKEX|F|HSI|1908"

g_60count = 0
g_60times = 60
S_Cont = 'COMEX|S|GC|1909|1910'
F_Cont1 = 'COMEX|F|GC|1909'
F_Cont2 = 'COMEX|F|GC|1910'


def initialize(context): 
    SetBarInterval("ZCE|S|TA|909|001", 'M', 1, 1)
    SubQuote(g_CommNo1)

def handle_data(context):
    global g_60count
    g_60count = g_60count +1
    if g_60count == g_60times:
        SubQuote(g_CommNo2)
        SubQuote("ZCE|F|CF|909")
    LogInfo(g_60count, g_ContNo1, Q_Last(g_ContNo1))
    LogInfo(g_60count, g_ContNo2, Q_Last(g_ContNo2))
    LogInfo(g_60count, "ZCE|F|CF|909", Q_Last("ZCE|F|CF|909"), Q_AskPrice("ZCE|F|CF|909"))
