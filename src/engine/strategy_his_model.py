import numpy as np
from capi.com_types import *
from .engine_model import *
import time, sys
import datetime
import copy
import math
import pandas as pd

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class TradeDateBars:
    def __init__(self, tradeDate):
        self._tradeDate = tradeDate
        self._data = []

    def updateBar(self, bar):
        assert "TradeDate" in bar and self.isInCurDataSet(bar["TradeDate"]), " error "
        if len(self._data) > 0 and bar["DateTimeStamp"] <= self._data[-1]["DateTimeStamp"]:
            self._data[-1] = bar
        else:
            self._data.append(bar)

    def getLastBar(self):
        if len(self._data) == 0:
            return None
        return self._data[-1]

    # 是否应该在当前数据结构中
    def isInCurDataSet(self, tradeDate):
        return tradeDate == self._tradeDate

    def getData(self):
        return self._data

    def getTradeDate(self):
        return self._tradeDate


class BarInfo(object):
    '''
    _curBar = 
        {
            'KLineIndex'    : value,
            'TradeDate'     : value,
            'DateTimeStamp' : value,
            'TotalQty'      : value,
            'PositionQty'   : value,
            'LastPrice'     : value,
            'KLineQty'      : value,
            'OpeningPrice'  : value,
            'HighPrice'     : value,
            'LowPrice'      : value,
            'SettlePrice'   : value,
        }
    '''
    
    def __init__(self, logger):
        self._logger = logger
        self._barList = []
        self._curBar = None

        #
        self._tradeDateBars = {}

    def _getBarValue(self, key):
        barValue = []
        for bar in self._barList:
            barValue.append(bar[key])
        return np.array(barValue)
    
    def updateBar(self, data):
        self._curBar = data
        if len(self._barList) > 0 and data["DateTimeStamp"] <= self._barList[-1]["DateTimeStamp"]:
            self._barList[-1] = data
        else:
            self._barList.append(data)

        #
        if data["TradeDate"] not in self._tradeDateBars:
            self._tradeDateBars[data["TradeDate"]] = TradeDateBars(data["TradeDate"])
        self._tradeDateBars[data["TradeDate"]].updateBar(data)

    def getCurBar(self):
        return self._curBar

    def getBarOpen(self):
        return self._getBarValue('OpeningPrice')
        
    def getBarClose(self):
        return self._getBarValue('LastPrice')

    def getBarVol(self):
        return self._getBarValue('TotalQty')

    def getBarOpenInt(self):
        return self._getBarValue('PositionQty')

    def getBarHigh(self):
        return self._getBarValue('HighPrice')
        
    def getBarLow(self):
        return self._getBarValue('LowPrice')

    def getBarTime(self):
        return self._getBarValue('DateTimeStamp')
        
    def getBarTradeDate(self):
        return self._curBar['TradeDate']

    def getBarList(self):
        return self._barList

    def getTradeDateKLine(self, tradeDate):
        if tradeDate not in self._tradeDateBars:
            return None
        return self._tradeDateBars[tradeDate].getData()
        
        
