import talib
import UserFunc1
from UserFunc2 import UserModel
from BarsInfo import Bars

code1 = "DCE|Z|I|MAIN"
code2 = "ZCE|Z|TA|MAIN"
barType = 'M'
barValue = 1

g_UserFunc2 = UserModel()
bars = Bars()

def initialize(context): 
    SetBarInterval(code1, barType, barValue, 1)
    SetBarInterval(code2, barType, barValue, 1)
    SetTriggerType(3, 1000)


def handle_data(context):
    last1 = UserFunc1.getQLast(code1)
    last2 = UserFunc1.getQLast(code2)
    LogInfo(last1, last2,g_UserFunc2.getCurTime(code1))
    
    open1 = Open(code1, barType, barValue)
    close1 = Close(code1, barType, barValue)
    barsLast = bars.BarsLast(open1[-1] > close1[-1], code1, barType, barValue)
    LogInfo("BarIndex : ", CurrentBar(code1, barType, barValue), "Open : ", open1[-1], "Close : ", close1[-1], "BarsLast : ", barsLast)
