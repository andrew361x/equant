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
        self._hisModel = StrategyHisQuote(strategy, self._cfgModel, self._calcCenter)
        self._trdModel = StrategyTrade(strategy, self._cfgModel)

    def setRunStatus(self, status):
        self._runStatus = status

    def getTradeModel(self):
        return self._trdModel
        
    def getConfigData(self):
        return self._cfgModel.getConfig()

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
            "KLineType": "M", # todo
            "KLineSlice": 1,  # todo
            "TradeDot": self.getContractUnit(contNo),  # 每手乘数
            "PriceTick": self.getPriceScale(contNo),  # 最小变动价位
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
        
    def subQuote(self):
        self._qteModel.subQuote()

    def onExchange(self, event):
        self._qteModel.onExchange(event)

    def onCommodity(self, event):
        self._qteModel.onCommodity(event)
            
    def onQuoteRsp(self, event):
        self._qteModel.onQuoteRsp(event)
        
    def onQuoteNotice(self, event):
        self._qteModel.onQuoteNotice(event)
        
    def onDepthNotice(self, event):
        self._qteModel.onDepthNotice(event)

    # ///////////////////////交易数据接口/////////////////////////
    def reqTradeData(self):
        self._trdModel.reqTradeData()
        
    #////////////////////////配置接口////////////////////////////
    def continueTrigger(self):
        return self._cfgModel.continues()

    #++++++++++++++++++++++base api接口++++++++++++++++++++++++++
    #////////////////////////K线函数/////////////////////////////
    def getKey(self, contNo, kLineType, kLineValue):
        #空合约取默认展示的合约
        if contNo == "" or kLineType =='' or kLineValue == 0:
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
        #TODO: 为什么要减1
        #return curBar["KLineIndex"] - 1
        return curBar['KLineIndex']

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
        return self._qteModel.getQLastDate(symbol)

    def getQLastFlag(self, symbol):
        return self._qteModel.getQLastFlag(symbol)

    def getQLastTime(self, symbol):
        return self._qteModel.getQLastTime(symbol)

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
    def setBuy(self, contractNo, share, price):
        contNo = contractNo if contractNo else self._cfgModel.getBenchmark()
        
        # 非K线触发的策略，不使用Bar
        curBar = None
        # 账户
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"

        # 对于开仓，需要平掉反向持仓
        qty = self._calcCenter.needCover(userNo, contNo, dBuy, share, price)
        if qty > 0:
            eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dBuy, oCover, hSpeculate, price, qty, curBar, False)
            if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)
            
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dBuy, oOpen, hSpeculate, price, share, curBar)
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setBuyToCover(self, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()
        curBar = None

        # 交易计算、生成回测报告
        # 产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dBuy, oCover, hSpeculate, price, share, curBar)
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setSell(self, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()
        curBar = None

        # 交易计算、生成回测报告
        # 产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dSell, oCover, hSpeculate, price, share, curBar)
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setSellShort(self, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()
        curBar = None
        
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        qty = self._calcCenter.needCover(userNo, contNo, dSell, share, price)
        if qty > 0:
            eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dSell, oCover, hSpeculate, price, qty, curBar, False)
            if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

        #交易计算、生成回测报告
        #产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dSell, oOpen, hSpeculate, price, share, curBar)
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
            'KLineIndex' : curBar['KLineIndex'],
            'ContractNo' : contNo,
            'Direct'     : direct,
            'Offset'     : offset,
            'Price'      : price,
            'Qty'        : share,
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

    # def deleteOrder(self, contractNo):
    #     pass

    #////////////////////////设置函数////////////////////////////
    def getConfig(self):
        return self._cfgModel._metaData

    def setSetBenchmark(self, symbolTuple):
        self._cfgModel.setContract(symbolTuple)

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

    def setTriggerCont(self, contNoTuple):
        if not contNoTuple or len(contNoTuple) == 0:
            return -1
        if len(contNoTuple) > 4:
            contNoTuple = contNoTuple[:4]
        return self._cfgModel.setTriggerCont(contNoTuple)

    # def setTradeMode(self, inActual, useSample, useReal):
    #     return self._cfgModel.setTradeMode(inActual, useSample, useReal)

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

    def setHedge(self, hedge, contNo):
        if hedge not in ('T', 'B', 'S', 'M'):
            return -1

        self._cfgModel.setHedge(hedge, contNo)
        return 0

    def setSlippage(self, slippage):
        self._cfgModel.setSlippage(slippage)
        return 0

    def setTriggerMode(self, contNo, type, value):
        return self._cfgModel.setTrigger(contNo, type, value)

    # ///////////////////////账户函数///////////////////////////
    def getAccountId(self):
        return self._trdModel.getAccountId()

    def getCost(self):
        return self._trdModel.getCost()

    def getCurrentEquity(self):
        return self._trdModel.getCurrentEquity()

    def getFreeMargin(self):
        return self._trdModel.getFreeMargin()

    def getProfitLoss(self):
        return self._trdModel.getProfitLoss()

    def getTotalFreeze(self):
        return self._trdModel.getTotalFreeze()

    def getBuyAvgPrice(self, contNo):
        return self._trdModel.getBuyAvgPrice(contNo)

    def getBuyPosition(self, contNo):
        return self._trdModel.getBuyPosition(contNo)

    def getBuyProfitLoss(self, contNo):
        return self._trdModel.getBuyProfitLoss(contNo)

    def getSellAvgPrice(self, contNo):
        return self._trdModel.getSellAvgPrice(contNo)

    def getSellPosition(self, contNo):
        return self._trdModel.getSellPosition(contNo)

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
        if (triggerType == ST_TRIGGER_KLINE or triggerType == ST_TRIGGER_HIS_KLINE) and triggerData :
            curBarIndex = triggerData["KLineIndex"]
            curBar = triggerData

        orderParam = {
            "UserNo"         : userNo,                   # 账户编号
            "OrderType"      : orderType,                # 定单类型
            "ValidType"      : validType,                # 有效类型
            "ValidTime"      : '0',                      # 有效日期时间(GTD情况下使用)
            "Cont"           : contNo,                   # 合约
            "Direct"         : orderDirct,               # 买卖方向：买、卖
            "Offset"         : entryOrExit,              # 开仓、平仓、平今
            "Hedge"          : hedge,                    # 投机套保
            "OrderPrice"     : orderPrice,               # 委托价格 或 期权应价买入价格
            "OrderQty"       : orderQty,                 # 委托数量 或 期权应价数量
            "DateTimeStamp"  : dateTime,                 # 时间戳（基准合约）
            "TradeDate"      : tradeDate,                # 交易日（基准合约）
            "TriggerType"    : triggerType,
            "CurBarIndex"    : curBarIndex #
        }

        key = (triggerInfo['ContractNo'], triggerInfo['KLineType'], triggerInfo['KLineSlice'])
        isSendSignal = self._config.hasKLineTrigger() and key == self._config.getKLineShowInfoSimple()
        # K线触发，发送信号
        if signal and isSendSignal:
            self.sendSignalEvent(self._signalName, contNo, orderDirct, entryOrExit, orderPrice, orderQty, curBar)
        # **************************************
        self._calcCenter.addOrder(orderParam)
        # **************************************
        return self.sendOrder(userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)
        
    def sendOrder(self, userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
        '''A账户下单函数，不经过calc模块，不产生信号，直接发单'''
        # 发送下单信号,K线触发、即时行情触发
        # 未选择实盘运行
        if not self._cfgModel.isActualRun():
            return -1, '未选择实盘运行，请在设置界面勾选"实盘运行"，或者在策略代码中调用SetActual()方法选择实盘运行'

        if not self._strategy.isRealTimeStatus():
            return -2, "策略当前状态不是实盘运行状态，请勿在历史回测阶段调用该函数"
               
        # 账户错误
        if not userNo or userNo == 'Default':
            return -3, "未指定下单账户信息"

        # 指定的用户未登录
        if self._trdModel.getSign(userNo) is None:
            return -4, "输入的账户没有在极星客户端登录"

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
            'TriggerPrice': 0,
            'TriggerMode': tmNone,
            'TriggerCondition': tcNone,
            'OrderQty': orderQty,
            'StrategyType': stNone,
            'Remark': '',
            'AddOneIsValid': tsDay,
        }

        eId = str(self._strategy.getStrategyId()) + '-' + str(self._strategy.getESessionId())
        aOrderEvent = Event({
            "EventCode": EV_ST2EG_ACTUAL_ORDER,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": aOrder,
            "ESessionId": eId,
        })
        self._strategy.sendEvent2Engine(aOrderEvent)

        # 更新策略的订单信息
        self._strategy.setESessionId(self._strategy.getESessionId() + 1)
        self._strategy.updateLocalOrder(eId, aOrder)
        return 0, eId

    # def addOrder2CalcCenter(self, userNo, contNo, direct, offset, price, share, curBar):
    #     if not curBar:
    #         return
    #
    #     orderParam = {
    #         "UserNo": userNo,  # 账户编号
    #         "OrderType": otMarket,  # 定单类型
    #         "ValidType": vtNone,  # 有效类型
    #         "ValidTime": '0',  # 有效日期时间(GTD情况下使用)
    #         "Cont": contNo,  # 合约
    #         "Direct": direct,  # 买卖方向：买、卖
    #         "Offset": offset,  # 开仓、平仓、平今
    #         "Hedge": hSpeculate,  # 投机套保
    #         "OrderPrice": price,  # 委托价格 或 期权应价买入价格
    #         "OrderQty": share,  # 委托数量 或 期权应价数量
    #         "DateTimeStamp": curBar['DateTimeStamp'],  # 时间戳（基准合约）
    #         "TradeDate": curBar['TradeDate'],  # 交易日（基准合约）
    #         "CurrentBarIndex": curBar['KLineIndex'],  # 当前K线索引
    #     }
    #     self._calcCenter.addOrder(orderParam)

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
        return EEQU_KLINE_SECOND

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

    #///////////////////////其他函数///////////////////////////
    def _addSeries(self, name, value, color, main, axis, type):
        addSeriesEvent = Event({
            "EventCode": EV_ST2EG_ADD_KLINESERIES,
            "StrategyId": self._strategy.getStrategyId(),
            "Data":{
                'ItemName':name,
                'Type': type,
                'Color': color,
                'Thick': 1,
                'OwnAxis': axis,
                'Param': [],
                'ParamNum': 0,
                'Groupid': 0,
                'GroupName':name,
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
            "EventCode" : eventCode,
            "StrategyId": self._strategy.getStrategyId(),
            "Data":{
                "SeriesName": name,
                "SeriesType": type,
                "IsMain"    : main,
                "Count"     : len(data),
                "Data"      : data
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
            'KLineIndex' : klineIndex,
            'Value'      : value,
            'Text'       : text
        }]

        self._plotNumeric(self._textName, value, color, main, EEQU_ISNOT_AXIS, EEQU_TEXT, barsback, data)
        
    def setUnPlotText(self, main, barsback):
        main = '0' if main else '1'
        curBar = self._hisModel.getCurBar()
        
        klineIndex = curBar['KLineIndex'] - barsback
        if klineIndex <= 0:
            return
        
        data = [{
            'KLineIndex' : klineIndex,
            'Value'      : np.nan,
            'Text'       : ""
        }]

        self._plotNumeric(self._textName, np.nan, 0, main, EEQU_ISNOT_AXIS, EEQU_TEXT, barsback, data)
        
    def setPlotIcon(self, value, icon, color, main, barsback):
        main = '0' if main else '1'
        curBar = self._hisModel.getCurBar()
        klineIndex = curBar['KLineIndex'] - barsback
        
        if klineIndex <= 0:
            return
            
        data = [{
            'KLineIndex' : klineIndex,
            'Value'      : value,
            'Icon'       : icon
        }]

        self._plotNumeric(self._strategyName, value, color, main, EEQU_ISNOT_AXIS, EEQU_ICON, barsback, data)
    
    def setPlotNumeric(self, name, value, color, main, axis, type, barsback):
        main = '0' if main else '1'
        axis = '0' if axis else '1'
        
        curBar = self._hisModel.getCurBar()

        klineIndex = curBar['KLineIndex'] - barsback
        if klineIndex <= 0:
            return
                   
        data = [{
            'KLineIndex' : klineIndex,
            'Value'      : value
        }]
        self._plotNumeric(name, value, color, main, axis, type, barsback, data)
        
    def setPlotVertLine(self, color, main, axis, barsback):
        main = '0' if main else '1'
        axis = '0' if axis else '1'
        
        curBar = self._hisModel.getCurBar()
        klineIndex = curBar['KLineIndex'] - barsback
        
        if klineIndex <= 0:
            return
        
        value = curBar['LastPrice']
        data = [{
            'KLineIndex' : klineIndex,
            'Value'      : value,
            'ClrK'       : color
        }]

        self._plotNumeric(self._strategyName, value, color, main, axis, EEQU_VERTLINE, barsback, data)
        

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
    def getBarInterval(self, contNo):
        if len(self._cfgModel._metaData) == 0 or 'Sample' not in self._cfgModel._metaData:
            return None

        sample = self._cfgModel.getSample()
        if not contNo:
            return sample['KLineSlice']
        barInfo = sample[contNo][-1]
        return barInfo['KLineSlice']

    def getBarType(self,contNo):
        if len(self._cfgModel._metaData) == 0 or 'Sample' not in self._cfgModel._metaData:
            return None

        sample = self._cfgModel.getSample()
        if not contNo:
            return sample['KLineType']
        barInfo = sample[contNo][-1]
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
            'ExchangeCode'  : '', # 交易所编码
            'CommodityCode' : '', # 商品编码
            'CommodityNo'   : '', # 合约到期日期
        }
        contractNo = contNo
        if not contNo:
            contractTuple = self._cfgModel.getContract()
            if len(contractTuple) == 0:
                return ret
            else:
                contractNo = contractTuple[0]

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

        if exchangeNo not in self._qteModel._exchangeData:
            return None

        exchangeModel = self._qteModel._exchangeData[exchangeNo]
        return exchangeModel._metaData['ExchangeName']

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
        return timeBucket[2*index + 1]["BeginTime"] if 2*index + 1 < len(timeBucket) else 0

    def getGetSessionStartTime(self, contNo, index):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return 0

        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        return timeBucket[2 * index]["BeginTime"] if 2 * index < len(timeBucket) else 0

    def getNextTimeInfo(self, contNo, timeStr):
        commodity = self.getCommodityInfoFromContNo(contNo)['CommodityCode']
        if commodity not in self._qteModel._commodityData:
            return {}

        timeInt = self.convertTime(timeStr)
        if timeInt < 0:
            return {}

        timeBucket = self._qteModel._commodityData[commodity]._metaData['TimeBucket']
        if len(timeBucket) == 0:
            return {}

        timeList = []
        for timeDict in timeBucket:
            timeList.append((timeDict['BeginTime'], timeDict['TradeState']))
        list.sort(timeList, key=lambda t: t[0])

        for timeTuple in timeList:
            if timeTuple[0] >= timeInt:
                return {'Time' : timeTuple[0], 'TradeState' : timeTuple[1]}

        return {'Time' : timeList[0][0], 'TradeState' : timeList[0][1]}

    def convertTime(self, timeStr):
        # to millisecond
        timeList = timeStr.split(':')
        if len(timeList) != 3:
            return -1

        timeInt = 0
        for t in timeList:
            timeInt = timeInt*100 + int(t)
        return timeInt*1000

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
        return commodityName+commodityInfo['CommodityNo']

    def getSymbolType(self, contNo):
        return self.getCommodityInfoFromContNo(contNo)['CommodityCode']

    # ///////////////////////策略状态///////////////////////////
    def getAvgEntryPrice(self, contNo):
        '''当前持仓的平均建仓价格'''
        posInfo = self._calcCenter.getPositionInfo(contNo)
        if not posInfo:
            return 0

        totalPrice = 0
        totalQty = 0
        if not contNo:
            for posDic in posInfo.values():
                totalPrice += posDic['BuyPrice'] * posDic['TotalBuy'] + posDic['SellPrice'] * posDic['TotalSell']
                totalQty += posDic['TotalBuy'] + posDic['TotalSell']
        else :
            totalPrice += posInfo['BuyPrice'] * posInfo['TotalBuy'] + posInfo['SellPrice'] * posInfo['TotalSell']
            totalQty += posInfo['TotalBuy'] + posInfo['TotalSell']

        return totalPrice/totalQty if totalQty > 0 else 0

    def getBarsSinceEntry(self, contNo):
        '''获得当前持仓中指定合约的第一个建仓位置到当前位置的Bar计数'''
        if not contNo:
            contNo = self._cfgModel.getBenchmark()

        barInfo = None
        for eSessionId in self._strategy._eSessionIdList:
            tradeRecord = self._strategy._localOrder[eSessionId]
            # if contNo == tradeRecord._contNo and tradeRecord._offset == oOpen:
            if contNo == tradeRecord._contNo and tradeRecord._offset == 'N':
                barInfo = tradeRecord.getBarInfo()
                break

        if not barInfo:
            return 0

        curBar = self._hisModel.getCurBar()
        return (curBar['KLineIndex'] - barInfo['KLineIndex'])

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

    def getFloatProfit(self, contNo):
        return self._calcCenter._getHoldProfit(contNo)

    def getGrossLoss(self):
        return self._calcCenter.getProfit()["TotalLose"]

    def getGrossProfit(self):
        return self._calcCenter.getProfit()["TotalProfit"]

    def getMargin(self, contNo):
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
        return winTimes/allTimes if allTimes > 0 else 0

    def getTradeCost(self):
        '''交易产生的手续费'''
        return self._calcCenter.getProfit()["Cost"]

    def getTotalTrades(self):
        '''交易总开仓手数'''
        # return self._calcCenter.getProfit()["AllTrade"]
        return 0