class StrategyHisQuote(object):
    '''
    功能：历史数据模型
    模型：
    _metaData = {
        'ZCE|F|SR|905' : 
        {
            'KLineReady' : False
            'KLineType'  : type
            'KLineSlice' : slice,
            'KLineData'  : [
                {
                    KLineIndex     : 0, 
                    TradeDate      : 20190405,
                    DateTimeStamp  : 20190405000000000,
                    TotalQty       : 1,
                    PositionQty    : 1,
                    LastPrice      : 4500,
                    KLineQty       : 1,
                    OpeningPrice   : 4500,
                    HighPrice      : 4500,
                    LowPrice       : 4500,
                    SettlePrice    : 4500,   
                },
                {
                    ...
                }
            ]
        }
        ...
    }
    '''
    def __init__(self, strategy, config, calc, parentDateModel):
        self._dataModel = parentDateModel
        # K线数据定义
        # response data
        self._kLineRspData = {}
        self._kLineNoticeData = {}
        self._curEarliestKLineDateTimeStamp = {}
        self._lastEarliestKLineDateTimeStamp = {}
        self._pkgEarliestKLineDateTimeStamp = {}
        self._hisLength = {}

        self._strategy = strategy
        self.logger = strategy.logger
        self._config = config
        self._calc = calc
        
        self._strategyName = strategy.getStrategyName()
        self._signalName = self._strategyName + "_Signal"
        self._textName = self._strategyName + "_Text"
        
        # 运行位置的数据
        # 和存储位置的数据不一样，存储的数据 >= 运行的数据。
        self._curBarDict = {}

        #
        self._firstRealTimeKLine = {}

    def initialize(self):
        self._contractTuple = self._config.getContract()
        # 基准合约
        self._contractNo = self._config.getBenchmark()
        # 回测样本配置
        self._sampleDict = self._config.getSample()
        self._useSample = self._config.getRunMode()["Simulate"]["UseSample"]
        # 触发方式配置
        self._triggerDict = self._config.getTrigger()
        
        # Bar
        for record in self._config.getKLineKindsInfo():
            key = (record["ContractNo"], record["KLineType"], record["KLineSlice"])
            self._curBarDict[key] = BarInfo(self.logger)
            self._kLineRspData[key] = {
                'KLineReady': False,
                'KLineData': []
            }
            self._kLineNoticeData[key] = {
                'KLineReady': False,
                'KLineData': [],
            }
            self._hisLength[key] = 0
            self._pkgEarliestKLineDateTimeStamp[key] = -1
            self._curEarliestKLineDateTimeStamp[key] = sys.maxsize
            self._lastEarliestKLineDateTimeStamp[key] = -1
            self._firstRealTimeKLine[key] = True

    # //////////////`////////////////////////////////////////////////////

    def getHisLength(self):
        return self._hisLength
    # ////////////////////////BaseApi类接口////////////////////////
    def getBarOpenInt(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return []

        return self._curBarDict[multiContKey].getBarOpenInt()

    def getBarTradeDate(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return 0

        curBar = self._curBarDict[multiContKey].getCurBar()
        return int(curBar['TradeDate'])

    def getBarCount(self, multiContKey):
        '''if multiContKey not in self._kLineRspData:
            return 0'''

        kLineHisData = self._kLineRspData[multiContKey]['KLineData']

        if multiContKey not in self._kLineNoticeData:
            return len(kLineHisData)

        kLineNoticeData = self._kLineNoticeData[multiContKey]['KLineData']
        if len(kLineNoticeData) == 0:
            return len(kLineHisData)

        lastHisBar = kLineHisData[-1]
        lastNoticeBar = kLineNoticeData[-1]

        return len(kLineHisData) + (lastNoticeBar['KLineIndex'] - lastHisBar['KLineIndex'])

    def getBarStatus(self, multiContKey):
        if multiContKey not in self._kLineRspData:
            return -1
        
        kLineHisData = self._kLineRspData[multiContKey]['KLineData']
        firstIndex = kLineHisData[0]['KLineIndex']
        lastIndex  = kLineHisData[-1]['KLineIndex']
        
        if multiContKey in self._kLineNoticeData:
            kLineNoticeData = self._kLineNoticeData[multiContKey]['KLineData']
            if len(kLineNoticeData) > 0:
                lastIndex = kLineNoticeData[-1]['KLineIndex']

        curBar = self._curBarDict[multiContKey].getCurBar()
        curBarIndex = curBar['KLineIndex']
        
        if curBarIndex == firstIndex:
            return 0
        elif curBarIndex >= lastIndex:
            return 2
        else:
            return 1

    def isHistoryDataExist(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return False

        return True if len(self._kLineRspData[multiContKey]) else False

    def getBarDate(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return 0
        curBar = self._curBarDict[multiContKey].getCurBar()
        return int(curBar['DateTimeStamp'] // 1000000000)

    def getBarTime(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return 0
        curBar = self._curBarDict[multiContKey].getCurBar()
        timeStamp = str(curBar['DateTimeStamp'])
        return float(timeStamp[-9:])/1000000000

    def getBarOpen(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return np.array([])
            
        return self._curBarDict[multiContKey].getBarOpen()

    def getBarClose(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return np.array([])
            
        return self._curBarDict[multiContKey].getBarClose()

    def getOpenD(self, daysAgo, multiContKey):
        openList = self.getBarOpen(multiContKey)

        if len(openList) == 0:
            contNo = multiContKey[0]
            raise Exception("请确保在策略的initialize方法中使用SetBarInterval(\"%s\", 'D', 1)方法订阅%s合约的日线信息"%(contNo, contNo))

        if daysAgo+1 > len(openList):
            return -1
        return openList[-(daysAgo + 1)]

    def getCloseD(self, daysAgo, multiContKey):
        priceList = self.getBarClose(multiContKey)

        if len(priceList) == 0:
            contNo = multiContKey[0]
            raise Exception("请确保在策略的initialize方法中使用SetBarInterval(\"%s\", 'D', 1)方法订阅%s合约的日线信息"%(contNo, contNo))

        if daysAgo+1 > len(priceList):
            return -1
        return priceList[-(daysAgo + 1)]

    def getHighD(self, daysAgo, multiContKey):
        priceList = self.getBarHigh(multiContKey)

        if len(priceList) == 0:
            contNo = multiContKey[0]
            raise Exception("请确保在策略的initialize方法中使用SetBarInterval(\"%s\", 'D', 1)方法订阅%s合约的日线信息"%(contNo, contNo))

        if daysAgo+1 > len(priceList):
            return -1
        return priceList[-(daysAgo + 1)]

    def getLowD(self, daysAgo, multiContKey):
        priceList = self.getBarLow(multiContKey)

        if len(priceList) == 0:
            contNo = multiContKey[0]
            raise Exception("请确保在策略的initialize方法中使用SetBarInterval(\"%s\", 'D', 1)方法订阅%s合约的日线信息"%(contNo, contNo))

        if daysAgo+1 > len(priceList):
            return -1
        return priceList[-(daysAgo + 1)]

    def getBarVol(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return np.array([])
            
        return self._curBarDict[multiContKey].getBarVol()
        
    def getBarHigh(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return np.array([])
        return self._curBarDict[multiContKey].getBarHigh()
        
    def getBarLow(self, multiContKey):
        if multiContKey not in self._curBarDict:
            return np.array([])
        return self._curBarDict[multiContKey].getBarLow()

    def getHisData(self, dataType, multiContKey, maxLength):
        if dataType not in (BarDataClose, BarDataOpen, BarDataHigh,
                            BarDataLow, BarDataMedian, BarDataTypical,
                            BarDataWeighted, BarDataVol, BarDataOpi,
                            BarDataTime):
            return []

        methodMap = {
            BarDataClose    : self.getBarClose,
            BarDataOpen     : self.getBarOpen,
            BarDataHigh     : self.getBarHigh,
            BarDataLow      : self.getBarLow,
            BarDataMedian   : self.getBarMedian,
            BarDataTypical  : self.getBarTypical,
            BarDataWeighted : self.getBarWeighted,
            BarDataVol      : self.getBarVol,
            BarDataOpi      : self.getBarOpenInt,
            BarDataTime     : self.getBarTime,
        }

        numArray = methodMap[dataType](multiContKey)

        return numArray if len(numArray) <= maxLength else numArray[-maxLength : ]

    def getHisBarsInfo(self, multiContKey, maxLength):
        if maxLength is not None and maxLength <= 0:
            return []

        if multiContKey not in self._curBarDict:
            return []

        barInfo = self._curBarDict[multiContKey]
        barInfoList = barInfo._barList
        if not barInfoList:
            return []

        return barInfoList if maxLength is None or len(barInfoList) <= maxLength else barInfoList[-maxLength : ]

    #//////////////////////////////////内部接口//////////////////////////////////

    # 获取存储位置最后一根k线的交易日
    def getLastTradeDate(self):
        result = {}
        for contractNo in self._contractTuple:
            lastKLine, _ = self.getLastStoredKLine(contractNo)
            if lastKLine is None:
                result[contractNo] = None
            else:
                result[contractNo] = lastKLine["TradeDate"]
        return result

    def getLastStoredKLine(self, key):
        noticeKLineDatas = self._kLineNoticeData[key]["KLineData"]
        rspKLineDatas = self._kLineRspData[key]["KLineData"]
        if len(noticeKLineDatas) > 0:
            return noticeKLineDatas[-1], KLineFromRealTime
        elif len(rspKLineDatas)>0:
            return rspKLineDatas[-1], KLineFromHis
        else:
            return None, None

    def setLastStoredKLineStable(self, key):
        noticeKLineDatas = self._kLineNoticeData[key]["KLineData"]
        if len(noticeKLineDatas) > 0:
            noticeKLineDatas[-1]["IsKLineStable"] = True
        else:
            pass

    def getLastRunKLine(self, contractNo):
        assert contractNo in self._curBarDict, "error"
        barManager = self._curBarDict[contractNo]
        return barManager.getCurBar()

    def getBarMedian(self, contNo):
        high = self.getBarHigh(contNo)
        low = self.getBarLow(contNo)
        minLength = min(len(high), len(low))
        if minLength == 0:
            return []
        medianList = []
        for i in range(0, minLength):
            median = (high[i] + low[i]) / 2
            medianList.append(median)
        return np.array(medianList)

    def getBarTypical(self, contNo):
        high = self.getBarHigh(contNo)
        low = self.getBarLow(contNo)
        close = self.getBarClose(contNo)
        minLength = min(len(high), len(low), len(close))
        if minLength == 0:
            return []
        typicalList = []
        for i in range(0, int(minLength)):
            typical = (high[i] + low[i] + close[i]) / 3
            typicalList.append(typical)
        return np.array(typicalList)

    def getBarWeighted(self, contNo):
        high = self.getBarHigh(contNo)
        low = self.getBarLow(contNo)
        open = self.getBarOpen(contNo)
        close = self.getBarClose(contNo)
        minLength = min(len(high), len(low), len(open), len(close))
        if minLength == 0:
            return []
        weightedList = []
        for i in range(0, minLength):
            weighted = (high[i] + low[i] + open[i] + close[i]) / 4
            weightedList.append(weighted)
        return np.array(weightedList)

    #////////////////////////参数设置类接口///////////////////////
        
    def _getKLineType(self):
        # if not self._sampleDict:
        #     return None
        # return self._sampleDict['KLineType']
        return self._config.getKLineType()
        
    def _getKLineSlice(self):
        # if not self._sampleDict:
        #     return None
        # return self._sampleDict['KLineSlice']
        return self._config.getKLineSlice()

    def _getKLineCount(self, sampleDict):
        if not sampleDict['UseSample']:
            return 1

        if sampleDict['KLineCount'] > 0:
            return sampleDict['KLineCount']

        if len(sampleDict['BeginTime']) > 0:
            return sampleDict['BeginTime']

        if sampleDict['AllK']:
            nowDateTime = datetime.now()
            if self._getKLineType() == EEQU_KLINE_DAY:
                threeYearsBeforeDateTime = nowDateTime - relativedelta(years = 3)
                threeYearsBeforeStr = datetime.strftime(threeYearsBeforeDateTime, "%Y%m%d")
                return threeYearsBeforeStr
            elif self._getKLineType() == EEQU_KLINE_HOUR or self._getKLineType() == EEQU_KLINE_MINUTE:
                oneMonthBeforeDateTime = nowDateTime - relativedelta(months = 1)
                oneMonthBeforeStr = datetime.strftime(oneMonthBeforeDateTime, "%Y%m%d")
                return oneMonthBeforeStr
            elif self._getKLineType() == EEQU_KLINE_SECOND:
                oneWeekBeforeDateTime = nowDateTime - relativedelta(days = 7)
                oneWeekBeforeStr = datetime.strftime(oneWeekBeforeDateTime, "%Y%m%d")
                return oneWeekBeforeStr
            else:
                raise NotImplementedError

    # //////////////////////////K线处理接口////////////////////////
    def reqAndSubKLineByCount(self, contractNo, kLineType, kLineSlice, count, notice):
        # print("请求k线", contractNo, kLineType, kLineSlice, count)
        # 请求历史K线阶段先不订阅
        event = Event({
            'EventCode'   : EV_ST2EG_SUB_HISQUOTE,
            'StrategyId'  : self._strategy.getStrategyId(),
            'ContractNo'  : contractNo,
            'KLineType'   : kLineType,
            'KLineSlice'  : kLineSlice,
            'Data'        : {
                    'ReqCount'   :  count,
                    'ContractNo' :  contractNo,
                    'KLineType'  :  kLineType,
                    'KLineSlice' :  kLineSlice,
                    'NeedNotice' :  notice,
                },
            })

        self._strategy.sendEvent2Engine(event)

    # '''向9.5请求所有合约历史数据'''
    # 请求历史k线，同时订阅即时k线, 参数全部合法, 至少请求一根
    def reqAndSubKLine(self):
        self._isReqByDate = {}
        self._reqBeginDate = {}
        self._isReqByDateEnd = {}
        self._reqKLineTimes = {}

        dateTimeStampLength = len("20190326143100000")
        for record in self._config.getKLineSubsInfo():
            countOrDate = record['BarCount']
            key = (record['ContractNo'], record['KLineType'], record['KLineSlice'])
            # print(" count or date is ", countOrDate)
            if isinstance(countOrDate, int):
                self._isReqByDate[key] = False
                self.reqAndSubKLineByCount(key[0], key[1], key[2], countOrDate, EEQU_NOTICE_NEED)
            else:
                self._isReqByDate[key] = True
                self._isReqByDateEnd[key] = False
                self._reqBeginDate[key] = int(countOrDate + (dateTimeStampLength - len(countOrDate)) * '0')
                self._reqKLineTimes[key] = 1
                count = self._reqKLineTimes[key] * 4000
                self.reqAndSubKLineByCount(key[0], key[1], key[2], count, EEQU_NOTICE_NOTNEED)

    def _handleKLineRspData(self, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        self._insertHisRspData(event)
        if self.isHisQuoteRspEnd(event):
            self._reIndexHisRspData(key)
            self._hisLength[key] = len(self._kLineRspData[key]["KLineData"])
            # if key == self._config.getKLineShowInfoSimple():
            #     print(self._kLineRspData[key]["KLineData"])

    # 当 not self._reqByDateEnd时，更新
    def _updateRspDataRefDTS(self, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        assert self._isReqByDate[key] and not self._isReqByDateEnd[key], "error"
        dataList = event.getData()
        contractNo = event.getContractNo()
        # update current package earliest KLine DateTimeStamp
        if len(dataList) == 0:
            pass
        else:
            self._pkgEarliestKLineDateTimeStamp[key] = dataList[-1]["DateTimeStamp"]
        # update current req earliest KLine DateTimeStamp
        if event.isChainEnd() and self._pkgEarliestKLineDateTimeStamp[key]<self._curEarliestKLineDateTimeStamp[key]:
            self._curEarliestKLineDateTimeStamp[key] = self._pkgEarliestKLineDateTimeStamp[key]

    def _handleKLineRspByDate(self, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        if not self._isReqByDateEnd[key]:
            self._insertHisRspData(event)
            self._updateRspDataRefDTS(event)
            if event.isChainEnd():
                self._isReqByDateContinue(event)
        else:
            self._handleKLineRspData(event)

    #
    def _isReqByDateContinue(self,  event):
        assert event.isChainEnd(), " error call"
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        if self._curEarliestKLineDateTimeStamp[key] <= self._reqBeginDate[key]:
            self._isReqByDateEnd[key] = True
            self.reqAndSubKLineByCount(key[0], key[1], key[2], self._reqKLineTimes[key] * 4000, EEQU_NOTICE_NEED)
        # 9.5 lack data
        elif self._curEarliestKLineDateTimeStamp[key] == self._lastEarliestKLineDateTimeStamp[key]:
            self._isReqByDateEnd[key] = True
            self.reqAndSubKLineByCount(key[0], key[1], key[2], self._reqKLineTimes[key] * 4000, EEQU_NOTICE_NEED)
        # local lack data
        elif self._curEarliestKLineDateTimeStamp[key] > self._reqBeginDate[key]:
            self._reqKLineTimes[key] += 1
            self.reqAndSubKLineByCount(key[0], key[1], key[2], self._reqKLineTimes[key] * 4000, EEQU_NOTICE_NOTNEED)
            self._lastEarliestKLineDateTimeStamp[key] = self._curEarliestKLineDateTimeStamp[key]
        else:
            raise IndexError("can't be this case")

    def _handleKLineRspByCount(self, event):
        self._handleKLineRspData(event)

    # response 数据
    def onHisQuoteRsp(self, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        kindInfo = {"ContractNo":key[0], "KLineType":key[1],"KLineSlice":key[2]}
        #print("key = ", key, len(event.getData()), event.isChainEnd(), kindInfo)
        #print(self._config.getKLineKindsInfo())

        assert kindInfo in self._config.getKLineKindsInfo(), " Error "
        if not self._isReqByDate[key]:                        # req by count
            self._handleKLineRspByCount(event)
        else:                                               # req by date
            self._handleKLineRspByDate(event)

    def isHisQuoteRspEnd(self, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        if event.isChainEnd() and not self._isReqByDate[key]:
            return True
        if event.isChainEnd() and self._isReqByDate[key] and self._isReqByDateEnd[key]:
            return True
        return False

    # 更新response 数据
    def _insertHisRspData(self, event):
        contNo = event.getContractNo()
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        localRspKLineData = self._kLineRspData[key]["KLineData"]

        kLineRspMsg = event.getData()
        # print("datalist is ", dataList)
        for kLineData in kLineRspMsg:
            kLineData["ContractNo"] = event.getContractNo()
            kLineData["KLineType"] = event.getKLineType()
            kLineData['KLineSlice'] = event.getKLineSlice()
            kLineData["Priority"] = self._config.getPriority(key)
            if self._isReqByDate[key]:
                if len(localRspKLineData) == 0 or (len(localRspKLineData) >= 1 and kLineData["DateTimeStamp"]<localRspKLineData[0]["DateTimeStamp"] and \
                kLineData["DateTimeStamp"] >= self._reqBeginDate[key]):
                    localRspKLineData.insert(0, kLineData)
            else:
                if len(localRspKLineData) == 0 or (len(localRspKLineData) >= 1 and kLineData["DateTimeStamp"]<localRspKLineData[0]["DateTimeStamp"]):
                    localRspKLineData.insert(0, kLineData)

    def _reIndexHisRspData(self, key):
        dataDict = self._kLineRspData[key]
        rfdataList = dataDict['KLineData']
        dataDict['KLineReady'] = True
        for i, record in enumerate(rfdataList):
            rfdataList[i]['KLineIndex'] = i+1

    def _handleKLineNoticeData(self, localDataList, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())

        # notice数据，直接加到队尾
        for data in event.getData():
            isNewKLine = True
            data["IsKLineStable"] = False
            storedLastKLine, lastKLineSource = self.getLastStoredKLine(key)
            # 没有数据，索引取回测数据的最后一条数据的索引，没有数据从1开始
            if storedLastKLine is None:
                data["KLineIndex"] = 1
                localDataList.append(data)
            else:
                lastKLineIndex = storedLastKLine["KLineIndex"]
                lastKLineDTS = storedLastKLine["DateTimeStamp"]
                if lastKLineDTS == data["DateTimeStamp"]:
                    data["KLineIndex"] = lastKLineIndex
                    isNewKLine = False
                    self._handleSameKLine(localDataList, data, lastKLineSource)
                elif lastKLineDTS < data["DateTimeStamp"]:
                    data["KLineIndex"] = lastKLineIndex+1
                    self.setLastStoredKLineStable(key)
                    localDataList.append(data)
                    # print(" 存储位置 new k line index =", data["KLineIndex"])
                else:
                    self.logger.error("error DateTimeStamp on StrategyHisQuote notice")

            # 处理触发
            # 一定要先填触发事件，在填充数据。
            # 否则触发有可能会覆盖
            isRealTimeStatus = self._strategy.isRealTimeStatus()
            orderWay = str(self._config.getSendOrder())
            kLineTrigger = self._config.hasKLineTrigger()
            if not kLineTrigger:
                pass
            elif self._strategy.isHisStatus() and len(localDataList) >= 2 and localDataList[-2]["IsKLineStable"] and isNewKLine:
                self._sendHisKLineTriggerEvent(key, localDataList[-2])
            elif isRealTimeStatus:
                # 一种特殊情况
                if self._firstRealTimeKLine[key] and isNewKLine and len(localDataList) >=2 and localDataList[-2]["IsKLineStable"] and orderWay==SendOrderRealTime:
                    self._sendHisKLineTriggerEvent(key, localDataList[-2])
                self._firstRealTimeKLine[key] = False

                if orderWay==SendOrderRealTime:
                    self._sendRealTimeKLineTriggerEvent(key, localDataList[-1])
                elif orderWay==SendOrderStable and len(localDataList) >= 2 and localDataList[-2]["IsKLineStable"] and isNewKLine:
                    self._sendRealTimeKLineTriggerEvent(key, localDataList[-2])
            else:
                pass

            # 实时阶段填充最新数据。
            # 触发和填充都更新运行位置数据
            # 但是仅填充数据事件向9.5发送数据
            if isRealTimeStatus:
                self._fillDataWhenRealTime(key, localDataList[-1])

    def _handleSameKLine(self, localDataList, data, lastKLineSource):
        if lastKLineSource == KLineFromHis:
            localDataList.append(data)
        elif lastKLineSource == KLineFromRealTime:
            localDataList[-1] = data

    def _fillDataWhenRealTime(self, key, data):
        event = Event({
            "EventCode": ST_TRIGGER_FILL_DATA,
            "ContractNo": key[0],
            "KLineType": key[1],
            "KLineSlice": key[2],
            "Data": {
                "Data": data,
                "Status": ST_STATUS_CONTINUES
            }
        })
        # print("[on his quote notice]填充k线到队列", data["KLineIndex"], data)
        self._strategy.sendTriggerQueue(event)
        return

    # # 填充k线
    # def _sendKLine(self, key, data, isRealTimeStatus):
    #     if not isRealTimeStatus and data["IsKLineStable"]:
    #         event = Event({
    #             "EventCode" : ST_TRIGGER_FILL_DATA,
    #             "ContractNo": key[0],
    #             "KLineType" : key[1],
    #             "KLineSlice": key[2],
    #             "Data": {
    #                 "Data": data,
    #                 "Status": ST_STATUS_HISTORY
    #             }
    #         })
    #         self._strategy.sendTriggerQueue(event)
    #         return
    #
    #     if isRealTimeStatus:


    def _sendHisKLineTriggerEvent(self, key, data):
        if not data["IsKLineStable"]:
            return

        assert key[1] is not None, "k line type error"
        event = Event({
            'EventCode': ST_TRIGGER_HIS_KLINE,
            'ContractNo': key[0],
            "KLineType": key[1],
            "KLineSlice": key[2],
            'Data': {
                "Data": data,
                "TradeDate": data["TradeDate"],
                "DateTimeStamp": data["DateTimeStamp"],
            }
        })
        self._strategy.sendTriggerQueue(event)

    def _sendRealTimeKLineTriggerEvent(self, key, data):
        kLineTrigger = self._config.hasKLineTrigger()
        if not kLineTrigger or key not in self._config.getKLineTriggerInfoSimple():
            return

        assert self._strategy.isRealTimeStatus(), " Error "
        orderWay = str(self._config.getSendOrder())
        if orderWay == SendOrderRealTime:
            event = Event({
                'EventCode': ST_TRIGGER_KLINE,
                'ContractNo': key[0],
                "KLineType": key[1],
                "KLineSlice": key[2],
                'Data': {
                    "Data":data,
                    "TradeDate": data["TradeDate"],
                    "DateTimeStamp":data["DateTimeStamp"],
                }
            })
            self._strategy.sendTriggerQueue(event)
            return

        if orderWay == SendOrderStable and data["IsKLineStable"]:
            event = Event({
                'EventCode': ST_TRIGGER_KLINE,
                'ContractNo': key[0],
                "KLineType": key[1],
                "KLineSlice": key[2],
                'Data': {
                    "Data": data,
                    "TradeDate": data["TradeDate"],
                    "DateTimeStamp": data["DateTimeStamp"],
                }
            })
            self._strategy.sendTriggerQueue(event)
            return

    def onHisQuoteNotice(self, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        kindInfo = {"ContractNo": key[0], "KLineType": key[1], "KLineSlice": key[2]}
        # print("kind = ", event.getData()[0]["DateTimeStamp"], kindInfo, )
        # 丢掉
        if not self._kLineRspData[key]["KLineReady"]:
            return

        # print("[on his quote notice ]", kindInfo, len(event.getData()), event.getData()[0]["DateTimeStamp"])
        assert kindInfo in self._config.getKLineKindsInfo(), " Error "
        localDataList = self._kLineNoticeData[key]['KLineData']
        self._handleKLineNoticeData(localDataList, event)

    # ///////////////////////////回测接口////////////////////////////////
    def _isAllReady(self):
        for record in self._config.getKLineKindsInfo():
            key = (record["ContractNo"], record["KLineType"], record["KLineSlice"])
            if not self._kLineRspData[key]["KLineReady"]:
                return False
        return True

    def _switchKLine(self, key=None):
        if key is None:
            key = self._config.getKLineShowInfoSimple()
        event = Event({
            "EventCode" :EV_ST2EG_SWITCH_STRATEGY,
            'StrategyId': self._strategy.getStrategyId(),
            'Data':
                {
                    'StrategyName': self._strategy.getStrategyName(),
                    'ContractNo'  : key[0],
                    'KLineType'   : key[1],
                    'KLineSlice'  : key[2],
                }
        })
        
        self._strategy.sendEvent2Engine(event)
        
    def _addSingleKLine(self, data):
        event = Event({
            "EventCode"  : EV_ST2EG_UPDATE_KLINEDATA,
            "StrategyId" : self._strategy.getStrategyId(),
            "KLineType"  : self._getKLineType(),
            "Data": {
                'Count'  : 1,
                "Data"   : [data,],
            }
        })
        # print("问题1：中间阶段:", data["KLineIndex"], data["DateTimeStamp"])
        self._strategy.sendEvent2Engine(event)
        
    def _addSignal(self):
        event = Event({
            "EventCode":EV_ST2EG_ADD_KLINESIGNAL,
            'StrategyId':self._strategy.getStrategyId(),
            "Data":{
                'ItemName':'EquantSignal',
                'Type': EEQU_INDICATOR,
                'Color': 0,
                'Thick': 1,
                'OwnAxis': EEQU_ISNOT_AXIS,
                'Param': [],
                'ParamNum': 0,
                'Groupid': 0,
                'GroupName':'Equant',
                'Main': EEQU_IS_MAIN,
            }
        })
        self._strategy.sendEvent2Engine(event)
    
    def _updateCurBar(self, key, data):
        '''更新当前Bar值'''
        self._curBarDict[key].updateBar(data)
        
    def _updateOtherBar(self, otherContractDatas):
        '''根据指定合约Bar值，更新其他合约bar值'''
        for otherContract, otherContractData in otherContractDatas.items():
            if otherContract not in self._curBarDict:
                self._curBarDict[otherContract] = BarInfo(self.logger)
            self._curBarDict[otherContract].updateBar(otherContractData)
    
    def _sendFlushEvent(self):
        event = Event({
            "EventCode": EV_ST2EG_UPDATE_STRATEGYDATA,
            "StrategyId": self._strategy.getStrategyId(),
        })
        self._strategy.sendEvent2Engine(event)
        
    def getCurBar(self, key=None):
        if not key:
            key = self._config.getKLineShowInfoSimple()
        return self._curBarDict[key].getCurBar()

    def printRspReady(self):
        for record in self._config.getKLineKindsInfo():
            key = (record["ContractNo"], record["KLineType"], record["KLineSlice"])
            print(record["ContractNo"], self._kLineRspData[key]["KLineReady"])

    def runReport(self, context, handle_data):
        # 不使用历史K线，也需要切换
        # 切换K线
        key = self._config.getKLineShowInfoSimple()

        self._switchKLine(key)
        # 增加信号线
        self._addSignal()
        self._sendFlushEvent()

        while not self._isAllReady():
            # print("waiting for data arrived ")
            # self.printRspReady()
            time.sleep(1)

        allHisData = []
        for record in self._config.getKLineKindsInfo():
            key = (record["ContractNo"], record["KLineType"], record["KLineSlice"])
            hisData = self._kLineRspData[key]["KLineData"]
            allHisData.extend(hisData)

        if len(allHisData) == 0:
            self.logger.error("没有数据，请检查SetBarInterval函数")
            return

        newDF = pd.DataFrame(allHisData)
        test = newDF[["DateTimeStamp", "KLineType", "KLineSlice"]].values
        effectiveDTS = []
        for i, record in enumerate(test):
            curBarDTS = datetime.strptime(str(record[0]), "%Y%m%d%H%M%S%f")
            if record[1] == EEQU_KLINE_MINUTE:
                curEffectiveDTS = curBarDTS-relativedelta(minutes=record[2])
            elif record[1] == EEQU_KLINE_DAY:
                curEffectiveDTS = curBarDTS-relativedelta(days=record[2])
            elif record[1] == EEQU_KLINE_SECOND:
                curEffectiveDTS = curBarDTS-relativedelta(seconds=record[2])
            elif record[1] == EEQU_KLINE_TICK:
                curEffectiveDTS = curBarDTS
            else:
                raise NotImplementedError("未实现的k线类型支持")
            effectiveDTS.append(curEffectiveDTS.strftime("%Y%m%d%H%M%S%f"))

        newDF["DateTimeStampForSort"] = effectiveDTS
        newDF.sort_values(['TradeDate', 'DateTimeStampForSort', 'Priority'], ascending=[True, True, False], inplace=True)
        newDF.reset_index(drop=True, inplace=True)

        # print("new df is ")
        # print(newDF[["TradeDate", "DateTimeStampForSort", "DateTimeStamp", "KLineType"]])
        allHisData = newDF.to_dict(orient="index")

        # print(newDF[["ContractNo", "TradeDate", "DateTimeStamp"]])
        beginTime = datetime.now();beginTimeStr = datetime.now().strftime('%H:%M:%S.%f')
        print('**************************** run his begin', len(allHisData))
        self.logger.info('[runReport] run report begin')
        beginPos = 0
        endPos = 0
        for index, row in allHisData.items():
            key = (row["ContractNo"], row["KLineType"], row["KLineSlice"])
            isShow = key == self._config.getKLineShowInfoSimple()

            # print(key, self._config.getKLineShowInfoSimple(),
            lastBar = self.getCurBar(key)
            self._updateCurBar(key, row)
            curBar = self.getCurBar(key)
            if lastBar is None or math.fabs(curBar["LastPrice"]-lastBar["LastPrice"])>1e-4:
                self._calcProfitWhenHis()
            if not self._config.hasKLineTrigger():
                continue

            # if key in self._config.getKLineTriggerInfoSimple():
            if key == self._config.getKLineShowInfoSimple():
                args = {
                    "Status": ST_STATUS_HISTORY,
                    "TriggerType":ST_TRIGGER_HIS_KLINE,
                    "ContractNo":key[0],
                    "KLineType":key[1],
                    "KLineSlice":key[2],
                    "TradeDate":row["TradeDate"],
                    "DateTimeStamp":row["DateTimeStamp"],
                    "TriggerData":row,
                }
                self._strategy.setCurTriggerSourceInfo(args)
                context.setCurTriggerSourceInfo(args)
                handle_data(context)

            # # 要显示的k线
            if isShow:
                endPos += 1

            # 发送刷新事件
            if isShow and endPos % 50 == 0:
                batchKLine = self._curBarDict[key].getBarList()[beginPos:endPos]
                self._addBatchKLine(batchKLine)
                self._sendFlushEvent()
                beginPos = endPos
                tradeDate = self._curBarDict[key].getCurBar()["TradeDate"]

            # 收到策略停止或退出信号， 退出历史回测
            if self._strategy._isExit():
                break

        if endPos != beginPos:
            batchKLine = self._curBarDict[key].getBarList()[beginPos:]
            self._addBatchKLine(batchKLine)
        self._sendFlushEvent()
        endTime = datetime.now();endTimeStr = datetime.now().strftime('%H:%M:%S.%f')
        self.logger.debug('[runReport] run report completed!')
        # self.logger.debug('[runReport] run report completed!, k线数量: {}, 耗时: {}s'.format(len(allHisData), endTime-beginTime))
        # print('**************************** run his end')

    def _addBatchKLine(self, data):
        event = Event({
            "EventCode": EV_ST2EG_NOTICE_KLINEDATA,
            "StrategyId": self._strategy.getStrategyId(),
            "KLineType": self._getKLineType(),
            "Data": {
                'Count': len(data),
                "Data": copy.deepcopy(data),
            }
        })
        # print("历史回测阶段:", data["KLineIndex"])
        self._strategy.sendEvent2Engine(event)

    # 在跑历史回测期间积攒的实时数据，但是作为历史回测, 因为有效期已过。
    def runVirtualReport(self, context, handle_data, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        kLineData = event.getData()["Data"]
        isShow = key==self._config.getKLineShowInfoSimple()
        # **************************
        lastBar = self.getCurBar(key)
        self._updateCurBar(key, kLineData)
        curBar = self.getCurBar(key)
        if lastBar is None or math.fabs(curBar["LastPrice"] - lastBar["LastPrice"]) > 1e-4:
            self._calcProfitWhenHis()
        # **************************
        if self._config.hasKLineTrigger() and key in self._config.getKLineTriggerInfoSimple():
            args = {
                "Status": ST_STATUS_HISTORY,
                "TriggerType": ST_TRIGGER_HIS_KLINE,
                "ContractNo": event.getContractNo(),
                "KLineType": event.getKLineType(),
                "KLineSlice": event.getKLineSlice(),
                "TradeDate": kLineData["TradeDate"],
                "DateTimeStamp": kLineData["DateTimeStamp"],
                "TriggerData": kLineData
            }
            self._strategy.setCurTriggerSourceInfo(args)
            context.setCurTriggerSourceInfo(args)
            handle_data(context)

        if isShow:
            self._addSingleKLine(kLineData)
            self._sendFlushEvent()

    def _calcProfitWhenHis(self):
        priceInfos = {}
        curTriggerInfo = self._strategy.getCurTriggerSourceInfo()

        if curTriggerInfo is None:
            return

        key = (curTriggerInfo["ContractNo"], curTriggerInfo["KLineType"], curTriggerInfo["KLineSlice"])
        assert key[1] is not None, "error"

        curBar = self._curBarDict[key].getCurBar()
        priceInfos[key[0]] = {
            "LastPrice": curBar['LastPrice'],
            "DateTimeStamp": curBar['DateTimeStamp'],
            "TradeDate": curBar['TradeDate'],
            "LastPriceSource": KLineFromHis,
        }
        self._calc.calcProfit([key[0]], priceInfos)

    def drawBatchHisKine(self, data):
        self.sendAllHisKLine(data)
        self._sendFlushEvent()

    def sendAllHisKLine(self, data):
        if len(data) == 0:
            return
        # print("len = ", len(data))
        event = Event({
            "EventCode": EV_ST2EG_NOTICE_KLINEDATA,
            "StrategyId": self._strategy.getStrategyId(),
            "KLineType": self._getKLineType(),
            "Data": {
                'Count': len(data),
                "Data": data,
            }
        })
        self._strategy.sendEvent2Engine(event)

    # 填充k线, 发送到9.5
    def runFillData(self, context, handle_data, event):
        key = (event.getContractNo(), event.getKLineType(), event.getKLineSlice())
        data = event.getData()["Data"]
        self._updateCurBar(key, data)
        # print("[run fill data] ", data["KLineIndex"], data["KLineQty"])
        if key == self._config.getKLineShowInfoSimple():
            self._sendRealTimeKLine2Client(key, data)
            # print(self._strategy.isRealTimeStatus(), self._strategy._runStatus, self._strategy._runRealTimeStatus, self._strategy.isRealTimeAsHisStatus())
            self._sendFlushEvent()

    # ST_STATUS_CONTINUES_AS_REALTIME 阶段
    def runRealTime(self, context, handle_data, event):
        eventCode = event.getEventCode()
        assert eventCode in [ST_TRIGGER_KLINE, ST_TRIGGER_TRADE_ORDER, ST_TRIGGER_TRADE_MATCH,\
        ST_TRIGGER_SANPSHOT_FILL, ST_TRIGGER_TIMER, ST_TRIGGER_CYCLE],  "Error "

        if eventCode == ST_TRIGGER_SANPSHOT_FILL:
            # 计算浮动盈亏
            try:
                self._calcProfitByQuote(event)
            except Exception as e:
                self.logger.error("即时行情计算浮动盈亏出现错误")

            # 处理止损止盈
            self._handleStopWinLose(event)

            # 延迟判断是否即时行情触发
            if not self._config.hasSnapShotTrigger() or not self._strategy.isRealTimeStatus():
                return
            if event.getContractNo() not in self._config.getTriggerContract():
                return
        else:
            pass

        if not self._strategy.isRealTimeStatus():
            return

        allData = event.getData()
        args = {
            "Status": ST_STATUS_CONTINUES,
            "TriggerType": eventCode,
            "ContractNo": event.getContractNo(),
            "KLineType": event.getKLineType(),
            "KLineSlice": event.getKLineSlice(),
            "TradeDate": allData["TradeDate"],
            "DateTimeStamp": allData["DateTimeStamp"],
            "TriggerData": allData["Data"]
        }
        self._strategy.setCurTriggerSourceInfo(args)
        context.setCurTriggerSourceInfo(args)
        handle_data(context)
        self._sendFlushEvent()

    def _sendRealTimeKLine2Client(self, key, data):
        # print("now data is ", data, self._getKLineSlice())
        event = Event({
            "EventCode": EV_ST2EG_UPDATE_KLINEDATA,
            "StrategyId": self._strategy.getStrategyId(),
            "ContractNo": key[0],
            "KLineType":  key[1],
            "KLineSlice": key[2],
            "Data": {
                'Count': 1,
                "Data": [data, ],
            }
        })
        # print("问题1：实盘阶段:", data["KLineIndex"], data["DateTimeStamp"])
        self._strategy.sendEvent2Engine(event)

    def _calcProfitByQuote(self, event):
        #
        data = event.getData()
        lv1Data = data["Data"]
        dateTimeStamp = data["DateTimeStamp"]
        tradeDate = data["TradeDate"]
        isLastPriceChanged = data["IsLastPriceChanged"]

        if not isLastPriceChanged:
            return

        priceInfos = {}
        priceInfos[event.getContractNo()] = {
            "LastPrice": lv1Data[4],
            "TradeDate": tradeDate,
            "DateTimeStamp" : dateTimeStamp,
            "LastPriceSource": LastPriceFromQuote
        }
        self._calc.calcProfit([event.getContractNo()], priceInfos)

    #
    def _handleStopWinLose(self, event):
        #
        if not self._strategy.isRealTimeStatus():
            return

        data = event.getData()
        contractNo = event.getContractNo()
        lv1Data = data["Data"]
        dateTimeStamp = data["DateTimeStamp"]
        tradeDate = data["TradeDate"]
        isLastPriceChanged = data["IsLastPriceChanged"]
        if not isLastPriceChanged:
            return
        # 最新价
        lastPrice = lv1Data[4]
        lastOpenPos = self._calc.getLatestOpenOrder(contractNo)
        allPos = self._calc.getPositionInfo(contractNo)

        if not lastOpenPos or not allPos:
            return

        priceTick = self._dataModel.getPriceTick(contractNo)
        stopWinParams = self._config.getStopWinParams(contractNo)
        stopLoseParams = self._config.getStopLoseParams(contractNo)
        isStopWinTrigger=None; isStopLoseTrigger=None

        if stopWinParams:
            isStopWinTrigger = (lastPrice-lastOpenPos["OrderPrice"])>=stopWinParams["StopPoint"]*priceTick
        if stopLoseParams:
            isStopLoseTrigger = (lastOpenPos["OrderPrice"]-lastPrice)>=stopLoseParams["StopPoint"]*priceTick

        # 处理止盈
        if isStopWinTrigger:
            self.logger.info(f"{contractNo} 的即时行情触发了止盈, 触发价格:{lastPrice}")
        if isStopLoseTrigger:
            self.logger.info(f"{contractNo} 的即时行情触发了止损, 触发价格:{lastPrice}, TotalBuy: {allPos['TotalBuy']}, TotalSell: {allPos['TotalSell']}")
            # print(f"{contractNo} 的即时行情触发了止损, 触发价格:{lastPrice}, TotalBuy: {allPos['TotalBuy']}, TotalSell: {allPos['TotalSell']}")

        if isStopLoseTrigger:
            coverPosPriceLose = self.getCoverPosPrice(lv1Data, stopLoseParams["CoverPosOrderType"], stopLoseParams["AddPoint"], priceTick)
            if allPos["TotalBuy"] >= 1:
                self._dataModel.setSell(contractNo, allPos["TotalBuy"], coverPosPriceLose, dSell)
            elif allPos["TotalSell"] >= 1:
                self._dataModel.setBuyToCover(contractNo, allPos["TotalSell"], coverPosPriceLose, dBuy)
            # allPos = self._calc.getPositionInfo(contractNo)
            # print(f"after cover pos , TotalBuy: {allPos['TotalBuy']}, TotalSell: {allPos['TotalSell']}")
        elif isStopWinTrigger:
            coverPosPriceWin = self.getCoverPosPrice(lv1Data, stopWinParams["CoverPosOrderType"], stopWinParams["AddPoint"], priceTick)
            if allPos["TotalBuy"] >= 1:
                self._dataModel.setSell(contractNo, allPos["TotalBuy"], coverPosPriceWin, dSell)
            elif allPos["TotalSell"] >= 1:
                self._dataModel.setBuyToCover(contractNo, allPos["TotalSell"], coverPosPriceWin, dBuy)

    def getCoverPosPrice(self, lv1Data, coverPosOrderType, addPoint, priceTick, direction):
        # price 应该根据coverPosOrderType调整, todo
        price = lv1Data[4]
        # 根据超价点数买+ 卖-
        if direction==dBuy:
            return price+addPoint*priceTick
        elif direction==dSell:
            return price-addPoint*priceTick
        else:
            return None