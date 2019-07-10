import numpy as np
from capi.com_types import *
from .engine_model import *
import talib
import time, sys
import math
import pandas as pd
from .strategy_cfg_model import StrategyConfig
from .strategy_his_model import StrategyHisQuote
from .strategy_qte_model import StrategyQuote
from .strategy_trd_model import StrategyTrade
from .statistics_model import StatisticsModel
import copy

from engine.calc import CalcCenter
from datetime import datetime


class StrategyModel(object):
    def __init__(self, strategy):
        self._strategy = strategy
        self.logger = strategy.logger
        self._argsDict = strategy._argsDict

        self._strategyName = strategy.getStrategyName()
        self._signalName = self._strategyName + "_Signal"
        self._textName = self._strategyName + "_Text"
        self._plotedDict = {}

        # Notice：会抛异常
        self._cfgModel = StrategyConfig(self._argsDict)
        self._config = self._cfgModel
        # 回测计算
        self._calcCenter = CalcCenter(self.logger)

        self._qteModel = StrategyQuote(strategy, self._cfgModel)
        self._hisModel = StrategyHisQuote(strategy, self._cfgModel, self._calcCenter, self)
        self._trdModel = StrategyTrade(strategy, self._cfgModel)
        self._staModel = StatisticsModel(strategy, self._cfgModel)

    def setRunStatus(self, status):
        self._runStatus = status

    def getTradeModel(self):
        return self._trdModel

    def getConfigData(self):
        return self._cfgModel.getConfig()

    def getConfigTimer(self):
        return self._cfgModel.getTimerTrigger()

    def getConfigCycle(self):
        return self._cfgModel.getCycleTrigger()

    def getConfigModel(self):
        return self._cfgModel

    def getHisQuoteModel(self):
        return self._hisModel

    def getMonResult(self):
        return self._calcCenter.getMonResult()

    def getQuoteModel(self):
        return self._qteModel

    # +++++++++++++++++++++++内部接口++++++++++++++++++++++++++++
    def getCalcCenter(self):
        return self._calcCenter

    def initialize(self):
        '''加载完策略初始化函数之后再初始化'''
        self._hisModel.initialize()
        self._trdModel.initialize()

    def initializeCalc(self):
        contNo = self._cfgModel.getContract()[0]
        strategyParam = {
            "InitialFunds": float(self._cfgModel.getInitCapital()),  # 初始资金
            "StrategyName": self._strategy.getStrategyName(),  # 策略名称
            "StartTime": "2019-04-01",  # 回测开始时间
            "EndTime": "2019-04-17",  # 回测结束时间
            "Margin": self._cfgModel.getMarginValue() if not self._cfgModel.getMarginValue() else 0.08,  # 保证金
            "Slippage": self._cfgModel.getSlippage(),  # 滑点
            "OpenRatio": self._cfgModel.getOpenRatio(),
            "CloseRatio": self._cfgModel.getCloseRatio(),
            "OpenFixed": self._cfgModel.getOpenFixed(),
            "CloseFixed": self._cfgModel.getCloseFixed(),
            "CloseTodayRatio": self._cfgModel.getCloseTodayRatio(),
            "CloseTodayFixed": self._cfgModel.getCloseTodayFixed(),
            "KLineType": "M",  # todo
            "KLineSlice": 1,  # todo
            "TradeDot": self.getContractUnit(contNo),  # 每手乘数
            "PriceTick": self.getPriceScale(contNo),  # 最小变动价位
            "Limit": self._config.getLimit(),
        }
        self._calcCenter.initArgs(strategyParam)

    # ++++++++++++++++++++++策略接口++++++++++++++++++++++++++++++
    # //////////////////////历史行情接口//////////////////////////
    def runReport(self, context, handle_data):
        self._hisModel.runReport(context, handle_data)

    def runRealTime(self, context, handle_data, event):
        code = event.getEventCode()
        if code == ST_TRIGGER_FILL_DATA:
            self._hisModel.runFillData(context, handle_data, event)
        elif code == ST_TRIGGER_HIS_KLINE:
            self._hisModel.runVirtualReport(context, handle_data, event)
        else:
            self._hisModel.runRealTime(context, handle_data, event)

    # ///////////////////////即时行情接口//////////////////////////
    def reqExchange(self):
        self._qteModel.reqExchange()

    def reqCommodity(self):
        self._qteModel.reqCommodity()

    def reqContract(self):
        self._qteModel.reqContract()

    def reqUnderlayMap(self):
        self._qteModel.reqUnderlayMap()

    def subQuote(self):
        self._qteModel.subQuote()

    def subQuoteList(self, contNoList):
        self._qteModel.subQuoteList(contNoList)

    def unsubQuoteList(self, contNoList):
        # TODO: 退订即使行情时，是否需要删除已经得到的即时行情信息
        self._qteModel.unsubQuoteList(contNoList)

    def onExchange(self, event):
        self._qteModel.onExchange(event)

    def onCommodity(self, event):
        self._qteModel.onCommodity(event)

    def onContract(self, event):
        self._qteModel.onContract(event)

    def onUnderlayMap(self, event):
        self._qteModel.onUnderlayMap(event)

    def onExchangeStateNotice(self, event):
        self._qteModel.onExchangeStatus(event)

    def onQuoteRsp(self, event):
        self._qteModel.onQuoteRsp(event)

    def onQuoteNotice(self, event):
        self._qteModel.onQuoteNotice(event)

    def onDepthNotice(self, event):
        self._qteModel.onDepthNotice(event)

    # ///////////////////////交易数据接口/////////////////////////
    def reqTradeData(self):
        self._trdModel.reqTradeData()

    # ////////////////////////配置接口////////////////////////////
    def continueTrigger(self):
        return self._cfgModel.continues()

    # ++++++++++++++++++++++base api接口++++++++++++++++++++++++++
    # ////////////////////////K线函数/////////////////////////////
    def getKey(self, contNo, kLineType, kLineValue):
        # 空合约取默认展示的合约
        if contNo == "" or kLineType == '' or kLineValue == 0:
            return self._cfgModel.getDefaultKey()

        # if contNo not in 合约没有订阅
        if kLineType not in (EEQU_KLINE_TIMEDIVISION, EEQU_KLINE_TICK,
                             EEQU_KLINE_SECOND, EEQU_KLINE_MINUTE,
                             EEQU_KLINE_HOUR, EEQU_KLINE_DAY,
                             EEQU_KLINE_WEEK, EEQU_KLINE_MONTH,
                             EEQU_KLINE_YEAR):
            raise Exception("输入K线类型异常，请参阅枚举函数-周期类型枚举函数")
        if not isinstance(kLineValue, int) or kLineValue < 0:
            raise Exception("输入K线周期异常，请确保输入的K线周期是正整数")
        return (contNo, kLineType, kLineValue)

    def getBarOpenInt(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.getBarOpenInt(multiContKey)

    def getBarTradeDate(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.getBarTradeDate(multiContKey)

    def getBarCount(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.getBarCount(multiContKey)

    def getCurrentBar(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        curBar = self._hisModel.getCurBar(multiContKey)
        if not curBar:
            return None
        return curBar['KLineIndex']

    def getCurrentBarEntity(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        curBar = self._hisModel.getCurBar(multiContKey)
        return curBar

    def getBarStatus(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.getBarStatus(multiContKey)

    def isHistoryDataExist(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.isHistoryDataExist(multiContKey)

    def getBarDate(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.getBarDate(multiContKey)

    def getBarTime(self, contNo, kLineType, kLineValue):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.getBarTime(multiContKey)

    def getBarOpen(self, contractNo, kLineType, kLineValue):
        multiContKey = self.getKey(contractNo, kLineType, kLineValue)
        return self._hisModel.getBarOpen(multiContKey)

    def getBarClose(self, contractNo, kLineType, kLineValue):
        multiContKey = self.getKey(contractNo, kLineType, kLineValue)
        return self._hisModel.getBarClose(multiContKey)

    def getOpenD(self, daysAgo, contractNo):
        contNo = self._cfgModel.getBenchmark() if not contractNo else contractNo
        multiContKey = self.getKey(contNo, 'D', 1)
        return self._hisModel.getOpenD(daysAgo, multiContKey)

    def getCloseD(self, daysAgo, contractNo):
        contNo = self._cfgModel.getBenchmark() if not contractNo else contractNo
        multiContKey = self.getKey(contNo, 'D', 1)
        return self._hisModel.getCloseD(daysAgo, multiContKey)

    def getHighD(self, daysAgo, contractNo):
        contNo = self._cfgModel.getBenchmark() if not contractNo else contractNo
        multiContKey = self.getKey(contNo, 'D', 1)
        return self._hisModel.getHighD(daysAgo, multiContKey)

    def getLowD(self, daysAgo, contractNo):
        contNo = self._cfgModel.getBenchmark() if not contractNo else contractNo
        multiContKey = self.getKey(contNo, 'D', 1)
        return self._hisModel.getLowD(daysAgo, multiContKey)

    def getBarVol(self, contractNo, kLineType, kLineValue):
        multiContKey = self.getKey(contractNo, kLineType, kLineValue)
        return self._hisModel.getBarVol(multiContKey)

    def getBarHigh(self, contractNo, kLineType, kLineValue):
        multiContKey = self.getKey(contractNo, kLineType, kLineValue)
        return self._hisModel.getBarHigh(multiContKey)

    def getBarLow(self, contractNo, kLineType, kLineValue):
        multiContKey = self.getKey(contractNo, kLineType, kLineValue)
        return self._hisModel.getBarLow(multiContKey)

    def getHisData(self, dataType, kLineType, kLineValue, contractNo, maxLength):
        multiContKey = self.getKey(contractNo, kLineType, kLineValue)
        return self._hisModel.getHisData(dataType, multiContKey, maxLength)

    def getHisBarsInfo(self, contNo, kLineType, kLineValue, maxLength):
        multiContKey = self.getKey(contNo, kLineType, kLineValue)
        return self._hisModel.getHisBarsInfo(multiContKey, maxLength)

    # ////////////////////////即时行情////////////////////////////
    def getQUpdateTime(self, symbol):
        return self._qteModel.getQUpdateTime(symbol)

    def getQAskPrice(self, symbol, level):
        return self._qteModel.getQAskPrice(symbol, level)

    def getQAskPriceFlag(self, symbol):
        return self._qteModel.getQAskPriceFlag(symbol)

    def getQAskVol(self, symbol, level):
        return self._qteModel.getQAskVol(symbol, level)

    def getQAvgPrice(self, symbol):
        return self._qteModel.getQAvgPrice(symbol)

    def getQBidPrice(self, symbol, level):
        return self._qteModel.getQBidPrice(symbol, level)

    def getQBidPriceFlag(self, symbol):
        return self._qteModel.getQBidPriceFlag(symbol)

    def getQBidVol(self, symbol, level):
        return self._qteModel.getQBidVol(symbol, level)

    def getQClose(self, symbol):
        return self._qteModel.getQClose(symbol)

    def getQHigh(self, symbol):
        return self._qteModel.getQHigh(symbol)

    def getQHisHigh(self, symbol):
        return self._qteModel.getQHisHigh(symbol)

    def getQHisLow(self, symbol):
        return self._qteModel.getQHisLow(symbol)

    def getQInsideVol(self, symbol):
        return self._qteModel.getQInsideVol(symbol)

    def getQLast(self, symbol):
        return self._qteModel.getQLast(symbol)

    def getQLastDate(self, symbol):
        symbol = self._config.getBenchmark() if not symbol else symbol
        key = None
        for keyTuple in self._hisModel._kLineNoticeData.keys():
            if keyTuple[0] == symbol and keyTuple[1] == 'T':
                key = keyTuple
                break
        if not key:
            raise Exception(
                "在使用Q_LastTime方法时，请确保已经在设置界面或者在策略代码中添加了SetBarInterval('%s', 'T', 1)为合约%s订阅了Tick行情！" % (symbol, symbol))
        tickInfo = self._hisModel.getLastStoredKLine(key)[0]
        dateTimeStamp = tickInfo['DateTimeStamp']
        return int(dateTimeStamp) // 1000000000

    def getQLastTime(self, symbol):
        symbol = self._config.getBenchmark() if not symbol else symbol
        key = None
        for keyTuple in self._hisModel._kLineNoticeData.keys():
            if keyTuple[0] == symbol and keyTuple[1] == 'T':
                key = keyTuple
                break
        if not key:
            raise Exception(
                "在使用Q_LastTime方法时，请确保已经在设置界面或者在策略代码中添加了SetBarInterval('%s', 'T', 1)为合约%s订阅了Tick行情！" % (symbol, symbol))
        tickInfo = self._hisModel.getLastStoredKLine(key)[0]
        dateTimeStamp = tickInfo['DateTimeStamp']
        return float(int(dateTimeStamp) % 1000000000) / 1000000000

    def getQLastVol(self, symbol):
        return self._qteModel.getQLastVol(symbol)

    def getQLow(self, symbol):
        return self._qteModel.getQLow(symbol)

    def getQLowLimit(self, symbol):
        return self._qteModel.getQLowLimit(symbol)

    def getQOpen(self, symbol):
        return self._qteModel.getQOpen(symbol)

    def getQOpenInt(self, symbol):
        return self._qteModel.getQOpenInt(symbol)

    def getQOpenIntFlag(self, symbol):
        return self._qteModel.getQOpenIntFlag(symbol)

    def getQOutsideVol(self, symbol):
        return self._qteModel.getQOutsideVol(symbol)

    def getQPreOpenInt(self, symbol):
        return self._qteModel.getQPreOpenInt(symbol)

    def getQPreSettlePrice(self, symbol):
        return self._qteModel.getQPreSettlePrice(symbol)

    def getQPriceChg(self, symbol):
        return self._qteModel.getQPriceChg(symbol)

    def getQPriceChgRadio(self, symbol):
        return self._qteModel.getQPriceChgRadio(symbol)

    def getQTodayEntryVol(self, symbol):
        return self._qteModel.getQTodayEntryVol(symbol)

    def getQTodayExitVol(self, symbol):
        return self._qteModel.getQTodayExitVol(symbol)

    def getQTotalVol(self, symbol):
        return self._qteModel.getQTotalVol(symbol)

    def getQTurnOver(self, symbol):
        return self._qteModel.getQTurnOver(symbol)

    def getQUpperLimit(self, symbol):
        return self._qteModel.getQUpperLimit(symbol)

    def getQuoteDataExist(self, symbol):
        return self._qteModel.getQuoteDataExist(symbol)

    # ////////////////////////策略函数////////////////////////////
    def setBuy(self, userNo, contractNo, share, price, needCover=True):
        contNo = contractNo if contractNo else self._cfgModel.getBenchmark()

        underlayContNo = self._qteModel.getUnderlayContractNo(contNo)
        if len(underlayContNo) > 0:
            contNo = underlayContNo

        # 非K线触发的策略，不使用Bar
        curBar = None
        # 计算考虑滑点损耗后的价格
        if not self._cfgModel.isActualRun():
            price = self._calcCenter.calcOrderPrice(contNo, dBuy, price)

        # 对于开仓，需要平掉反向持仓
        qty = self._calcCenter.needCover(userNo, contNo, dBuy, share, price)
        if qty > 0 and needCover:
            eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtGFD, dBuy, oCover, hSpeculate, price, qty, curBar)
            if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtGFD, dBuy, oOpen, hSpeculate, price, share, curBar)
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setBuyToCover(self, userNo, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()

        underlayContNo = self._qteModel.getUnderlayContractNo(contNo)
        if len(underlayContNo) > 0:
            contNo = underlayContNo

        curBar = None

        # 计算考虑滑点损耗后的价格
        if not self._cfgModel.isActualRun():
            price = self._calcCenter.calcOrderPrice(contNo, dBuy, price)

        # 交易计算、生成回测报告
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtGFD, dBuy, oCover, hSpeculate, price, share, curBar)
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setSell(self, userNo, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()

        underlayContNo = self._qteModel.getUnderlayContractNo(contNo)
        if len(underlayContNo) > 0:
            contNo = underlayContNo

        curBar = None

        # 计算考虑滑点损耗后的价格
        if not self._cfgModel.isActualRun():
            price = self._calcCenter.calcOrderPrice(contNo, dSell, price)

        # 交易计算、生成回测报告
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtGFD, dSell, oCover, hSpeculate, price, share, curBar)
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setSellShort(self, userNo, contractNo, share, price, needCover=True):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()

        underlayContNo = self._qteModel.getUnderlayContractNo(contNo)
        if len(underlayContNo) > 0:
            contNo = underlayContNo

        curBar = None

        # 计算考虑滑点损耗后的价格
        if not self._cfgModel.isActualRun():
            price = self._calcCenter.calcOrderPrice(contNo, dSell, price)

        qty = self._calcCenter.needCover(userNo, contNo, dSell, share, price)
        if qty > 0 and needCover:
            eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtGFD, dSell, oCover, hSpeculate, price, qty,
                                           curBar)
            if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

        # 交易计算、生成回测报告
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtGFD, dSell, oOpen, hSpeculate, price, share, curBar)
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def sendFlushEvent(self):
        flushEvent = Event({
            "EventCode": EV_ST2EG_UPDATE_STRATEGYDATA,
            "StrategyId": self._strategy.getStrategyId(),
        })
        self._strategy.sendEvent2Engine(flushEvent)

    def sendSignalEvent(self, signalName, contNo, direct, offset, price, share, curBar):
        if not curBar:
            return

        data = [{
            'KLineIndex': curBar['KLineIndex'],
            'ContractNo': contNo,
            'Direct': direct,
            'Offset': offset,
            'Price': price,
            'Qty': share,
        }]
        #
        eventCode = EV_ST2EG_UPDATE_KLINESIGNAL if self._strategy.isRealTimeStatus() else EV_ST2EG_NOTICE_KLINESIGNAL
        signalNoticeEvent = Event({
            "EventCode": eventCode,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": {
                'SeriesName': signalName,
                'Count': len(data),
                'Data': data,
            }
        })
        self._strategy.sendEvent2Engine(signalNoticeEvent)

    def setStartTrade(self):
        self._cfgModel.setPending(False)

    def setStopTrade(self):
        self._cfgModel.setPending(True)

    def isTradeAllowed(self):
        if self._cfgModel.isActualRun() and self._strategy.isRealTimeStatus() and not self._cfgModel.getPending():
            return True
        return False

    # ////////////////////////设置函数////////////////////////////
    def getConfig(self):
        return self._cfgModel._metaData

    def addUserNo(self, userNo):
        self._cfgModel.addUserNo(userNo)

    def setBarInterval(self, contractNo, barType, barInterval, sampleConfig, trigger=True):
        self._cfgModel.setBarInterval(contractNo, barType, barInterval, sampleConfig, trigger)

    def setSample(self, sampleType, sampleValue):
        return self._cfgModel.setSample(sampleType, sampleValue)

    def setInitCapital(self, capital, userNo):
        initFund = capital if capital else 1000000
        self._cfgModel.setInitCapital(initFund, userNo)
        return 0

    def setMargin(self, type, value, contNo):
        if type not in (0, 1):
            return -1

        if type == 0:
            # 按比例
            if not value or value == 0:
                return self._cfgModel.setMargin(EEQU_FEE_TYPE_RATIO, 0.08, contNo)

            if value > 1:
                return -1
            return self._cfgModel.setMargin(EEQU_FEE_TYPE_FIXED, value, contNo)

        if type == 1:
            # 按固定值
            if not value or value <= 0:
                return -1
            return self._cfgModel.setMargin(EEQU_FEE_TYPE_FIXED, value, contNo)

    def setTradeFee(self, type, feeType, feeValue, contNo):
        if type not in ('A', 'O', 'C', 'T'):
            return -1

        if feeType not in (1, 2):
            return -1

        feeType = EEQU_FEE_TYPE_RATIO if feeType == 1 else EEQU_FEE_TYPE_FIXED
        return self._cfgModel.setTradeFee(type, feeType, feeValue, contNo)

    def setActual(self):
        return self._cfgModel.setActual()

    def setOrderWay(self, type):
        if type not in (1, 2):
            return -1
        self._cfgModel.setOrderWay(type)
        return 0

    def setTradeDirection(self, tradeDirection):
        if tradeDirection not in (0, 1, 2):
            return -1

        self._cfgModel.setTradeDirection(tradeDirection)
        return 0

    def setMinTradeQuantity(self, tradeQty):
        if tradeQty <= 0 or tradeQty > MAXSINGLETRADESIZE:
            return -1

        self._cfgModel.setMinQty(tradeQty)
        return 0

    def setHedge(self, hedge):
        if hedge not in ('T', 'B', 'S', 'M'):
            return -1

        self._cfgModel.setHedge(hedge)
        return 0

    def setSlippage(self, slippage):
        self._cfgModel.setSlippage(slippage)
        return 0

    def setTriggerMode(self, type, value):
        return self._cfgModel.setTrigger(type, value)

    def setWinPoint(self, winPoint, nPriceType, nAddTick, contNo):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()
        return self._cfgModel.setWinPoint(winPoint, nPriceType, nAddTick, contNo)

    def setStopPoint(self, stopPoint, nPriceType, nAddTick, contNo):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()
        return self._cfgModel.setStopPoint(stopPoint, nPriceType, nAddTick, contNo)

    def subscribeContract(self, contNo):
        contList = [contNo]
        self._cfgModel.updateSubQuoteContract(contList)
        return self.subQuoteList(contList)

    def unsubscribeContract(self, contNo):
        contList = [contNo]
        self._cfgModel.updateUnsubQuoteContract(contList)
        return self.unsubQuoteList(contList)

    # ///////////////////////账户函数///////////////////////////
    def getAccountId(self):
        return self._trdModel.getAccountId()

    def getAllPositionSymbol(self):
        return self._trdModel.getAllPositionSymbol()

    def getCost(self):
        return self._trdModel.getCost()

    def getCurrentEquity(self):
        return self._trdModel.getCurrentEquity()

    def getFreeMargin(self):
        return self._trdModel.getFreeMargin()

    def getAMargin(self):
        return self._trdModel.getAMargin()

    def getProfitLoss(self):
        return self._trdModel.getProfitLoss()

    def getCoverProfit(self):
        return self._trdModel.getCoverProfit()

    def getTotalFreeze(self):
        return self._trdModel.getTotalFreeze()

    def getBuyAvgPrice(self, contNo):
        return self._trdModel.getBuyAvgPrice(contNo)

    def getBuyPosition(self, contNo):
        return self._trdModel.getBuyPosition(contNo)

    def getBuyPositionCanCover(self, contNo):
        return self._trdModel.getBuyPositionCanCover(contNo)

    def getBuyProfitLoss(self, contNo):
        return self._trdModel.getBuyProfitLoss(contNo)

    def getSellAvgPrice(self, contNo):
        return self._trdModel.getSellAvgPrice(contNo)

    def getSellPosition(self, contNo):
        return self._trdModel.getSellPosition(contNo)

    def getSellPositionCanCover(self, contNo):
        return self._trdModel.getSellPositionCanCover(contNo)

    def getSellProfitLoss(self, contNo):
        return self._trdModel.getSellProfitLoss(contNo)

    def getTotalAvgPrice(self, contNo):
        return self._trdModel.getTotalAvgPrice(contNo)

    def getTotalPosition(self, contNo):
        return self._trdModel.getTotalPosition(contNo)

    def getTotalProfitLoss(self, contNo):
        return self._trdModel.getTotalProfitLoss(contNo)

    def getTodayBuyPosition(self, contNo):
        return self._trdModel.getTodayBuyPosition(contNo)

    def getTodaySellPosition(self, contNo):
        return self._trdModel.getTodaySellPosition(contNo)

    def getOrderBuyOrSell(self, eSession):
        return self._trdModel.getOrderBuyOrSell(eSession)

    def getOrderEntryOrExit(self, eSession):
        return self._trdModel.getOrderEntryOrExit(eSession)

    def getOrderFilledLot(self, eSession):
        return self._trdModel.getOrderFilledLot(eSession)

    def getOrderFilledPrice(self, eSession):
        return self._trdModel.getOrderFilledPrice(eSession)

    def getOrderLot(self, eSession):
        return self._trdModel.getOrderLot(eSession)

    def getOrderPrice(self, eSession):
        return self._trdModel.getOrderPrice(eSession)

    def getOrderStatus(self, eSession):
        return self._trdModel.getOrderStatus(eSession)

    def getOrderTime(self, eSession):
        return self._trdModel.getOrderTime(eSession)

    def getFirstOrderNo(self, contNo1, contNo2):
        return self._trdModel.getFirstOrderNo(contNo1, contNo2)

    def getNextOrderNo(self, orderId, contNo1, contNo2):
        return self._trdModel.getNextOrderNo(orderId, contNo1, contNo2)

    def getLastOrderNo(self, contNo1, contNo2):
        return self._trdModel.getLastOrderNo(contNo1, contNo2)

    def getFirstQueueOrderNo(self, contNo1, contNo2=''):
        return self._trdModel.getFirstQueueOrderNo(contNo1, contNo2)

    def getNextQueueOrderNo(self, orderId, contNo1, contNo2=''):
        return self._trdModel.getNextQueueOrderNo(orderId, contNo1, contNo2)

    def getAllQueueOrderNo(self, contNo):
        orderIdList = []
        orderId = self.getFirstQueueOrderNo(contNo)
        if orderId != -1:
            orderIdList.append(orderId)
        while (orderId != -1):
            orderId = self.getNextQueueOrderNo(orderId, contNo)
            if orderId != -1:
                orderIdList.append(orderId)
        return orderIdList

    def getALatestFilledTime(self, contNo):
        return self._trdModel.getALatestFilledTime(contNo)

    def getOrderContractNo(self, orderId):
        return self._trdModel.getOrderContractNo(orderId)

    def deleteOrder(self, eSession):
        return self._trdModel.deleteOrder(eSession)

    def buySellOrder(self, userNo, contNo, orderType, validType, orderDirct, \
                     entryOrExit, hedge, orderPrice, orderQty, curBar, signal=True):
        '''
            1. buySell下单，经过calc模块，会判断虚拟资金，会产生平仓单
            2. 如果支持K线触发，会产生下单信号
            3. 对于即时行情和委托触发，在日志中分析下单信号
        '''
        triggerInfo = self._strategy.getCurTriggerSourceInfo()
        dateTime = triggerInfo["DateTimeStamp"]
        tradeDate = triggerInfo["TradeDate"]
        triggerType = triggerInfo["TriggerType"]
        triggerData = triggerInfo["TriggerData"]

        curBarIndex = None
        curBar = None
        key = self._config.getKLineShowInfoSimple()
        curShowBar = self.getHisQuoteModel().getCurBar(key)
        if curShowBar:
            curBar = copy.deepcopy(curShowBar)
            curBarIndex = curBar["KLineIndex"]

        userNo = self._cfgModel.getUserNo() if not userNo else userNo
        if not userNo:
            userNo = "Default"

        orderParam = {
            "UserNo": userNo,  # 账户编号
            "OrderType": orderType,  # 定单类型
            "ValidType": validType,  # 有效类型
            "ValidTime": '0',  # 有效日期时间(GTD情况下使用)
            "Cont": contNo,  # 合约
            "Direct": orderDirct,  # 买卖方向：买、卖
            "Offset": entryOrExit,  # 开仓、平仓、平今
            "Hedge": hedge,  # 投机套保
            "OrderPrice": orderPrice,  # 委托价格 或 期权应价买入价格
            "OrderQty": orderQty,  # 委托数量 或 期权应价数量
            "DateTimeStamp": dateTime,  # 时间戳（基准合约）
            "TradeDate": tradeDate,  # 交易日（基准合约）
            "TriggerType": triggerType,
            "CurBar": curBar,
            "CurBarIndex": curBarIndex,  #
            "StrategyId": self._strategy.getStrategyId(),
            "StrategyName": self._strategy.getStrategyName(),
            "StrategyStage": self._strategy.getStatus()
        }

        # if entryOrExit in (oCover, oCoverT):
        if entryOrExit in (oCover, oCoverT):
            isVaildOrder = self._calcCenter.coverJudge(orderParam)
            if isVaildOrder < 0:
                return ""

        canAdded = self._calcCenter.addOrder(orderParam)
        if canAdded < 1:
            return ""

        '''buy/sell 信号，
        历史阶段：一定没有委托
        实时数据：不一定有委托发
        '''
        curBar = self.getHisQuoteModel().getCurBar(self._config.getKLineShowInfoSimple())
        if self._config.hasKLineTrigger() and curBar:
            self.sendSignalEvent(self._signalName, contNo, orderDirct, entryOrExit, orderPrice, orderQty, curBar)

        retCode, eSessionId = self.sendOrder(userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge,
                                             orderPrice, orderQty)
        return eSessionId if retCode == 0 else ""

    def sendOrder(self, userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty, \
                  triggerType=stNone, triggerMode=tmNone, triggerCondition=tcNone, triggerPrice=0, aFunc=False):
        '''A账户下单函数，不经过calc模块，直接发单'''
        if not userNo:
            userNo = self._cfgModel.getUserNo()

        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        # 是否暂停实盘下单
        if self._cfgModel.getPending():
            self.logger.warn(f"请调用StartTrade方法开启实盘下单功能")
            return -5, "请调用StartTrade方法开启实盘下单功能"

        # 发送下单信号,K线触发、即时行情触发
        # 未选择实盘运行
        if not self._cfgModel.isActualRun():
            #self.logger.warn(f"未选择实盘运行，请在设置界面勾选'实盘运行'，或者在策略代码中调用SetActual()")
            return -1, '未选择实盘运行，请在设置界面勾选"实盘运行"，或者在策略代码中调用SetActual()方法选择实盘运行'

        if not self._strategy.isRealTimeStatus():
            #self.logger.warn(f"策略当前状态不是实盘运行状态， 不会产生实盘订单")
            return -2, "策略当前状态不是实盘运行状态， 不会产生实盘订单"

        # 账户错误
        if not userNo or userNo == 'Default':
            #self.logger.warn(f"未指定下单账户信息")
            return -3, "未指定下单账户信息"

        # 指定的用户未登录
        if not self._trdModel.getSign(userNo):
            #self.logger.warn(f"输入的账户没有在极星客户端登录")
            return -4, "输入的账户没有在极星客户端登录"

        underlayContNo = self._qteModel.getUnderlayContractNo(contNo)
        if len(underlayContNo) > 0:
            contNo = underlayContNo

        eId = str(self._strategy.getStrategyId()) + '-' + str(self._strategy.getESessionId())
        # 上期所特殊处理
        if "SHFE|" in contNo and entryOrExit == oCover:
            if orderDirct == dBuy:
                positionInfo = self._trdModel.getUserModel(userNo).getPositionInfo(contNo, dSell)
            elif orderDirct == dSell:
                positionInfo = self._trdModel.getUserModel(userNo).getPositionInfo(contNo, dBuy)

            if positionInfo is None:
                self.logger.warn(f"持仓查询没有查询到对应方向的持仓, 无法平仓")
                return -6, "持仓查询没有查询到对应方向的持仓, 无法平仓"
            entryOrExitToday = oCoverT
            orderQtyToday = positionInfo["TodayPos"]
            aOrder = {
                'UserNo': userNo,
                'Sign': self._trdModel.getSign(userNo),
                'Cont': contNo,
                'OrderType': orderType,
                'ValidType': validType,
                'ValidTime': '0',
                'Direct': orderDirct,
                'Offset': entryOrExitToday,
                'Hedge': hedge,
                'OrderPrice': orderPrice,
                'TriggerPrice': 0,
                'TriggerMode': tmNone,
                'TriggerCondition': tcNone,
                'OrderQty': orderQtyToday,
                'StrategyType': stNone,
                'Remark': '',
                'AddOneIsValid': tsDay,
            }
            self.sendActualOrder2Engine(aOrder, eId, self._strategy.getStrategyId(), aFunc)
            if orderQty > positionInfo["TodayPos"]:
                orderQty = orderQty - positionInfo["TodayPos"]
                entryOrExit = oCover
            else:
                self._strategy.setESessionId(self._strategy.getESessionId() + 1)
                self._strategy.updateLocalOrder(eId, aOrder)
                # 新的eId
                eId = str(self._strategy.getStrategyId()) + '-' + str(self._strategy.getESessionId())
                return 0, eId

        # 发送定单到实盘
        aOrder = {
            'UserNo': userNo,
            'Sign': self._trdModel.getSign(userNo),
            'Cont': contNo,
            'OrderType': orderType,
            'ValidType': validType,
            'ValidTime': '0',
            'Direct': orderDirct,
            'Offset': entryOrExit,
            'Hedge': hedge,
            'OrderPrice': orderPrice,
            'TriggerPrice': triggerPrice,
            'TriggerMode': triggerMode,
            'TriggerCondition': triggerCondition,
            'OrderQty': orderQty,
            'StrategyType': triggerType,
            'Remark': '',
            'AddOneIsValid': tsDay,
        }

        self.sendActualOrder2Engine(aOrder, eId, self._strategy.getStrategyId(), aFunc)
        # self.logger.trade_info(self._strategy.getStrategyId(), aOrder)
        # 更新策略的订单信息
        self._strategy.setESessionId(self._strategy.getESessionId() + 1)
        self._strategy.updateLocalOrder(eId, aOrder)
        return 0, eId

    # afunc表明是由A函数调用的，还是buy/sell调用的
    def sendActualOrder2Engine(self, aOrder, eId, strategyId, aFunc):
        if int(aOrder["OrderQty"] + 0.5) <= 0:
            return
        aOrder["OrderQty"] = int(aOrder["OrderQty"] + 0.5)
        aOrderEvent = Event({
            "EventCode": EV_ST2EG_ACTUAL_ORDER,
            "StrategyId": strategyId,
            "Data": aOrder,
            "ESessionId": eId,
        })
        self._strategy.sendEvent2Engine(aOrderEvent)
        '''A函数 发送实盘信号'''
        curBar = self.getHisQuoteModel().getCurBar(self._config.getKLineShowInfoSimple())
        if aFunc and self._config.hasKLineTrigger() and curBar:
            self.logger.debug(f"实盘信号已经发送，k线时间戳：{curBar['DateTimeStamp']}")
            self.sendSignalEvent(self._signalName, aOrder["Cont"], aOrder["Direct"], aOrder["Offset"],
                                 aOrder["OrderPrice"], aOrder["OrderQty"], curBar)
        self.logger.trade_info(f"发送实盘订单，策略Id:{strategyId}, 本地订单号：{eId}, 订单数据：{repr(aOrder)}")

    def getAOrderNo(self, eId):
        if not (isinstance(eId, str) and '-' in eId):
            return ('', '')

        orderId = self._strategy.getOrderId(eId)
        if not orderId:
            orderId = ''
        orderNo = self._strategy.getOrderNo(eId)
        if not orderNo:
            orderNo = ''
        return orderId, orderNo

    def deleteAllOrders(self, contNo):
        orderList = self.getAllQueueOrderNo(contNo)
        if len(orderList) == 0:
            return True

        for orderId in orderList:
            self._trdModel.deleteOrderByOrderId(orderId)

        return True

    # ///////////////////////枚举函数///////////////////////////
    def getEnumBuy(self):
        return dBuy

    def getEnumSell(self):
        return dSell

    def getEnumEntry(self):
        return oOpen

    def getEnumExit(self):
        return oCover

    def getEnumExitToday(self):
        return oCoverT

    def getEnumEntryExitIgnore(self):
        return oNone

    def getEnumSended(self):
        return osSended

    def getEnumAccept(self):
        return osAccept

    def getEnumTriggering(self):
        return osTriggering

    def getEnumActive(self):
        return osActive

    def getEnumQueued(self):
        return osQueued

    def getEnumFillPart(self):
        return osFillPart

    def getEnumFilled(self):
        return osFilled

    def getEnumCanceling(self):
        return osCanceling

    def getEnumModifying(self):
        return osModifying

    def getEnumCanceled(self):
        return osCanceled

    def getEnumPartCanceled(self):
        return osPartCanceled

    def getEnumFail(self):
        return osFail

    def getEnumSuspended(self):
        return osSuspended

    def getEnumApply(self):
        return osApply

    def getEnumPeriodTick(self):
        return EEQU_KLINE_TICK

    def getEnumPeriodDyna(self):
        return EEQU_KLINE_TIMEDIVISION

    def getEnumPeriodSecond(self):
        return EEQU_KLINE_TICK

    def getEnumPeriodMin(self):
        return EEQU_KLINE_MINUTE

    def getEnumPeriodHour(self):
        return EEQU_KLINE_HOUR

    def getEnumPeriodDay(self):
        return EEQU_KLINE_DAY

    def getEnumPeriodWeek(self):
        return EEQU_KLINE_WEEK

    def getEnumPeriodMonth(self):
        return EEQU_KLINE_MONTH

    def getEnumPeriodYear(self):
        return EEQU_KLINE_YEAR

    def getEnumPeriodDayX(self):
        return EEQU_KLINE_DayX

    def getEnumOrderMarket(self):
        return otMarket

    def getEnumOrderLimit(self):
        return otLimit

    def getEnumOrderMarketStop(self):
        return otMarketStop

    def getEnumOrderLimitStop(self):
        return otLimitStop

    def getEnumOrderExecute(self):
        return otExecute

    def getEnumOrderAbandon(self):
        return otAbandon

    def getEnumOrderEnquiry(self):
        return otEnquiry

    def getEnumOrderOffer(self):
        return otOffer

    def getEnumOrderIceberg(self):
        return otIceberg

    def getEnumOrderGhost(self):
        return otGhost

    def getEnumOrderSwap(self):
        return otSwap

    def getEnumOrderSpreadApply(self):
        return otSpreadApply

    def getEnumOrderHedgApply(self):
        return otHedgApply

    def getEnumOrderOptionAutoClose(self):
        return otOptionAutoClose

    def getEnumOrderFutureAutoClose(self):
        return otFutureAutoClose

    def getEnumOrderMarketOptionKeep(self):
        return otMarketOptionKeep

    def getEnumGFD(self):
        return vtGFD

    def getEnumGTC(self):
        return vtGTC

    def getEnumGTD(self):
        return vtGTD

    def getEnumIOC(self):
        return vtIOC

    def getEnumFOK(self):
        return vtFOK

    def getEnumSpeculate(self):
        return hSpeculate

    def getEnumHedge(self):
        return hHedge

    def getEnumSpread(self):
        return hSpread

    def getEnumMarket(self):
        return hMarket

    def getRed(self):
        return 0xFF0000

    def getGreen(self):
        return 0x00AA00

    def getBlue(self):
        return 0x0000FF

    def getYellow(self):
        return 0xFFFF00

    def getPurple(self):
        return 0x9900FF

    def getGray(self):
        return 0x999999

    def getBrown(self):
        return 0x996600

    def getEnumClose(self):
        return BarDataClose

    def getEnumOpen(self):
        return BarDataOpen

    def getEnumHigh(self):
        return BarDataHigh

    def getEnumLow(self):
        return BarDataLow

    def getEnumMedian(self):
        return BarDataMedian

    def getEnumTypical(self):
        return BarDataTypical

    def getEnumWeighted(self):
        return BarDataWeighted

    def getEnumVol(self):
        return BarDataVol

    def getEnumOpi(self):
        return BarDataOpi

    def getEnumTime(self):
        return BarDataTime

    # ///////////////////////其他函数///////////////////////////
    def _addSeries(self, name, value, color, main, axis, type):
        addSeriesEvent = Event({
            "EventCode": EV_ST2EG_ADD_KLINESERIES,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": {
                'ItemName': name,
                'Type': type,
                'Color': color,
                'Thick': 1,
                'OwnAxis': axis,
                'Param': [],
                'ParamNum': 0,
                'Groupid': 0,
                'GroupName': name,
                'Main': main,
            }
        })

        self._strategy.sendEvent2Engine(addSeriesEvent)

    def _plotNumeric(self, name, value, color, main, axis, type, barsback, data):
        if name not in self._plotedDict:
            self._addSeries(name, value, color, main, axis, type)
            self._plotedDict[name] = (name, value, color, main, axis, type, barsback)

        if self._strategy.isRealTimeStatus():
            eventCode = EV_ST2EG_UPDATE_KLINESERIES
        else:
            eventCode = EV_ST2EG_NOTICE_KLINESERIES
        serialEvent = Event({
            "EventCode": eventCode,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": {
                "SeriesName": name,
                "SeriesType": type,
                "IsMain": main,
                "Count": len(data),
                "Data": data
            }
        })
        self._strategy.sendEvent2Engine(serialEvent)

    def setPlotText(self, value, text, color, main, barsback):
        main = '0' if main else '1'
        curBar = self._hisModel.getCurBar()

        klineIndex = curBar['KLineIndex'] - barsback
        if klineIndex <= 0:
            return

        data = [{
            'KLineIndex': klineIndex,
            'Value': value,
            'Text': text
        }]

        self._plotNumeric(self._textName, value, color, main, EEQU_ISNOT_AXIS, EEQU_TEXT, barsback, data)

    def setUnPlotText(self, main, barsback):
        main = '0' if main else '1'
        curBar = self._hisModel.getCurBar()

        klineIndex = curBar['KLineIndex'] - barsback
        if klineIndex <= 0:
            return

        data = [{
            'KLineIndex': klineIndex,
            'Value': np.nan,
            'Text': ""
        }]

        self._plotNumeric(self._textName, np.nan, 0, main, EEQU_ISNOT_AXIS, EEQU_TEXT, barsback, data)

    def setPlotIcon(self, value, icon, main, barsback):
        main = '0' if main else '1'
        curBar = self._hisModel.getCurBar()

        klineIndex = curBar['KLineIndex'] - barsback
        if klineIndex <= 0:
            return

        data = [{
            'KLineIndex': klineIndex,
            'Value': value,
            'Icon': icon
        }]

        self._plotNumeric(self._strategyName, value, 0, main, EEQU_ISNOT_AXIS, EEQU_ICON, barsback, data)

    def setUnPlotIcon(self, main, barsback):
        return self.setPlotIcon(np.nan, 0, main, barsback)

    def setPlotDot(self, name, value, icon, color, main, barsback):
        main = '0' if main else '1'
        curBar = self._hisModel.getCurBar()

        klineIndex = curBar['KLineIndex'] - barsback
        if klineIndex <= 0:
            return

        data = [{
            'KLineIndex': klineIndex,
            'Value': value,
            'Icon': icon
        }]

        self._plotNumeric(name, value, color, main, EEQU_ISNOT_AXIS, EEQU_DOT, barsback, data)

    def setUnPlotDot(self, name, main, barsback):
        return self.setPlotDot(name, np.nan, 0, 0, main, barsback)

    def setPlotBar(self, name, vol1, vol2, color, main, filled, barsback):
        main = '0' if main else '1'
        filled = 1 if filled else 0
        curBar = self._hisModel.getCurBar()
        klineIndex = curBar['KLineIndex'] - barsback

        if klineIndex <= 0:
            return

        data = [{
            'KLineIndex': klineIndex,
            'Value': vol1,
            'ClrBar': color,
            'BarValue': vol2,
            'Filled': filled
        }]

        self._plotNumeric(name, 0, color, main, EEQU_ISNOT_AXIS, EEQU_BAR, barsback, data)

    def setUnPlotBar(self, name, main, barsback):
        return self.setPlotBar(name, np.nan, np.nan, 0, main, True, barsback)

    def setPlotNumeric(self, name, value, color, main, axis, type, barsback):
        main = '0' if main else '1'
        axis = '0' if axis else '1'

        curBar = self._hisModel.getCurBar()

        klineIndex = curBar['KLineIndex'] - barsback
        if klineIndex <= 0:
            return

        data = [{
            'KLineIndex': klineIndex,
            'Value': value
        }]
        self._plotNumeric(name, value, color, main, axis, type, barsback, data)

    def setUnPlotNumeric(self, name, main, barsback):
        return self.setPlotNumeric(name, np.nan, 0, main, EEQU_ISNOT_AXIS, 1, barsback)

    def setPlotVertLine(self, color, main, axis, barsback):
        main = '0' if main else '1'
        axis = '0' if axis else '1'

        curBar = self._hisModel.getCurBar()
        klineIndex = curBar['KLineIndex'] - barsback

        if klineIndex <= 0:
            return

        value = curBar['LastPrice']
        data = [{
            'KLineIndex': klineIndex,
            'Value': value,
            'ClrK': color
        }]

        self._plotNumeric(self._strategyName, value, color, main, axis, EEQU_VERTLINE, barsback, data)

    def setUnPlotVertLine(self, main, barsback):
        main = '0' if main else '1'

        curBar = self._hisModel.getCurBar()
        klineIndex = curBar['KLineIndex'] - barsback

        if klineIndex <= 0:
            return

        value = curBar['LastPrice']
        data = [{
            'KLineIndex': klineIndex,
            'Value': np.nan,
            'ClrK': 0
        }]

        self._plotNumeric(self._strategyName, np.nan, 0, main, EEQU_ISNOT_AXIS, EEQU_VERTLINE, barsback, data)

    def setPlotPartLine(self, name, index1, price1, count, price2, color, main, axis, width):
        main = '0' if main else '1'
        axis = '0' if axis else '1'

        if index1 <= 0 or count <= 0:
            return

        data = [{
            'KLineIndex': index1,
            'Value': price1,
            'Idx2': count,
            'LineValue': price2,
            'ClrLine': color,
            'LinWid': width
        }]

        self._plotNumeric(name, 0, color, main, axis, EEQU_PARTLINE, 0, data)

    def setUnPlotPartLine(self, name, index1, count, main):
        main = '0' if main else '1'

        if index1 <= 0 or count <= 0:
            return

        data = [{
            'KLineIndex': index1,
            'Value': np.nan,
            'Idx2': count,
            'LineValue': np.nan,
            'ClrLine': 0,
            'LinWid': 1
        }]

        self._plotNumeric(name, np.nan, 0, main, EEQU_ISNOT_AXIS, EEQU_PARTLINE, 0, data)

    def setPlotStickLine(self, name, price1, price2, color, main, axis, barsback):
        main = '0' if main else '1'
        axis = '0' if axis else '1'

        curBar = self._hisModel.getCurBar()
        klineIndex = curBar['KLineIndex'] - barsback

        if klineIndex <= 0:
            return

        data = [{
            'KLineIndex': klineIndex,
            'Value': price1,
            'StickValue': price2,
            'ClrStick': color
        }]

        self._plotNumeric(name, 0, color, main, axis, EEQU_STICKLINE, barsback, data)

    def setUnPlotStickLine(self, name, main, barsback):
        return self.setPlotStickLine(name, np.nan, np.nan, 0, main, EEQU_ISNOT_AXIS, barsback)

    def formatArgs(self, args):
        if len(args) == 0:
            return None

        argStr = ""
        for arg in args:
            if isinstance(arg, str):
                argStr = argStr + ' ' + arg
            else:
                argStr = argStr + ' ' + str(arg)

        return '[User]%s' % argStr

    def LogDebug(self, args):
        logInfo = self.formatArgs(args)
        self.logger.debug(logInfo)

    def LogInfo(self, args):
        logInfo = self.formatArgs(args)
        self.logger.info(logInfo)

    def LogWarn(self, args):
        logInfo = self.formatArgs(args)
        self.logger.warn(logInfo)

    def LogError(self, args):
        logInfo = self.formatArgs(args)
        self.logger.error(logInfo)

    # ///////////////////////属性函数///////////////////////////
    def getBarInterval(self):
        barInfo = self._cfgModel.getKLineShowInfo()
        if 'KLineSlice' not in barInfo:
            return None
        return barInfo['KLineSlice']

    def getBarType(self):
        barInfo = self._cfgModel.getKLineShowInfo()
        if 'KLineType' not in barInfo:
            return None
        return barInfo['KLineType']

    def getBidAskSize(self, contNo):
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return 0
            else:
                contractNo = contractTuple[0]

        quoteModel = self._qteModel._contractData[contractNo]
        bidList = quoteModel._metaData['Lv2BidData']

        isNotAllZero = False
        for bidData in bidList:
            isNotAllZero = isNotAllZero or bidData != 0

        return len(bidList) if isNotAllZero else 0

    def getCommodityInfoFromContNo(self, contNo):
        '''
        从合约编号中提取交易所编码/商品编码/合约到期日期
        :param contNo: 合约编号
        :return: {}
        '''
        ret = {
            'ExchangeCode': '',  # 交易所编码
            'CommodityCode': '',  # 商品编码
            'CommodityNo': '',  # 合约到期日期
        }
        contractNo = contNo
        if not contNo:
            contractNo = self._cfgModel.getBenchmark()

        contList = contractNo.split('|')
        if len(contList) == 0:
            return ret

        ret['ExchangeCode'] = contList[0]
        ret['CommodityCode'] = '|'.join(contList[:-1])
        ret['CommodityNo'] = contList[-1]
        return ret

    def getCanTrade(self, contNo):
        return 0

    def getContractUnit(self, contNo):
        commodityNo = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return 0

        commodityModel = self._qteModel._commodityData[commodityNo]
        return commodityModel._metaData['TradeDot']

    def getExchangeName(self, contNo):
        exchangeNo = self.getCommodityInfoFromContNo(contNo)['ExchangeCode']
        return exchangeNo
        # if exchangeNo not in self._qteModel._exchangeData:
        #    return None

        # exchangeModel = self._qteModel._exchangeData[exchangeNo]
        # return exchangeModel._metaData['ExchangeName']

    def getExchangeTime(self, exgNo):
        return self._qteModel.getExchangeTime(exgNo)

    def getExchangeStatus(self, exgNo):
        return self._qteModel.getExchangeStatus(exgNo)

    def getExpiredDate(self, contNo):
        return 0

    def getGetSessionCount(self, contNo):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return 0

        sessionCount = 0
        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        for data in timeBucket:
            if data['TradeState'] == EEQU_TRADESTATE_BID or data['TradeState'] == EEQU_TRADESTATE_CONTINUOUS:
                sessionCount += 1
        return sessionCount

    def getSessionEndTime(self, contNo, index):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return 0

        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        endTime = timeBucket[2 * index + 1]["BeginTime"] if 2 * index + 1 < len(timeBucket) else 0
        return float(endTime) / 1000000000

    def getGetSessionStartTime(self, contNo, index):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return 0

        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        beginTime = timeBucket[2 * index]["BeginTime"] if 2 * index < len(timeBucket) else 0
        return float(beginTime) / 1000000000

    def getNextTimeInfo(self, contNo, timeStr):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return {}

        timeInt = float(timeStr) * 1000000000

        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        if len(timeBucket) == 0:
            return {}

        timeList = []
        for timeDict in timeBucket:
            timeList.append((timeDict['BeginTime'], timeDict['TradeState']))
        list.sort(timeList, key=lambda t: t[0])

        for timeTuple in timeList:
            if timeTuple[0] >= timeInt:
                return {'Time': float(timeTuple[0]) / 1000000000, 'TradeState': timeTuple[1]}

        return {'Time': float(timeList[0][0]) / 1000000000, 'TradeState': timeList[0][1]}

    def getCurrentTime(self):
        currentTime = datetime.now().strftime('0.%H%M%S')
        return float(currentTime)

    def isInSession(self, contNo):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        # 兼容跨期套利
        contNoInfo = contNo.split('|')
        if len(contNoInfo) >= 4 and (contNoInfo[1] == 'S' or contNoInfo[1] == 's'):
            contNo = contNoInfo[0] + '|F|' + contNoInfo[2] + '|' + contNoInfo[3]

        currentTime = self.getCurrentTime()
        sessionCount = self.getGetSessionCount(contNo)
        for index in range(0, sessionCount):
            startTime = self.getGetSessionStartTime(contNo, index)
            endTime = self.getSessionEndTime(contNo, index)

            if startTime >= endTime:
                endTime += 0.24
                if currentTime <= startTime:
                    currentTime += 0.24
            if currentTime >= startTime and currentTime < endTime:
                return True
        return False

    def getMarginRatio(self, contNo):
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return 0
            else:
                contractNo = contractTuple[0]

        marginValue = self._cfgModel.getMarginValue()
        return marginValue if not marginValue else 8

    def getMaxBarsBack(self):
        return self._hisModel.getHisLength()

    def getMaxSingleTradeSize(self):
        return MAXSINGLETRADESIZE

    def getPriceTick(self, contNo):
        commodityNo = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return 0

        commodityModel = self._qteModel._commodityData[commodityNo]
        priceTick = commodityModel._metaData['PriceTick']
        return priceTick

    def getOptionStyle(self, contNo):
        return 0

    def getOptionType(self, contNo):
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return -1
            else:
                contractNo = contractTuple[0]

        contInfo = contractNo.split('|')
        if len(contInfo) < 4 or contInfo[1] != EEQU_COMMODITYTYPE_OPTION:
            return -1

        commodityMo = contInfo[3]
        if 'C' in commodityMo or 'c' in commodityMo:
            return 0
        elif 'P' in commodityMo or 'p' in commodityMo:
            return 1
        return -1

    def getPriceScale(self, contNo):
        commodityNo = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return 0

        commodityModel = self._qteModel._commodityData[commodityNo]
        pricePrec = commodityModel._metaData['PricePrec']

        return math.pow(0.1, pricePrec)

    def getRelativeSymbol(self):
        return 0

    def getStrikePrice(self):
        return 0

    def getSymbol(self):
        return self._cfgModel.getContract()

    def getSymbolName(self, contNo):
        commodityInfo = self.getCommodityInfoFromContNo(contNo)
        commodityNo = commodityInfo['CommodityCode']
        if commodityNo not in self._qteModel._commodityData:
            return None

        commodityModel = self._qteModel._commodityData[commodityNo]
        commodityName = commodityModel._metaData['CommodityName']
        return commodityName + commodityInfo['CommodityNo']

    def getSymbolType(self, contNo):
        return self.getCommodityInfoFromContNo(contNo)['CommodityCode']

    def getIndexMap(self, contNo):
        return self._qteModel.getUnderlayContractNo(contNo)

    # ///////////////////////策略状态///////////////////////////
    def getAvgEntryPrice(self, contNo):
        '''当前持仓的平均建仓价格'''
        if not contNo:
            contNo = self._config.getBenchmark()

        posInfo = self._calcCenter.getPositionInfo(contNo)
        if not posInfo:
            return 0

        totalPrice = posInfo['BuyPrice'] * posInfo['TotalBuy'] + posInfo['SellPrice'] * posInfo['TotalSell']
        totalQty = posInfo['TotalBuy'] + posInfo['TotalSell']

        return totalPrice / totalQty if totalQty > 0 else 0

    def getFirstOpenOrderInfo(self, contNo, key):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        if self.getMarketPosition(contNo) == 0:
            return -1

        orderInfo = self._calcCenter.getFirstOpenOrder(contNo)
        if not orderInfo or key not in orderInfo:
            return -1

        return orderInfo[key]

    def getLatestCoverOrderInfo(self, contNo, key):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        if self.getMarketPosition(contNo) == 0:
            return -1

        orderInfo = self._calcCenter.getLatestCoverOrder(contNo)
        if not orderInfo or key not in orderInfo:
            return -1

        return orderInfo[key]

    def getBarsSinceEntry(self, contNo):
        '''获得当前持仓中指定合约的第一个建仓位置到当前位置的Bar计数'''
        barIndex = self.getFirstOpenOrderInfo(contNo, 'CurBarIndex')
        if barIndex == -1:
            return barIndex

        curBar = self._hisModel.getCurBar()
        return int(curBar['KLineIndex'] - barIndex)

    def getBarsSinceExit(self, contNo):
        '''获得当前持仓中指定合约的最近平仓位置到当前位置的Bar计数'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getLatestCoverOrder(contNo)
        if not orderInfo or 'CurBarIndex' not in orderInfo:
            return -1

        barIndex = orderInfo['CurBarIndex']

        curBar = self._hisModel.getCurBar()
        return (curBar['KLineIndex'] - barIndex)

    def getBarsSinceLastEntry(self, contNo):
        '''获得当前持仓的最后一个建仓位置到当前位置的Bar计数'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        if self.getMarketPosition(contNo) == 0:
            return -1

        orderInfo = self._calcCenter.getLatestCoverOrder(contNo)
        if not orderInfo or 'CurBarIndex' not in orderInfo:
            return -1

        barIndex = orderInfo['CurBarIndex']

        curBar = self._hisModel.getCurBar()
        return (int(curBar['KLineIndex']) - barIndex)

    def getBarsSinceToday(self, contractNo, barType, barValue):
        key = self.getKey(contractNo, barType, barValue)
        curBar = self._hisModel.getCurBar(key)
        tradeDate = curBar['TradeDate']
        barList = self._hisModel._curBarDict[key].getTradeDateKLine(tradeDate)
        if len(barList) == 0:
            return 0

        firstBar = barList[0]
        res = curBar['KLineIndex'] - firstBar['KLineIndex']
        return res if res > 0 else 0

    def getPositionValue(self, contNo, key):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        pos = self.getMarketPosition(contNo)
        if pos == 0:
            return -1

        positionInfo = self._calcCenter.getPositionInfo(contNo)
        if not positionInfo or key not in positionInfo:
            return -1

        return positionInfo[key]

    def getContractProfit(self, contNo):
        '''获得当前持仓的每手浮动盈亏'''
        holdProfit = self.getPositionValue(contNo, 'HoldProfit')
        if holdProfit == -1:
            return 0

        totalBuy = self.getPositionValue(contNo, 'TotalBuy')
        totalSell = self.getPositionValue(contNo, 'TotalSell')
        totalQty = totalBuy + totalSell
        return holdProfit / totalQty if totalQty > 0 else 0

    def getCurrentContracts(self, contNo):
        '''获得策略当前的持仓合约数(净持仓)'''
        totalBuy = self.getPositionValue(contNo, 'TotalBuy')
        totalSell = self.getPositionValue(contNo, 'TotalSell')

        totalBuy = 0 if totalBuy == -1 else totalBuy
        totalSell = 0 if totalSell == -1 else totalSell

        return totalBuy - totalSell

    def getEntryDate(self, contNo):
        '''获得当前持仓的第一个建仓位置的日期'''
        entryDate = self.getFirstOpenOrderInfo(contNo, 'TradeDate')
        if entryDate == -1:
            return 19700101
        return entryDate

    def getBuyPositionInStrategy(self, contNo):
        '''获得当前持仓的买入方向的持仓量'''
        return self.getPositionValue(contNo, 'TotalBuy')

    def getSellPositionInStrategy(self, contNo):
        '''当前持仓的卖出持仓量'''
        return self.getPositionValue(contNo, 'TotalSell')

    def getEntryPrice(self, contNo):
        '''获得当前持仓的第一次建仓的委托价格'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getFirstOpenOrder(contNo)
        if not orderInfo or 'OrderPrice' not in orderInfo:
            return 0

        return float(orderInfo['OrderPrice'])

    def getEntryTime(self, contNo):
        '''获得当前持仓的第一个建仓位置的时间'''
        dateTimeStamp = self.getFirstOpenOrderInfo(contNo, 'DateTimeStamp')
        if dateTimeStamp == -1:
            return 0
        return (int(dateTimeStamp) % 1000000000) / 1000000000

    def getExitDate(self, contNo):
        ''' 获得最近平仓位置Bar日期'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getLatestCoverOrder(contNo)
        if not orderInfo or 'TradeDate' not in orderInfo:
            return 19700101

        return int(orderInfo['TradeDate'])

    def getExitPrice(self, contNo):
        '''获得合约最近一次平仓的委托价格'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getLatestCoverOrder(contNo)
        if not orderInfo or 'OrderPrice' not in orderInfo:
            return 0

        return orderInfo['OrderPrice']

    def getExitTime(self, contNo):
        '''获得最近平仓位置Bar时间'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getLatestCoverOrder(contNo)
        if not orderInfo or 'DateTimeStamp' not in orderInfo:
            return 0

        dateTimeStamp = orderInfo['DateTimeStamp']
        return (int(dateTimeStamp) % 1000000000) / 1000000000

    def getLastEntryDate(self, contNo):
        '''获得当前持仓的最后一个建仓位置的日期'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getLatestOpenOrder(contNo)
        if not orderInfo or 'TradeDate' not in orderInfo:
            return 19700101

        return int(orderInfo['TradeDate'])

    def getLastEntryPrice(self, contNo):
        '''获得当前持仓的最后一次建仓的委托价格'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getLatestOpenOrder(contNo)
        if not orderInfo or 'OrderPrice' not in orderInfo:
            return 0

        return float(orderInfo['OrderPrice'])

    def getLastEntryTime(self, contNo):
        '''获得当前持仓的最后一个建仓位置的时间'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        orderInfo = self._calcCenter.getLatestOpenOrder(contNo)
        if not orderInfo or 'DateTimeStamp' not in orderInfo:
            return 0

        dateTimeStamp = orderInfo['DateTimeStamp']
        return (int(dateTimeStamp) % 1000000000) / 1000000000

    def getMarketPosition(self, contNo):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        positionInfo = self._calcCenter.getPositionInfo(contNo)
        if not positionInfo:
            return -1

        buy = positionInfo['TotalBuy']
        sell = positionInfo['TotalSell']
        if buy == sell:
            return 0
        return 1 if buy > sell else -1

    # ///////////////////////策略性能///////////////////////////
    def getAvailable(self):
        return self._calcCenter.getProfit()['Available']

    def getEquity(self):
        fundRecodeList = self._calcCenter.getFundRecord()
        if not fundRecodeList:
            return self.getAvailable()

        fundRecordDict = fundRecodeList[-1]
        return fundRecordDict['DynamicEquity']

    def getFloatProfit(self, contNo):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()
        return self._calcCenter._getHoldProfit(contNo)

    def getGrossLoss(self):
        return self._calcCenter.getProfit()["TotalLose"]

    def getGrossProfit(self):
        return self._calcCenter.getProfit()["TotalProfit"]

    def getMargin(self, contNo):
        if not contNo:
            contNo = self._cfgModel.getBenchmark()
        return self._calcCenter._getHoldMargin(contNo)

    def getNetProfit(self):
        '''平仓盈亏'''
        return self._calcCenter.getProfit()["LiquidateProfit"]

    def getNumEvenTrades(self):
        '''保本交易总手数'''
        # return self._calcCenter.getProfit()["EventTrade"]
        return 0

    def getNumLosTrades(self):
        '''亏损交易总手数'''
        # return self._calcCenter.getProfit()["LoseTrade"]
        return 0

    def getNumWinTrades(self):
        '''盈利交易的总手数'''
        # return self._calcCenter.getProfit()["WinTrade"]
        return 0

    def getNumAllTimes(self):
        '''开仓次数'''
        return self._calcCenter.getProfit()["AllTimes"]

    def getNumWinTimes(self):
        '''盈利次数'''
        return self._calcCenter.getProfit()["WinTimes"]

    def getNumLoseTimes(self):
        '''亏损次数'''
        return self._calcCenter.getProfit()["LoseTimes"]

    def getNumEventTimes(self):
        '''保本次数'''
        return self._calcCenter.getProfit()["EventTimes"]

    def getPercentProfit(self):
        '''盈利成功率'''
        winTimes = self._calcCenter.getProfit()["WinTimes"]
        allTimes = self._calcCenter.getProfit()["AllTimes"]
        return winTimes / allTimes if allTimes > 0 else 0

    def getTradeCost(self):
        '''交易产生的手续费'''
        return self._calcCenter.getProfit()["Cost"]

    def getTotalTrades(self):
        '''交易总开仓手数'''
        # return self._calcCenter.getProfit()["AllTrade"]
        return 0

    def SMA(self, price, period, weight):
        '''计算加权移动平均值'''
        return self._staModel.SMA(price, period, weight)

    def ParabolicSAR(self, high, low, afstep, aflimit):
        '''计算抛物线转向'''
        return self._staModel.ParabolicSAR(high, low, afstep, aflimit)

    def getHighest(self, price, length):
        if (not isinstance(price, np.ndarray) and not isinstance(price, list)) or len(price) == 0:
            return np.array([])

        arr = np.array(price) if isinstance(price, list) else price
        if length <= 1:
            return arr

        return talib.MAX(arr, length)

    def getLowest(self, price, length):
        if (not isinstance(price, np.ndarray) and not isinstance(price, list)) or len(price) == 0:
            return np.array([])

        arr = np.array(price) if isinstance(price, list) else price
        if length <= 1:
            return arr

        return talib.MIN(arr, length)
