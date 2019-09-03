import talib

#ContractId = "NYMEX|F|CL|1908"
#ContractId = "ZCE|F|CF|001"
BarIndexMap = {}
code1='ZCE|S|CF|909|001'
code2='ZCE|F|CF|909'
code3='ZCE|F|CF|001'

def getBarIndex(timestamp):
    if timestamp not in BarIndexMap:
        return 0
    return BarIndexMap[timestamp]

def initialize(context): 
    #SetBarInterval(ContractId, 'M', 5, 200)
    
    #SubQuote(code1)  #订阅价差组合合约的即时行情
    #SubQuote(code2)  #订阅一腿合约的即时行情    
    #SubQuote(code3)  #订阅二腿合约的即时行情
    SetBarInterval(code1 , 'M', 5, 200) 
    SetBarInterval(code2 , 'M', 5, 200)
    SetBarInterval(code3 , 'M', 5, 200)


def handle_data(context):
    #global BarIndexMap
    #his = HisBarsInfo()
    #LogInfo("AAA", his[-1]['DateTimeStamp'], his[-1]['KLineIndex'])
    #BarIndexMap[his[-1]['DateTimeStamp']] = his[-1]['KLineIndex']

    #index50 = getBarIndex(20190716145000000)
    #LogInfo(index50)
    price1 = Close(code1, 'M', 5)
    price2 = Close(code2, 'M', 5)
    price3 = Close(code3, 'M', 5)
    len1=len(price1)
    len2=len(price2)
    len3=len(price3)
    LogInfo('len1:%d, len2:%d, len3:%d' %(len1,len2,len3))
    
    if len1 > 0:
        LogInfo('CId1:%s, len1:%d, Close:%f' %(code1, len1, price1[-1]))
    
    if len2 > 0:
        LogInfo('CId2:%s, len2:%d, Close:%f' %(code2, len2, price2[-1]))
    
    if len3 > 0:
        LogInfo('CId3:%s, len3:%d, Close:%f' %(code3, len3, price3[-1]))

