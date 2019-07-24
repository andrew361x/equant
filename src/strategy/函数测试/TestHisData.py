import talib

ContractId = "NYMEX|F|CL|1908"
BarIndexMap = {}

def getBarIndex(timestamp):
    if timestamp not in BarIndexMap:
        return 0
    return BarIndexMap[timestamp]

def initialize(context): 
    SetBarInterval(ContractId, 'M', 1, 2000)


def handle_data(context):
    global BarIndexMap
    his = HisBarsInfo()
    LogInfo("AAA", his[-1]['DateTimeStamp'], his[-1]['KLineIndex'])
    BarIndexMap[his[-1]['DateTimeStamp']] = his[-1]['KLineIndex']

    index50 = getBarIndex(20190716145000000)
    LogInfo(index50)
