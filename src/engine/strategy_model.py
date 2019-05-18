import numpy as np
from capi.com_types import *
from .engine_model import *
from copy import deepcopy
import talib
import time, sys
import datetime
import copy
import math

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from engine.calc import CalcCenter

class StrategyModel(object):
    def __init__(self, strategy):
        self._strategy = strategy
        self.logger = strategy.logger
        self._argsDict = strategy._argsDict
       
        self._plotedDict = {}
        
        # Notice：会抛异常
        self._cfgModel = StrategyConfig(self._argsDict)
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
        self._qteModel.initialize()
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
            "KLineType": self._cfgModel.getKLineType(),  # K线类型
            "KLineSlice": self._cfgModel.getKLineSlice(),  # K线间隔
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
            self._strategy.setTriggerType(ST_TRIGGER_FILL_DATA)
            self._hisModel.runReportRealTime(context, handle_data, event)
        else:
            self._hisModel.runRealTime(context, handle_data, event)
        # if code == ST_TRIGGER_KLINE:
        #     self._strategy.setTriggerType(ST_TRIGGER_KLINE)
        #     self._hisModel.runRealTime(context, handle_data, event)
        #
        # elif code == ST_TRIGGER_CYCLE or code == ST_TRIGGER_TIMER:
        #     if not self._strategy.isRealTimeStatus():
        #         return
        #     else:
        #         self._hisModel.runOtherTrigger(context, handle_data, event)
        # elif code == ST_TRIGGER_TRADE:
        #     self._strategy.setTriggerType(ST_TRIGGER_FILL_DATA)
        #
        #     # print("交易触发===================")
        #     if not self._strategy.isRealTimeStatus():
        #         return
        #     else:
        #         self.logger.info("交易触发")
        #         self._hisModel.runOtherTrigger(context, handle_data, event)
        # elif code == ST_TRIGGER_SANPSHOT:
        #      self._strategy.setTriggerType(ST_TRIGGER_SANPSHOT)
        #      self._hisModel.runSnapShotTrigger(context, handle_data, event)

    def reqHisQuote(self):
        self._hisModel.reqAndSubQuote()

    def onHisQuoteRsp(self, event):
        self._hisModel.onHisQuoteRsp(event)
        
    def onHisQuoteNotice(self, event):
        self._hisModel.onHisQuoteNotice(event)

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
    def getBarOpenInt(self, contNo):
        return self._hisModel.getBarOpenInt(contNo)

    def getBarTradeDate(self, contNo):
        return self._hisModel.getBarTradeDate(contNo)

    def getBarCount(self, contNo):
        return self._hisModel.getBarCount(contNo)

    def getCurrentBar(self, contNo):
        curBar = self._hisModel.getCurBar(contNo)
        return curBar["KLineIndex"] - 1

    def getBarStatus(self, contNo):
        return self._hisModel.getBarStatus(contNo)

    def isHistoryDataExist(self, contNo):
        return self._hisModel.isHistoryDataExist(contNo)

    def getBarDate(self, contNo):
        return self._hisModel.getBarDate(contNo)

    def getBarTime(self, contNo):
        return self._hisModel.getBarTime(contNo)

    def getBarOpen(self, symbol):
        return self._hisModel.getBarOpen(symbol)
        
    def getBarClose(self, symbol):
        return self._hisModel.getBarClose(symbol)

    def getBarVol(self, contNo):
        return self._hisModel.getBarVol(contNo)

    def getBarHigh(self, symbol):
        return self._hisModel.getBarHigh(symbol)
        
    def getBarLow(self, symbol):
        return self._hisModel.getBarLow(symbol)

    # ////////////////////////即时行情////////////////////////////
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
            eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dBuy, oCover, hSpeculate, price, qty, curBar, 'BuyToCover', False)
            if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)
            
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dBuy, oOpen, hSpeculate, price, share, curBar, 'Buy')
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)


    def setBuyToCover(self, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()
        curBar = None

        # 交易计算、生成回测报告
        # 产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dBuy, oCover, hSpeculate, price, share, curBar, 'BuyToCover')
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setSell(self, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()
        curBar = None

        # 交易计算、生成回测报告
        # 产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dSell, oCover, hSpeculate, price, share, curBar, 'Sell')
        if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

    def setSellShort(self, contractNo, share, price):
        contNo = contractNo if contractNo is not None else self._cfgModel.getBenchmark()
        curBar = None
        
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        qty = self._calcCenter.needCover(userNo, contNo, dSell, share, price)
        if qty > 0:
            eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dSell, oCover, hSpeculate, price, qty, curBar, 'Sell', False)
            if eSessionId != "": self._strategy.updateBarInfoInLocalOrder(eSessionId, curBar)

        #交易计算、生成回测报告
        #产生信号
        userNo = self._cfgModel.getUserNo() if self._cfgModel.isActualRun() else "Default"
        eSessionId = self.buySellOrder(userNo, contNo, otLimit, vtNone, dSell, oOpen, hSpeculate, price, share, curBar, 'SellShort')
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

    def setUserNo(self, userNo):
        self._cfgModel.setUserNo(userNo)

    def setBarInterval(self, barType, barInterval, contNo):
        self._cfgModel.setBarInterval(barType, barInterval, contNo)

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

    def setTriggerMode(self, type, value):
        return self._cfgModel.setTrigger(type, value)

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
        entryOrExit, hedge, orderPrice, orderQty, curBar, singnalName, signal=True):
        '''
            1. buySell下单，经过calc模块，会判断虚拟资金，会产生平仓单
            2. 如果支持K线触发，会产生下单信号
            3. 对于即时行情和委托触发，在日志中分析下单信号
        '''
        curTriggerType = self._strategy.getTriggerType()
        if curTriggerType in [ST_TRIGGER_NONE, ST_TRIGGER_KLINE, ST_TRIGGER_HIS_KLINE] and not self._cfgModel.hasKLineTrigger():
            return
        datetime = '20190517090001001'
        tradeDate = '20190517'
        
        triggerDict = self._cfgModel.getTrigger()
        kilneTrigger = True if 'KLine' in triggerDict else False
        #K线触发
        if not curBar and kilneTrigger:
            curBar = self._hisModel.getCurBar()
            datetime = curBar['DateTimeStamp']
            tradeDate = curBar['TradeDate']
        
        orderParam = {
            "UserNo"         : userNo,                   # 账户编号
            "OrderType"      : orderType,                 # 定单类型
            "ValidType"      : validType,                   # 有效类型
            "ValidTime"      : '0',                      # 有效日期时间(GTD情况下使用)
            "Cont"           : contNo,                   # 合约
            "Direct"         : orderDirct,                   # 买卖方向：买、卖
            "Offset"         : entryOrExit,                   # 开仓、平仓、平今
            "Hedge"          : hedge,               # 投机套保
            "OrderPrice"     : orderPrice,                    # 委托价格 或 期权应价买入价格
            "OrderQty"       : orderQty,                    # 委托数量 或 期权应价数量
            "DateTimeStamp"  : datetime,                 # 时间戳（基准合约）
            "TradeDate"      : tradeDate,                # 交易日（基准合约）
        }

        # K线触发，发送信号
        if signal and kilneTrigger:
            self.sendSignalEvent(singnalName, contNo, orderDirct, entryOrExit, orderPrice, orderQty, curBar)
        self._calcCenter.addOrder(orderParam)
        return self.sendOrder(userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)
        
    def sendOrder(self, userNo, contNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
        '''A账户下单函数，不经过calc模块，不产生信号，直接发单'''
        #发送下单信号,K线触发、即时行情触发
        # 未选择实盘运行
        if not self._cfgModel.isActualRun():
            return ""
            
        if not self._strategy.isRealTimeStatus():
            return
               
        # 账户错误
        if not userNo or userNo == 'Default':
            return ""
        
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
        return eId


    def addOrder2CalcCenter(self, userNo, contNo, direct, offset, price, share, curBar):
        if not curBar:
            return

        orderParam = {
            "UserNo": userNo,  # 账户编号
            "OrderType": otMarket,  # 定单类型
            "ValidType": vtNone,  # 有效类型
            "ValidTime": '0',  # 有效日期时间(GTD情况下使用)
            "Cont": contNo,  # 合约
            "Direct": direct,  # 买卖方向：买、卖
            "Offset": offset,  # 开仓、平仓、平今
            "Hedge": hSpeculate,  # 投机套保
            "OrderPrice": price,  # 委托价格 或 期权应价买入价格
            "OrderQty": share,  # 委托数量 或 期权应价数量
            "DateTimeStamp": curBar['DateTimeStamp'],  # 时间戳（基准合约）
            "TradeDate": curBar['TradeDate'],  # 交易日（基准合约）
            "CurrentBarIndex": curBar['KLineIndex'],  # 当前K线索引
        }
        self._calcCenter.addOrder(orderParam)

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

    def getEnumColorRed(self):
        return 0xFF0000

    def getEnumColorGreen(self):
        return 0x00AA00

    def getEnumColorBlue(self):
        return 0x0000FF

    def getEnumColorPurple(self):
        return 0x9900FF

    def getEnumColorGray(self):
        return 0x999999

    #///////////////////////其他函数///////////////////////////
    def _addSeries(self, name, value, locator, color, barsback):
        addSeriesEvent = Event({
            "EventCode": EV_ST2EG_ADD_KLINESERIES,
            "StrategyId": self._strategy.getStrategyId(),
            "Data":{
                'ItemName':name,
                'Type': EEQU_INDICATOR,
                'Color': color,
                'Thick': 1,
                'OwnAxis': EEQU_ISNOT_AXIS,
                'Param': [],
                'ParamNum': 0,
                'Groupid': 0,
                'GroupName':name,
                'Main': EEQU_IS_MAIN,
            }
        })
        
        self._strategy.sendEvent2Engine(addSeriesEvent)
    
    def setPlotNumeric(self, name, value, locator, color, barsback):
        curBar = self._hisModel.getCurBar()

        # if self._strategy.isRealTimeStatus() and name == "MA_909_5":
        #     print("Real Time ************* :", "name: ", name, "value:", value)
        # if self._strategy.isRealTimeAsHisStatus() and name == "MA_909_5":
        #     print("Real Time As History*** :", "name: ", name, "value:", value)

        if name not in self._plotedDict:
            self._addSeries(name, value, locator, color, barsback)
            self._plotedDict[name] = (name, value, locator, color, barsback)

        data = [{
            'KLineIndex' : curBar['KLineIndex'],
            'Value'      : value
        }]
        if self._strategy.isRealTimeStatus() or self._strategy.isRealTimeAsHisStatus():
            eventCode = EV_ST2EG_UPDATE_KLINESERIES
        else:
            eventCode = EV_ST2EG_NOTICE_KLINESERIES
        serialEvent = Event({
            "EventCode" : eventCode,
            "StrategyId": self._strategy.getStrategyId(),
            "Data":{
                "SeriesName": name,
                "SeriesType": EEQU_INDICATOR,
                "IsMain"    : EEQU_IS_MAIN,
                "Count"     : len(data),
                "Data"      : data
            }
        })
        self._strategy.sendEvent2Engine(serialEvent)

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
            if data['TradeState'] == EEQU_TRADESTATE_CONTINUOUS:
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
        return self._calcCenter._getProfit()["LiquidateProfit"]

    def getNumEvenTrades(self):
        '''保本交易总手数'''
        # return self._calcCenter._getProfit()["EventTrade"]
        return 0

    def getNumLosTrades(self):
        '''亏损交易总手数'''
        # return self._calcCenter._getProfit()["LoseTrade"]
        return 0

    def getNumWinTrades(self):
        '''盈利交易的总手数'''
        # return self._calcCenter._getProfit()["WinTrade"]
        return 0

    def getNumAllTimes(self):
        '''开仓次数'''
        return self._calcCenter._getProfit()["AllTimes"]

    def getNumWinTimes(self):
        '''盈利次数'''
        return self._calcCenter._getProfit()["WinTimes"]

    def getNumLoseTimes(self):
        '''亏损次数'''
        return self._calcCenter._getProfit()["LoseTimes"]

    def getNumEventTimes(self):
        '''保本次数'''
        return self._calcCenter._getProfit()["EventTimes"]

    def getPercentProfit(self):
        '''盈利成功率'''
        winTimes = self._calcCenter._getProfit()["WinTimes"]
        allTimes = self._calcCenter._getProfit()["AllTimes"]
        return winTimes/allTimes if allTimes > 0 else 0

    def getTradeCost(self):
        '''交易产生的手续费'''
        return self._calcCenter._getProfit()["Cost"]

    def getTotalTrades(self):
        '''交易总开仓手数'''
        # return self._calcCenter._getProfit()["AllTrade"]
        return 0

class StrategyConfig(object):
    '''
    功能：策略配置模块
    参数：
    {
        'Contract' : (  #合约设置,第一个元素为基准合约
            'ZCE|F|SR|905', 
        ),
        
        'Trigger'  : {  #触发方式设置
            '1' : '201904016100001'  定时触发       ST_TRIGGER_TIMER
            '2' : 300                周期触发(毫秒) ST_TRIGGER_CYCLE
            '3' : None,              K线触发        ST_TRIGGER_KLINE
            '4' : None,              即时行情触发   ST_TRIGGER_SANPSHOT
            '5' : None,              交易触发       ST_TRIGGER_TRADE
        },
        
        'Sample'   : {  #样本设置
            'ZCE|F|SC|906'  :   {
                'KLineType'     : 'M',   K线类型
                'KLineSlice'    : 1,     K线周期

                'UseSample'     : True,  是否使用样本
                'KLineCount'    : 0,     K线数量
                'BeginTime'     : '',    起始日期， 目前支持到天
            }
            'KLineType'     : 'M',   K线类型
            'KLineSlice'    : 1,     K线周期
            'UseSample'     : True,  是否使用样本
            'KLineCount'    : 0,     K线数量
            'BeginTime'     : '',    起始日期， 目前支持到天
        },
        
        'RunMode'  : {  #运行模式
            'Simulate' : {
                'Continues' : True,  连续运行
            }
            'Actual'   : {
                'SendOrder' : '1'    发单模式,1-实时发单,2-K线完成后发单
            }
        },
        
        'Money'    : {   #资金设置
            'ET001'  : {    #资金账号
                'UserNo'    : 'ET001',
                'InitFunds' : '1000000'   初始资金
                'ZCE|F|SC|906'  :   {
                    'OrderQty'  : {
                        'Type'  : '1'-固定手数, '2'-固定资金，'3'-资金比例
                        'Count' : 设置的值
                    }
                    'Hedge'     : T-投机,B-套保,S-套利,M-做市
                    'MARGIN'    : {'Type':'F', 'Value':value} 'F'-固定值,'R'-比例
                    'OpenFee'   : {'Type':'F', 'Value':value} 开仓手续费
                    'CloseFee'  : {'Type':'F', 'Value':value} 平仓手续费
                    'CloseTodayFee' : {'Type':'F', 'Value':value} 平今手续费
                }
            }
        }
        
        'Limit'   : {   #下单限制
            'OpenTimes' : 1, 每根K线同向开仓次数(-1,1-100)
            'ContinueOpenTimes' :-1, (-1, 1-100)
            'OpenAllowClose' : True  开仓的当前K线不允许平仓
            'CloseAllowOpen' : True  平仓的当前K线不允许开仓
        }
        
        'Other' : None                
      }
    '''
    def __init__(self, argsDict):
        ret = self._chkConfig(argsDict)
        if ret > 0:
            raise Exception(ret)

        # self._metaData = self.convertArgsDict(argsDict)
        self._metaData = deepcopy(argsDict)
        
    def _chkConfig(self, argsDict):
        if 'Contract' not in argsDict:
            return 1
            
        if 'Trigger' not in argsDict:
            return 2
            
        if 'Sample' not in argsDict:
            return 3
            
        if 'RunMode' not in argsDict:
            return 4 
            
        if 'Money' not in argsDict:
            return 5
            
        if 'Limit' not in argsDict:
            return 6
            
        return 0

    def continues(self):
        runModeDict = self.getRunMode()
        
        #实盘默认继续运行
        if 'Actual' in runModeDict:
            return True
            
        if 'Simulate' in runModeDict:
            return runModeDict['Simulate']['Continues']
        
        return False

    def getConfig(self):
        return self._metaData

    def getBenchmark(self):
        '''获取基准合约'''
        return self._metaData['Contract'][0]

    def getTriggerContract(self):
        return self._metaData['Contract']

    def setBenchmark(self, benchmark):
        '''设置基准合约'''
        if not benchmark:
            return 0

        if not self._metaData['Contract']:
            self._metaData['Contract'] = (benchmark, )

        contList = list(self._metaData['Contract'])
        contList[0] = benchmark
        self._metaData['Contract'] = tuple(contList)
        
    def getContract(self):
        '''获取合约列表'''
        return self._metaData['Contract']

    def setContract(self, contTuple):
        '''设置合约列表'''
        if not contTuple or not isinstance(contTuple, tuple):
            return -1
        self._metaData['Contract'] = contTuple
        return 0

    def setUserNo(self, userNo):
        '''设置交易使用的账户'''
        if userNo:
            self._metaData['Money']['UserNo'] = userNo
            return 0
        return -1

    def getUserNo(self):
        '''获取交易使用的账户'''
        return self._metaData['Money']['UserNo']

    def getTrigger(self):
        '''获取触发方式'''
        return self._metaData['Trigger']

    def setTrigger(self, type, value):
        '''设置触发方式'''
        if type not in (1, 2, 3, 4, 5):
            return -1
        if type == 4 and value%100 != 0:
            return -1
        if type == 5 and isinstance(value, list):
            for timeStr in value:
                if len(timeStr) != 14 or not self.isVaildDate(timeStr, "%Y%m%d%H%M%S"):
                    return -1

        trigger = self._metaData['Trigger']
        if type == 1:
            trigger['KLine'] = True
        elif type == 2:
            trigger['SnapShot'] = True
        elif type == 3:
            trigger['Trade'] = True
        elif type == 4:
            trigger['Cycle'] = value
        elif value:
            trigger['Timer'] = value
        return 0

    def setSample(self, sampleType, sampleValue):
        '''设置样本数据'''
        if sampleType not in ('A', 'D', 'C', 'N'):
            return -1

        sample = self._metaData['Sample']

        # 使用所有K线
        if sampleType == 'A':
            self.setAllKTrueInSample(sample)
            return 0

        # 指定日期开始触发
        if sampleType == 'D':
            if not sampleValue or not isinstance(sampleValue, str):
                return -1
            if not self.isVaildDate(sampleValue, "%Y%m%d"):
                return -1
            self.setBarPeriodInSample(sampleValue, sample)
            return 0

        # 使用固定根数
        if sampleType == 'C':
            if not isinstance(sampleValue, int) or sampleValue <= 0:
                return -1
            self.setBarCountInSample(sampleValue, sample)
            return 0

        # 不执行历史K线
        if sampleType == 'N':
            self.setUseSample(False)
            return 0

        return -1

    def initSampleDict(self):
        sample = {
            'KLineType': 'D',
            'KLineSlice': 1,
            'KLineCount': 2000
        }
        return sample

    def getSample(self, contNo=''):
        '''获取样本数据'''
        if contNo in self._metaData['Sample']:
            return self._metaData['Sample'][contNo]
        return self._metaData['Sample']

    def getStartTime(self, contNo=''):
        '''获取回测起始时间'''
        if contNo in self._metaData['Sample']:
            if "BeginTime" in self._metaData['Sample'][contNo]:
                return self._metaData['Sample'][contNo]['BeginTime']
            else:
                return 0
        if "BeginTime" in self._metaData['Sample']:
            return self._metaData['Sample']['BeginTime']
        return 0

    def getKLineType(self):
        '''获取K线类型'''
        return self._metaData['Sample']['KLineType']

    def getKLineSlice(self):
        '''获取K线间隔'''
        return self._metaData['Sample']['KLineSlice']

    def setAllKTrueInSample(self, sample, setForSpread=False):
        if 'BeginTime' in sample:
            del sample['BeginTime']

        if 'KLineCount' in sample:
            del sample['KLineCount']

        sample['AllK'] = True
        if setForSpread:
            sample['UseSample'] = True
        else:
            self._metaData['RunMode']['Simulate']['UseSample'] = True

    def setBarPeriodInSample(self, beginDate, sample, setForSpread=False):
        '''设置起止时间'''
        if 'AllK' in sample:
            del sample['AllK']

        if 'KLineCount' in sample:
            del sample['KLineCount']

        sample['BeginTime'] = beginDate
        if setForSpread:
            sample['UseSample'] = True
        else:
            self._metaData['RunMode']['Simulate']['UseSample'] = True

    def setBarCountInSample(self, count, sample, setForSpread=False):
        '''设置K线数量'''
        if 'AllK' in sample:
            del sample['AllK']

        if 'BeginTime' in sample:
            del sample['BeginTime']

        sample['KLineCount'] = count
        if setForSpread:
            sample['UseSample'] = True
        else:
            self._metaData['RunMode']['Simulate']['UseSample'] = True

    def setUseSample(self, isUseSample):
        self._metaData['RunMode']['Simulate']['UseSample'] = isUseSample

    def setBarInterval(self, barType, barInterval, contNo=''):
        '''设置K线类型和K线周期'''
        if barType not in ('t', 'T', 'S', 'M', 'H', 'D', 'W', 'm', 'Y'):
            return -1
        if not contNo or contNo == self.getBenchmark():
            self._metaData['Sample']['KLineType'] = barType
            self._metaData['Sample']['KLineSlice'] = barInterval
            return 0

        if contNo not in self._metaData['Sample']:
            self._metaData['Sample'][contNo] = [{'KLineType' : barType, 'KLineSlice' : barInterval}, ]
            return 0

        isExist = False
        barList = self._metaData['Sample'][contNo]
        for barDict in barList:
            if barDict['KLineType'] == barType and barDict['KLineSlice'] == barInterval:
                isExist = True
                break
        if isExist:
            return 0

        barList.append({'KLineType': barType, 'KLineSlice': barInterval})
        return 0

    def getInitCapital(self, userNo=''):
        '''获取初始资金'''
        if userNo in self._metaData:
            return self._metaData['Money'][userNo]['InitFunds']
        return self._metaData['Money']['InitFunds']

    def setInitCapital(self, capital, userNo=''):
        '''设置初始资金'''
        if not userNo:
            self._metaData['Money']['InitFunds'] = capital
        if userNo not in self._metaData['Money']:
            self._metaData['Money'][userNo] = {'InitFunds': capital}
        else:
            self._metaData['Money'][userNo]['InitFunds'] = capital

    def getRunMode(self):
        '''获取运行模式'''
        return self._metaData['RunMode']

    def getMarginValue(self, contNo=''):
        '''获取保证金比例值'''
        if contNo in self._metaData['Money']:
            return self._metaData['Money'][contNo]['Margin']['Value']
        return self._metaData['Money']['Margin']['Value']

    def getMarginType(self, contNo=''):
        '''获取保证金类型'''
        if contNo in self._metaData['Money']:
            return self._metaData['Money'][contNo]['Margin']['Type']
        return self._metaData['Money']['Margin']['Type']

    def setMargin(self, type, value, contNo=''):
        '''设置保证金的类型及比例/额度'''
        if value < 0 or type not in (EEQU_FEE_TYPE_RATIO, EEQU_FEE_TYPE_FIXED):
            return -1

        if not contNo:
            self._metaData['Money']['Margin']['Value'] = value
            self._metaData['Money']['Margin']['Type'] = type
            return 0
        if contNo not in self._metaData['Money']:
            self._metaData['Money'][contNo] = self.initFeeDict()
        self._metaData['Money'][contNo]['Margin']['Value'] = value
        self._metaData['Money'][contNo]['Margin']['Type'] = type
        return 0

    def getRatioOrFixedFee(self, feeType, isRatio, contNo=''):
        '''获取 开仓/平仓/今平 手续费率或固定手续费'''
        if feeType not in ('OpenFee', 'CloseFee', 'CloseTodayFee'):
            return 0

        openFeeType = EEQU_FEE_TYPE_RATIO if isRatio else EEQU_FEE_TYPE_FIXED
        if contNo in self._metaData['Money']:
            return self._metaData['Money'][contNo][feeType]['Value'] if self._metaData['Money'][contNo][feeType]['Type'] == openFeeType else 0
        return self._metaData['Money'][feeType]['Value'] if self._metaData['Money'][feeType]['Type'] == openFeeType else 0

    def getOpenRatio(self, contNo=''):
        '''获取开仓手续费率'''
        return self.getRatioOrFixedFee('OpenFee', True, contNo)

    def getOpenFixed(self, contNo=''):
        '''获取开仓固定手续费'''
        return self.getRatioOrFixedFee('OpenFee', False, contNo)

    def getCloseRatio(self, contNo=''):
        '''获取平仓手续费率'''
        return self.getRatioOrFixedFee('CloseFee', True, contNo)

    def getCloseFixed(self, contNo=''):
        '''获取平仓固定手续费'''
        return self.getRatioOrFixedFee('CloseFee', False, contNo)

    def getCloseTodayRatio(self, contNo=''):
        '''获取今平手续费率'''
        return self.getRatioOrFixedFee('CloseTodayFee', True, contNo)

    def getCloseTodayFixed(self, contNo=''):
        '''获取今平固定手续费'''
        return self.getRatioOrFixedFee('CloseTodayFee', False, contNo)


    def setTradeFee(self, type, feeType, feeValue, contNo=''):
        if not contNo:
            self.setTradeFeeInMoneyDict(type, feeType, feeValue, self._metaData['Money'])
            return

        if contNo not in self._metaData['Money']:
            self._metaData['Money'][contNo] = self.initFeeDict()
        self.setTradeFeeInMoneyDict(type, feeType, feeValue, self._metaData['Money'][contNo])

    def setTradeFeeInMoneyDict(self, type, feeType, feeValue, moneyDict):
        typeMap = {
            'A': ('OpenFee', 'CloseFee', 'CloseTodayFee'),
            'O': ('OpenFee',),
            'C': ('CloseFee',),
            'T': ('CloseTodayFee',),
        }
        if type not in typeMap:
            return

        keyList = typeMap[type]
        for key in keyList:
            money = moneyDict[key]
            money['Type'] = feeType
            money['Value'] = feeValue

    def initFeeDict(self):
        keys = ('Margin', 'OpenFee', 'CloseFee', 'CloseTodayFee')
        initDict = {'Type': '', 'Value': 0}
        feeDict =  {
            'MinQty': 0,
            'OrderQty': {
                'Type': '',
                'Count': 0
            },
            'Hedge': '',
        }
        for k in keys:
            feeDict[k] = deepcopy(initDict)
        return feeDict

    def setTriggerCont(self, contNoTuple):
        self._metaData['TriggerCont'] = contNoTuple

    def getTriggerCont(self):
        if 'TriggerCont' in self._metaData:
            return self._metaData['TriggerCont']
        return None

    def setActual(self):
        self._metaData['RunMode']['Actual']['SendOrder2Actual'] = True

    # def setTradeMode(self, inActual, useSample, useReal):
    #     runMode = self._metaData['RunMode']
    #     if inActual:
    #         # 实盘运行
    #         runMode['Actual']['SendOrder2Actual'] = True
    #     else:
    #         # 模拟盘运行
    #         runMode['Simulate']['UseSample'] = useSample
    #         runMode['Simulate']['Continues'] = useReal

    def setOrderWay(self, type):
        if type not in (1, 2):
            return -1
        self._metaData['RunMode']['SendOrder'] = str(type)

    def setTradeDirection(self, tradeDirection):
        '''设置交易方向'''
        self._metaData["Other"]["TradeDirection"] = tradeDirection

    def setMinQty(self, minQty, contNo=''):
        '''设置最小下单量'''
        if not contNo:
            self._metaData["Money"]["MinQty"] = minQty
            return
        if contNo not in self._metaData['Money']:
            self._metaData['Money'][contNo] = self.initFeeDict()
        self._metaData["Money"]["MinQty"] = minQty

    def setHedge(self, hedge, contNo=''):
        '''设置投保标志'''
        if not contNo:
            self._metaData["Money"]["Hedge"] = hedge
        if contNo not in self._metaData['Money']:
            self._metaData['Money'][contNo] = self.initFeeDict()
        self._metaData["Money"][contNo]["Hedge"] = hedge

    def setSlippage(self, slippage):
        '''设置滑点损耗'''
        self._metaData['Other']['Slippage'] = slippage

    def getSlippage(self):
        '''滑点损耗'''
        return self._metaData['Other']['Slippage']

    def getSendOrder(self):
        return self._metaData['RunMode']['SendOrder']

    def hasKLineTrigger(self):
        return bool(self._metaData['Trigger']['KLine'])

    def hasTimerTrigger(self):
        return bool(self._metaData['Trigger']['Timer'])

    def hasCycleTrigger(self):
        return bool(self._metaData['Trigger']['Cycle'])

    def hasSnapShotTrigger(self):
        return bool(self._metaData['Trigger']['SnapShot'])

    def hasTradeTrigger(self):
        return bool(self._metaData['Trigger']['Trade'])

    def isActualRun(self):
        return bool(self._metaData['RunMode']['Actual']['SendOrder2Actual'])

    def isVaildDate(self, date, format):
        try:
            time.strptime(date, format)
            return True
        except:
            return False

    def getLimit(self):
        return self._metaData['Limit']

class BarInfo(object):
    def __init__(self, logger):
        self._logger = logger
        self._barList = []
        self._curBar = None
        
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

    def getCurBar(self):
        return self._curBar

    def getBarOpen(self):
        return self._getBarValue('OpeningPrice')
        
    def getBarClose(self):
        return self._getBarValue('LastPrice')

    def getBarOpenInt(self):
        return self._getBarValue('PositionQty')

    def getBarHigh(self):
        return self._getBarValue('HighPrice')
        
    def getBarLow(self):
        return self._getBarValue('LowPrice')
        
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
    def __init__(self, strategy, config, calc):
        # K线数据定义
        # response data
        self._metaData = {}
        self._curEarliestKLineDateTimeStamp = {}
        self._lastEarliestKLineDateTimeStamp = {}
        self._pkgEarliestKLineDateTimeStamp = {}
        # 请求的 k线数量够了，
        self._hisLength = {}

        self._kLineNoticeData = {}

        self._strategy = strategy
        self.logger = strategy.logger
        self._config = config
        self._calc = calc
        
        # 运行位置的数据
        # 和存储位置的数据不一样，存储的数据 >= 运行的数据。
        self._curBarDict = {}
            
        # 请求次数，用于连续请求
        self._reqKLineTimes = 1

        # 按日期请求
        self._reqByDate = False
        self._reqBeginDate = 0

        # 上次时间戳
        self._lastTimestamp = 0
        
        # 回测阶段的实时K线数据,不出指标和信号
        self._reportRealDataList = []
        self._isAfterReportFirstData = True

        #
        self._realTimeAsHistoryKLineCnt = 0

    def initialize(self):
        self._contractTuple = self._config.getContract()
        
        # 基准合约
        self._contractNo = self._contractTuple[0]

        # 回测样本配置
        self._sampleDict = self._config.getSample()
        
        self._useSample = self._config.getRunMode()["Simulate"]["UseSample"]
        
        # 触发方式配置
        self._triggerDict = self._config.getTrigger()
        
        # Bar
        rspKLineReady = not bool(self._useSample)
        for contractNo in self._contractTuple:
            self._curBarDict[contractNo] = BarInfo(self.logger)
            self._metaData[contractNo] = {
                'KLineReady': rspKLineReady,
                'KLineType': '',
                'KLineSlice': 1,
                'KLineData': []
            }
            self._kLineNoticeData[contractNo] = {
                'KLineType': '',
                'KLineSlice': 1,
                'KLineReady': True,
                'KLineData': [],
            }
            self._hisLength[contractNo] = 0
            self._pkgEarliestKLineDateTimeStamp[contractNo] = -1
            self._curEarliestKLineDateTimeStamp[contractNo] = sys.maxsize
            self._lastEarliestKLineDateTimeStamp[contractNo] = -1

    # //////////////`////////////////////////////////////////////////////
    def getBeginDate(self):
        data = self._metaData[self._contractNo]['KLineData']
        return str(data[0]['TradeDate'])

    def getEndDate(self):
        data = self._metaData[self._contractNo]['KLineData']
        return str(data[-1]['TradeDate'])

    def getHisLength(self):
        return self._hisLength
    # ////////////////////////BaseApi类接口////////////////////////
    def getBarOpenInt(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._metaData:
            return []

        return self._curBarDict[contNo].getBarOpenInt()

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

    def getLastStoredKLine(self, contractNo):
        noticeKLineDatas = self._kLineNoticeData[contractNo]["KLineData"]
        rspKLineDatas = self._metaData[contractNo]["KLineData"]
        if len(noticeKLineDatas) > 0:
            return noticeKLineDatas[-1], KLineFromRealTime
        elif len(rspKLineDatas)>0:
            return rspKLineDatas[-1], KLineFromHis
        else:
            return None, None

    def setLastStoredKLineStable(self, contractNo):
        noticeKLineDatas = self._kLineNoticeData[contractNo]["KLineData"]
        rspKLineDatas = self._metaData[contractNo]["KLineData"]
        if len(noticeKLineDatas) > 0:
            noticeKLineDatas[-1]["IsKLineStable"] = True
        elif len(rspKLineDatas) > 0:
            rspKLineDatas[-1]["IsKLineStable"] = True
        else:
            pass

    def getLastRunKLine(self, contractNo):
        assert contractNo in self._curBarDict, "error"
        barManager = self._curBarDict[contractNo]
        return barManager.getCurBar()

    def getBarTradeDate(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._metaData:
            return 0

        curBar = self._curBarDict[contNo].getCurBar()
        return curBar['TradeDate']

    def getBarCount(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._metaData:
            return 0

        kLineHisData = self._metaData[contNo]['KLineData']

        if contNo not in self._kLineNoticeData:
            return len(kLineHisData)

        kLineNoticeData = self._kLineNoticeData[contNo]['KLineData']
        if len(kLineNoticeData) == 0:
            return len(kLineHisData)

        lastHisBar = kLineHisData[-1]
        lastNoticeBar = kLineNoticeData[-1]

        return len(kLineHisData) + (lastNoticeBar['KLineIndex'] - lastHisBar['KLineIndex'])

    def getBarStatus(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return -1

        curBar = self._curBarDict[contNo].getCurBar()
        curBarIndex = curBar['KLineIndex']
        firstHisBarIndex = self._metaData[contNo]['KLineData'][0]['KLineIndex']
        lastHisBarIndex = self._metaData[contNo]['KLineData'][-1]['KLineIndex']

        if contNo not in self._kLineNoticeData or len(self._kLineNoticeData[contNo]['KLineData']) == 0:
            # 仅有历史K线
            if curBarIndex == firstHisBarIndex:
                return 0
            elif curBarIndex < lastHisBarIndex:
                return 1
            elif curBarIndex == lastHisBarIndex:
                return 2

        # 既有历史K线，又有实时K线
        lastNoticeBarIndex = self._kLineNoticeData[contNo]['KLineData'][-1]['KLineIndex']

        if curBarIndex == firstHisBarIndex:
            return 0
        elif curBarIndex >= lastNoticeBarIndex:
            return 2
        else:
            return 1

    def isHistoryDataExist(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return False

        return True if len(self._metaData[contNo]) else False

    def getBarDate(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return 0
        curBar = self._curBarDict[contNo].getCurBar()
        return (curBar['DateTimeStamp']//1000000000)

    def getBarTime(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return 0
        curBar = self._curBarDict[contNo].getCurBar()
        return (curBar['DateTimeStamp']%1000000000)/1000000000

    def getBarOpen(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return 0
        return self._curBarDict[contNo].getBarOpen()
        
    def getBarClose(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return 0
        return self._curBarDict[contNo].getBarClose()

    def getBarVol(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return 0

        curBar = self._curBarDict[contNo].getCurBar()
        return curBar['TotalQty']
        
    def getBarHigh(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return 0
        return self._curBarDict[contNo].getBarHigh()
        
    def getBarLow(self, contNo):
        if contNo == '':
            contNo = self._contractNo

        if contNo not in self._curBarDict:
            return 0
        return self._curBarDict[contNo].getBarLow()
        
    #////////////////////////参数设置类接口///////////////////////
        
    def _getKLineType(self):
        if not self._sampleDict:
            return None
        return self._sampleDict['KLineType']
        
    def _getKLineSlice(self):
        if not self._sampleDict:
            return None
        return self._sampleDict['KLineSlice']
        
    def _getKLineCount(self):
        if not self._useSample:
            return 1

        if 'KLineCount' in self._sampleDict:
            return self._sampleDict['KLineCount']

        if 'BeginTime' in self._sampleDict:
            return self._sampleDict['BeginTime']

        if 'AllK' in self._sampleDict:
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
    def reqKLinesByCount(self, contNo, count, notice):
        # print("请求k线", contNo, count)
        # 请求历史K线阶段先不订阅    
        event = Event({
            'EventCode'   : EV_ST2EG_SUB_HISQUOTE,
            'StrategyId'  : self._strategy.getStrategyId(),
            'ContractNo'  : contNo,
            'Data'        : {
                    'ReqCount'   :  count,
                    'ContractNo' :  contNo,
                    'KLineType'  :  self._getKLineType(),
                    'KLineSlice' :  self._getKLineSlice(),
                    'NeedNotice' :  EEQU_NOTICE_NEED
                },
            })
            
        self._strategy.sendEvent2Engine(event)

        # 请求历史k线，
        # 可能同时请求即时k线
    def reqAndSubQuote(self):
        '''向9.5请求所有合约历史数据'''
        count, countOrDate = 0, self._getKLineCount()

        # print(" count or date is ", countOrDate)
        if isinstance(countOrDate, int):
            count = countOrDate
            self._reqByDate = False
        else:
            self._reqByDate = True
            self._reqByDateEnd = False

            dateTimeStampLength = len("20190326143100000")
            self._reqBeginDate = int(countOrDate + (dateTimeStampLength - len(countOrDate)) * '0')
            count = self._reqKLineTimes * 4000

        for contNo in self._contractTuple:
            # req by count
            if not self._reqByDate:
                self.reqKLinesByCount(contNo, count, EEQU_NOTICE_NEED)
            # req by date
            else:
                self.reqKLinesByCount(self._contractNo, count, EEQU_NOTICE_NOTNEED)

    def _handleKLineRspData(self, event):
        contractNo = event.getContractNo()
        self._insertHisRspData(event)
        if self.isHisQuoteRspEnd(event):
            # print(contractNo," end ***************")
            self._reIndexHisRspData(contractNo)
            self._hisLength[contractNo] = len(self._metaData[contractNo]["KLineData"])

    # 当 not self._reqByDateEnd时，更新
    def _updateRspDataRefDTS(self, event):
        assert self._reqByDate and not self._reqByDateEnd, "error"
        dataList = event.getData()
        contractNo = event.getContractNo()
        # update current package earliest KLine DateTimeStamp
        if len(dataList) == 0:
            pass
        else:
            self._pkgEarliestKLineDateTimeStamp[contractNo] = dataList[-1]["DateTimeStamp"]
        # update current req earliest KLine DateTimeStamp
        if event.isChainEnd() and self._pkgEarliestKLineDateTimeStamp[contractNo]<self._curEarliestKLineDateTimeStamp[contractNo]:
            self._curEarliestKLineDateTimeStamp[contractNo] = self._pkgEarliestKLineDateTimeStamp[contractNo]

    def _handleKLineRspByDate(self, event):
        contractNo = event.getContractNo()
        if not self._reqByDateEnd:
            self._insertHisRspData(event)
            self._updateRspDataRefDTS(event)
            if event.isChainEnd():
                self._isReqByDateContinue(event)
        else:
            self._handleKLineRspData(event)

    def _isReqByDateContinue(self,  event):
        contractNo = event.getContractNo()
        # req by date end or continue
        # enough data
        if not event.isChainEnd():
            return
        elif self._curEarliestKLineDateTimeStamp[contractNo] <= self._reqBeginDate:
            self._reqByDateEnd = True
            self.reqKLinesByCount(contractNo, self._reqKLineTimes * 4000, EEQU_NOTICE_NEED)
        # 9.5 lack data
        elif self._curEarliestKLineDateTimeStamp[contractNo] == self._lastEarliestKLineDateTimeStamp[contractNo]:
            self._reqByDateEnd = True
            self.reqKLinesByCount(contractNo, self._reqKLineTimes * 4000, EEQU_NOTICE_NEED)
        # local lack data
        elif self._curEarliestKLineDateTimeStamp[contractNo] > self._reqBeginDate:
            self._reqKLineTimes += 1
            self.reqKLinesByCount(contractNo, self._reqKLineTimes * 4000, EEQU_NOTICE_NOTNEED)
            self._lastEarliestKLineDateTimeStamp[contractNo] = self._curEarliestKLineDateTimeStamp[contractNo]
        else:
            raise IndexError("can't be this case")

    def _handleKLineRspByCount(self, event):
        self._handleKLineRspData(event)

    # response 数据
    def onHisQuoteRsp(self, event):
        if not self._reqByDate:                     # req by count
            self._handleKLineRspByCount(event)
        else:                                       # req by date
            self._handleKLineRspByDate(event)

    def isHisQuoteRspEnd(self, event):
        if event.isChainEnd() and not self._reqByDate:
            return True
        if event.isChainEnd() and self._reqByDate and self._reqByDateEnd:
            return True
        return False

    # 更新response 数据
    def _insertHisRspData(self, event):
        contNo = event.getContractNo()

        dataDict = self._metaData[contNo]
        dataDict['KLineType'] = event.getKLineType()
        dataDict['KLineSlice'] = event.getKLineSlice()
        rfdataList = dataDict['KLineData']

        dataList = event.getData()
        # print("datalist is ", dataList)
        for kLineData in dataList:
            if self._reqByDate:
                if len(rfdataList) == 0 or (len(rfdataList) >= 1 and kLineData["DateTimeStamp"] < rfdataList[0]["DateTimeStamp"] and \
                    kLineData["DateTimeStamp"] >= self._reqBeginDate):
                    rfdataList.insert(0, kLineData)
            else:
                if len(rfdataList) == 0 or (len(rfdataList) >= 1 and kLineData["DateTimeStamp"] < rfdataList[0]["DateTimeStamp"]):
                    rfdataList.insert(0, kLineData)

    def _reIndexHisRspData(self, contractNo):
        dataDict = self._metaData[contractNo]
        rfdataList = dataDict['KLineData']
        dataDict['KLineReady'] = True
        for i, record in enumerate(rfdataList):
            rfdataList[i]['KLineIndex'] = i+1
            
    def _afterReportRealData(self, contNo):
        '''回测结束后，先发送回测阶段收到的实时数据，不发单'''
        for data in self._reportRealDataList:
            event = Event({
                "EventCode": ST_TRIGGER_FILL_DATA,
                "ContractNo": contNo,
                "Data":data
            })
            
            self._strategy.sendTriggerQueue(event)

    def _handleKLineNoticeData(self, localStoreList, event):
        apiDataList = event.getData()
        contractNo = event.getContractNo()
        # notice数据，直接加到队尾
        for data in apiDataList:
            data["IsKLineStable"] = False
            storedLastKLine, lastKLineSource = self.getLastStoredKLine(contractNo)
            # 没有数据，索引取回测数据的最后一条数据的索引，没有数据从1开始
            if storedLastKLine is None:
                data["KLineIndex"] = 1
                localStoreList.append(data)
            else:
                lastKLineIndex = storedLastKLine["KLineIndex"]
                lastKLineDTS = storedLastKLine["DateTimeStamp"]
                if lastKLineDTS == data["DateTimeStamp"]:
                    data["KLineIndex"] = lastKLineIndex
                    self._handleSameKLine(localStoreList, data , lastKLineSource, contractNo)
                else:
                    data["KLineIndex"] = lastKLineIndex+1
                    self.setLastStoredKLineStable(contractNo)
                    localStoreList.append(data)
            # print(storedLastKLine["KLineIndex"], storedLastKLine["DateTimeStamp"], self._metaData[contractNo]["KLineData"][-1]["DateTimeStamp"])
            # 发送实时k线
            self._sendRealTimeKLine(data, contractNo)
            # 处理触发
            if len(localStoreList) >= 2:
                self._handleRealTimeKLineTrigger(contractNo, localStoreList[-2])
                self._handleRealTimeKLineTrigger(contractNo, localStoreList[-1])
            elif len(localStoreList) == 1:
                self._handleRealTimeKLineTrigger(contractNo, localStoreList[-1])
            else:
                raise ValueError

    def _handleSameKLine(self, localStoreList, data , lastKLineSource, contractNo):
        if lastKLineSource == KLineFromHis:
            # todo 处理 历史k线最后一根,
            localStoreList.append(data)
        elif lastKLineSource == KLineFromRealTime:
            localStoreList[-1] = data

    def _sendRealTimeKLine(self, data, contNo):
        if contNo != self._contractNo:
            return

        # 跑历史回测期间，到来的实时数据只有稳定后才填充，并且按照历史触发。
        if self._strategy.isHisStatus():
            if not data["IsKLineStable"]:
                return
            else:
                status = ST_STATUS_CONTINUES_AS_HISTORY
                self._realTimeAsHistoryKLineCnt += 1
        else:
            status = ST_STATUS_CONTINUES_AS_REALTIME
        event = Event({
            "EventCode": ST_TRIGGER_FILL_DATA,
            "ContractNo": contNo,
            "Data": {
                "Data": data,
                "Status": status
            }
        })
        self._strategy.sendTriggerQueue(event)

    def _handleRealTimeKLineTrigger(self, contractNo, data):
        if contractNo != self._contractNo:
            return
        orderWay = str(self._config.getSendOrder())
        kLineTrigger = self._config.hasKLineTrigger()
        if orderWay == SendOrderRealTime and kLineTrigger and not data["IsKLineStable"]:
            event = Event({
                'EventCode': ST_TRIGGER_KLINE,
                'ContractNo': contractNo,
                'Data': data
            })
            self._strategy.sendTriggerQueue(event)

        if orderWay == SendOrderStable and kLineTrigger and data["IsKLineStable"]:
            event = Event({
                'EventCode': ST_TRIGGER_KLINE,
                'ContractNo': contractNo,
                'Data': data,
            })
            self._strategy.sendTriggerQueue(event)

    def onHisQuoteNotice(self, event):
        contNo = event.getContractNo()
        if self._useSample and (contNo not in self._metaData or not self._metaData[contNo]["KLineReady"]):
            # raise ValueError, todo, error handle
            return

        kLineTrigger = self._config.hasKLineTrigger()
        dataDict = self._kLineNoticeData[contNo]
        dataDict['KLineType'] = event.getKLineType()
        dataDict['KLineSlice'] = event.getKLineSlice()
        localStoreList = dataDict['KLineData']
        self._handleKLineNoticeData(localStoreList, event)

    # ///////////////////////////回测接口////////////////////////////////
    def _isAllReady(self):
        if not self._useSample:
            return True
        for contractNo in self._config.getContract():
            if contractNo not in self._metaData or not self._metaData[contractNo]["KLineReady"]:
                return False
        return True

    def _switchKLine(self, contNo):
        event = Event({
            "EventCode" :EV_ST2EG_SWITCH_STRATEGY,
            'StrategyId': self._strategy.getStrategyId(),
            'Data':
                {
                    'StrategyName': self._strategy.getStrategyName(),
                    'ContractNo'  : contNo,
                    'KLineType'   : self._getKLineType(),
                    'KLineSlice'  : self._getKLineSlice(),
                }
        })
        
        self._strategy.sendEvent2Engine(event)
        
    def _addKLine(self, data):
        event = Event({
            "EventCode"  : EV_ST2EG_NOTICE_KLINEDATA,
            "StrategyId" : self._strategy.getStrategyId(),
            "KLineType"  : self._getKLineType(),
            "Data": {
                'Count'  : 1,
                "Data"   : [data,],
            }
        })
        # print("历史回测阶段:", data["KLineIndex"])
        self._strategy.sendEvent2Engine(event)
        
    def _addSignal(self):
        event = Event({
            "EventCode"  :EV_ST2EG_ADD_KLINESIGNAL,
            'StrategyId' :self._strategy.getStrategyId(),
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
    
    def _updateCurBar(self, contNo, data):
        '''更新当前Bar值'''
        self._curBarDict[contNo].updateBar(data)
        
    def _updateOtherBar(self, otherContractDatas):
        '''根据指定合约Bar值，更新其他合约bar值'''
        for otherContract, otherContractData in otherContractDatas.items():
            if otherContract not in self._curBarDict:
                self._curBarDict[otherContract] = BarInfo(self.logger)
            self._curBarDict[otherContract].updateBar(otherContractData)
    
    # def _afterBar(self, contractNos, barInfos):
        # self._calc.calcProfit(contractNos,barInfos)
        #result = self._calc.getMonResult()
        # result.update({
            # "StrategyName":self._strategy.getStrategyName(),
            # "Status":ST_STATUS_HISTORY,
        # })
        # event = Event({
            # "EventCode":EV_EG2ST_MONITOR_INFO,
            # "StrategyId":self._strategy.getStrategyId(),
            # "Data":result
        # })
        # self._strategy.sendEvent2Engine(event)
        
    def _sendFlushEvent(self):
        event = Event({
            "EventCode": EV_ST2EG_UPDATE_STRATEGYDATA,
            "StrategyId": self._strategy.getStrategyId(),
        })
        self._strategy.sendEvent2Engine(event)
        
    def getCurBar(self, contNo = ''):
        if contNo == '':
            contNo = self._contractNo
        return self._curBarDict[contNo].getCurBar()
        
    def runReport(self, context, handle_data):
        '''历史回测接口'''
        # 不使用历史K线，也需要切换
        # 切换K线
        self._switchKLine(self._contractNo)
        # 增加信号线
        self._addSignal()
        self._sendFlushEvent()

        if not self._useSample:
            return

        while not self._isAllReady():
            time.sleep(1)

        # ==============使用基准合约回测==================
        baseContractData = self._metaData[self._contractNo]['KLineData']
        self.logger.info('[runReport] run report begin')

        contractList = list(self._config.getContract())
        beginIndex = 0
        for i, data in enumerate(baseContractData):
            # todo 过滤最后一根k线，不过滤的话，会出现 k线稳定发单在交界处异常。
            # 更新当前Bar
            self._updateCurBar(self._contractNo, data)
            # # 根据基准合约，更新其他Bar
            # otherContractDatas = {}
            # # 填入基准合约bar info
            # otherContractDatas.update({self._contractNo:data})
            # 执行策略函数。历史回测期间, 按照k线最新价计算浮动盈亏, 过滤在sendOrder里面过滤
            if self._strategy._isExit():
                break
            if not self._config.hasKLineTrigger():
                continue
            self._strategy.setTriggerType(ST_TRIGGER_HIS_KLINE)
            handle_data(context)
            self._calcProfitWhenHis()
            if i%200==0:
                self.drawBatchHisKine(baseContractData[beginIndex:i+1])
                beginIndex = i+1
            elif i == len(baseContractData)-1:
                self.drawBatchHisKine(baseContractData[beginIndex:])

        self.logger.debug('[runReport] run report completed!')
        # 回测完成，刷新信号、指标
        self._sendFlushEvent()
        # print('**************************** run his end')

    def _calcProfitWhenHis(self):
        priceInfos = {}
        for contractNo in self._contractTuple:
            curContractBar = self._curBarDict[contractNo].getCurBar()
            priceInfos[contractNo] = {
                "TradeDate": curContractBar["TradeDate"],
                "DateTimeStamp": curContractBar["DateTimeStamp"],
                "LastPrice": curContractBar["LastPrice"],  # filed mean = 4,表示 LastPrice
                "LastPriceSource": LastPriceFromKLine
        }
        # self._calc.calcProfit(priceInfos)
        contractNos = list(self._contractTuple)
        self._calc.calcProfit(contractNos, priceInfos)

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

    # 即时行情变了，重新计算盈利。
    def calcProfitByQuote(self, priceInfos):
        contractNos = list(self._contractTuple)
        self._calc.calcProfit(contractNos, priceInfos)

    # 填充实时k线
    def runReportRealTime(self, context, handle_data, event):
        '''发送回测阶段来的数据'''
        assert event.getContractNo() == self._contractNo, "error ,only base contract can update k line "
        data = event.getData()["Data"]
        self._strategy.setRunRealTimeStatus(event.getData()["Status"])
        # print("status = ", event.getData()["Status"])
        contractList = list(self._config.getContract())

        # 更新当前bar数据
        self._updateCurBar(self._contractNo, data)
        # 更新其他bar
        # otherContractDatas = {}
        # otherContractDatas.update({self._contractNo: data})

        # 当作历史回测阶段
        if self._strategy.isRealTimeAsHisStatus():
            self.runVirtualReport(context, handle_data, event)
            self._realTimeAsHistoryKLineCnt -= 1
        elif self._strategy.isRealTimeStatus():
            # 推送基准合约K线
            self._updateRealTimeKLine(data)
        else:
            raise ValueError
        # print(self._strategy.isRealTimeStatus(), self._strategy._runStatus, self._strategy._runRealTimeStatus, self._strategy.isRealTimeAsHisStatus())
        self._sendFlushEvent()

    def runVirtualReport(self,context, handle_data, event):
        if self._config.hasKLineTrigger():
            data = event.getData()["Data"]
            self._addKLine(data)
            self._strategy.setTriggerType(ST_TRIGGER_HIS_KLINE)
            handle_data(context)

    # ST_STATUS_CONTINUES_AS_REALTIME 阶段
    def runRealTime(self, context, handle_data, event):
        contractList = list(self._config.getContract())
        contNo = event.getContractNo()
        data = event.getData()
        eventCode = event.getEventCode()

        if not self._strategy.isRealTimeStatus():
            return
        # print(self._strategy.isRealTimeStatus(), contNo == self._contractNo, self._strategy._runStatus, self._strategy._runRealTimeStatus)
        # assert self._strategy.isRealTimeStatus(), "error "

        if not self._strategy.isRealTimeStatus():
            return
        assert contNo == self._contractNo, "error "

        if eventCode == ST_TRIGGER_KLINE:
            # 更新当前bar数据
            self._updateCurBar(contNo, data)
            if self._config.hasKLineTrigger():
                # print("实时k线触发")
                self._strategy.setTriggerType(eventCode)
                handle_data(context)
        elif eventCode == ST_TRIGGER_TIMER and self._config.hasTimerTrigger():
            # print("定时触发")
            self._strategy.setTriggerType(eventCode)
            handle_data(context)
        elif eventCode == ST_TRIGGER_CYCLE and self._config.hasCycleTrigger():
            # print("循环触发")
            self._strategy.setTriggerType(eventCode)
            handle_data(context)
        elif eventCode == ST_TRIGGER_SANPSHOT and self._config.hasSnapShotTrigger():
            self._strategy.setTriggerType(eventCode)
            handle_data(context)
        elif eventCode == ST_TRIGGER_TRADE and self._config.hasTradeTrigger():
            self._strategy.setTriggerType(eventCode)
            handle_data(context)
        self._sendFlushEvent()

        assert eventCode in [ST_TRIGGER_KLINE, ST_TRIGGER_TRADE, ST_TRIGGER_SANPSHOT, ST_TRIGGER_TIMER, ST_TRIGGER_CYCLE], "Error "

    def _updateRealTimeKLine(self, data):
        event = Event({
            "EventCode": EV_ST2EG_UPDATE_KLINEDATA,
            "StrategyId": self._strategy.getStrategyId(),
            "KLineType": self._getKLineType(),
            "Data": {
                'Count': 1,
                "Data": [data, ],
            }
        })
        self._strategy.sendEvent2Engine(event)


class StrategyQuote(QuoteModel):
    '''即时行情数据模型'''
    def __init__(self, strategy, config):
        '''
        self._exchangeData  = {}  #{key=ExchangeNo,value=ExchangeModel}
        self._commodityData = {}  #{key=CommodityNo, value=CommodityModel}
        self._contractData  = {}  #{key=ContractNo, value=QuoteDataModel}
        '''
        self._strategy = strategy
        self.logger = strategy.logger
        QuoteModel.__init__(self, self.logger)
        self._config = config
        
    def initialize(self):
        self._contractTuple = self._config.getContract()
        
    def subQuote(self):
        contList = []
        for cno in self._contractTuple:
            contList.append(cno)

        event = Event({
            'EventCode'   : EV_ST2EG_SUB_QUOTE,
            'StrategyId'  : self._strategy.getStrategyId(),
            'Data'        : contList,
        })
            
        self._strategy.sendEvent2Engine(event) 

    def reqExchange(self):
        event = Event({
            'EventCode': EV_ST2EG_EXCHANGE_REQ,
            'StrategyId': self._strategy.getStrategyId(),
            'Data': '',
        })

        self._strategy.sendEvent2Engine(event)

    def reqCommodity(self):
        event = Event({
            'EventCode'   : EV_ST2EG_COMMODITY_REQ, 
            'StrategyId'  : self._strategy.getStrategyId(),
            'Data'        : '',
        })
        
        self._strategy.sendEvent2Engine(event)

    # /////////////////////////////应答消息处理///////////////////
    def onExchange(self, event):
        dataDict = event.getData()
        for k, v in dataDict.items():
            self._exchangeData[k] = ExchangeModel(self.logger, v)


    def onCommodity(self, event):
        dataDict = event.getData()
        for k, v in dataDict.items():
            self._commodityData[k] = CommodityModel(self.logger, v)

    def onQuoteRsp(self, event):
        '''
        event.Data = {
            'ExchangeNo' : dataDict['ExchangeNo'],
            'CommodityNo': dataDict['CommodityNo'],
            'UpdateTime' : 20190401090130888, # 时间戳
            'Lv1Data'    : {                  # 普通行情
                '0'      : 5074,              # 昨收盘
                '1'      : 5052,              # 昨结算
                '2'      : 269272,            # 昨持仓
                '3'      : 5067,              # 开盘价
                '4'      : 5084,              # 最新价
                ...
                '126'    : 1                  # 套利行情系数
                },
            'Lv2BidData' :[
                5083,                         # 买1
                5082,                         # 买2
                5082,                         # 买3
                5080,                         # 买4
                5079,                         # 买5
            ],
            'Lv2AskData':[
                5084,                         # 卖1
                5085,                         # 卖2
                5086,                         # 卖3
                5087,                         # 卖4
                5088,                         # 卖5
            ]
        }
        '''
        data = event.getData()

        if not isinstance(type(data), dict):
            return

        contractNo = apiEvent.getContractNo()
        if contractNo not in self._contractData:
            contMsg = {
                'ExchangeNo': data['ExchangeNo'],
                'CommodityNo': data['CommodityNo'],
                'ContractNo': contractNo,
            }
            self._contractData[contractNo] = QuoteDataModel(self.logger, contMsg)

        self._contractData[contractNo]._metaData = data

    def onQuoteNotice(self, event):
        QuoteModel.updateLv1(self, event)

    def onDepthNotice(self, event):
        QuoteModel.updateLv2(self, event)

    def getLv1DataAndUpdateTime(self, contNo):
        if not contNo:
            return
        if contNo in self._contractData:
            metaData = self._contractData[contNo]._metaData
            resDict = { 'UpdateTime' : metaData['UpdateTime'],
                       'Lv1Data' : deepcopy(metaData['Lv1Data'])
            }
            return resDict

    # ////////////////////////即时行情////////////////////////////
    # 参数验装饰器
    def paramValidatorFactory(abnormalRet):
        def paramValidator(func):
            def validator(*args, **kwargs):
                if len(args) == 0:
                    return abnormalRet
                if len(args) == 1:
                    return func(*args, **kwargs)

                model = args[0]
                contNo = args[1]
                if not contNo:
                    contNo = model._config.getBenchmark()

                if contNo not in model._contractData:
                    return abnormalRet
                elif not isinstance(model._contractData[contNo], QuoteDataModel):
                    return abnormalRet

                if len(args) == 2:
                    return func(model, contNo)

                if len(args) == 3:
                    if args[2] > 10:
                        return abnormalRet
                    return func(model, contNo, args[2])
            return validator
        return paramValidator

    # 合约最新卖价
    @paramValidatorFactory(0)
    def getQAskPrice(self, contNo, level=1):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][17]

        lv2AskData = quoteDataModel._metaData["Lv2AskData"]
        if (level > len(lv2AskData)) or (not isinstance(lv2AskData[level-1], dict)):
            return 0

        return lv2AskData[level-1].get('Price')

    # 卖盘价格变化标志
    @paramValidatorFactory(0)
    def getQAskPriceFlag(self, contNo):
        # TODO: 增加卖盘价格比较逻辑
        return 1

    # 合约最新卖量
    @paramValidatorFactory(0)
    def getQAskVol(self, contNo, level=1):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][18]

        lv2AskData = quoteDataModel._metaData["Lv2AskData"]
        if (level > len(lv2AskData)) or (not isinstance(lv2AskData[level - 1], dict)):
            return 0

        return lv2AskData[level - 1].get('Qty')

    # 实时均价即结算价
    @paramValidatorFactory(0)
    def getQAvgPrice(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][15]

    # 合约最新买价
    @paramValidatorFactory(0)
    def getQBidPrice(self, contNo, level):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][19]

        lv2BidData = quoteDataModel._metaData["Lv2BidData"]
        if (level > len(lv2BidData)) or (not isinstance(lv2BidData[level-1], dict)):
            return 0

        return lv2BidData[level-1].get('Price')

    # 买价变化标志
    @paramValidatorFactory(0)
    def getQBidPriceFlag(self, contNo):
        # TODO: 增加买价比较逻辑
        return 1

    # 指定合约,指定深度的最新买量
    @paramValidatorFactory(0)
    def getQBidVol(self, contNo, level):
        quoteDataModel = self._contractData[contNo]
        if level == 1:
            return quoteDataModel._metaData["Lv1Data"][20]

        lv2BidData = quoteDataModel._metaData["Lv2BidData"]
        if (level > len(lv2BidData)) or (not isinstance(lv2BidData[level - 1], dict)):
            return 0

        return lv2BidData[level - 1].get('Qty')

    # 当日收盘价，未收盘则取昨收盘
    @paramValidatorFactory(0)
    def getQClose(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][0] if quoteDataModel._metaData["Lv1Data"][14] == 0 else quoteDataModel._metaData["Lv1Data"][14]

    # 当日最高价
    @paramValidatorFactory(0)
    def getQHigh(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][5]

    # 历史最高价
    @paramValidatorFactory(0)
    def getQHisHigh(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][7]

    # 历史最低价
    @paramValidatorFactory(0)
    def getQHisLow(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][8]

    # 内盘量，买入价成交为内盘
    @paramValidatorFactory(0)
    def getQInsideVol(self, contNo):
        # TODO: 计算买入价成交量逻辑
        return 0

    # 最新价
    @paramValidatorFactory(0)
    def getQLast(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][4]

    # 最新成交日期
    @paramValidatorFactory(None)
    def getQLastDate(self, contNo):
        # TODO: 获取最新成交日期逻辑
        return None

    # 最新价变化标志
    @paramValidatorFactory(0)
    def getQLastFlag(self, contNo):
        # TODO: 增加最新价和次最新价比较逻辑
        return 1

    # 最新成交时间
    @paramValidatorFactory(0)
    def getQLastTime(self, contNo):
        # TODO: 获取最新成交时间逻辑
        return None

    # 现手
    @paramValidatorFactory(0)
    def getQLastVol(self, contNo):
        # TODO: 增加现手计算逻辑
        return 0

    # 当日最低价
    @paramValidatorFactory(0)
    def getQLow(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][6]

    # 当日跌停板价
    @paramValidatorFactory(0)
    def getQLowLimit(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][10]

    # 当日开盘价
    @paramValidatorFactory(0)
    def getQOpen(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][3]

    # 持仓量
    @paramValidatorFactory(0)
    def getQOpenInt(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][12]

    # 持仓量变化标志
    @paramValidatorFactory(0)
    def getQOpenIntFlag(self, contNo):
        # TODO: 增加持仓量变化比较逻辑
        return 1

    # 外盘量
    @paramValidatorFactory(0)
    def getQOutsideVol(self, contNo):
        # TODO: 增加外盘量计算逻辑
        return 0

    # 昨持仓量
    @paramValidatorFactory(0)
    def getQPreOpenInt(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][2]

    # 昨结算
    @paramValidatorFactory(0)
    def getQPreSettlePrice(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][1]

    # 当日涨跌
    @paramValidatorFactory(0)
    def getQPriceChg(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][112]

    # 当日涨跌幅
    @paramValidatorFactory(0)
    def getQPriceChgRadio(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][113]

    # 当日开仓量
    @paramValidatorFactory(0)
    def getQTodayEntryVol(self, contNo):
        # TODO: 增加当日开仓量的计算逻辑
        return 0

    # 当日平仓量
    @paramValidatorFactory(0)
    def getQTodayExitVol(self, contNo):
        # TODO: 增加当日平仓量的计算逻辑
        return 0

    # 当日成交量
    @paramValidatorFactory(0)
    def getQTotalVol(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][11]

    # 当日成交额
    @paramValidatorFactory(0)
    def getQTurnOver(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][27]

    # 当日涨停板价
    @paramValidatorFactory(0)
    def getQUpperLimit(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return quoteDataModel._metaData["Lv1Data"][9]

    # 行情数据是否有效
    @paramValidatorFactory(False)
    def getQuoteDataExist(self, contNo):
        quoteDataModel = self._contractData[contNo]
        return True if len(quoteDataModel._metaData["Lv1Data"]) else False


class StrategyTrade(TradeModel):
    '''交易数据模型'''
    def __init__(self, strategy, config):
        self.logger = strategy.logger
        self._strategy = strategy
        TradeModel.__init__(self, self.logger)
        self._config = config
        #self._selectedUserNo = self._config._metaData['Money']['UserNo']
        # print("===== StrategyTrade ====", self._config._metaData)
        
    def initialize(self):
        self._selectedUserNo = self._config.getUserNo()

    def reqTradeData(self):
        event = Event({
            'EventCode': EV_ST2EG_STRATEGYTRADEINFO,
            'StrategyId': self._strategy.getStrategyId(),
            'Data': '',
        })

        self._strategy.sendEvent2Engine(event)

    def getAccountId(self):
        '''
        :return:当前公式应用的交易帐户ID
        '''
        return self._selectedUserNo

    def getDataFromTMoneyModel(self, key):
        '''
        获取self._userInfo中当前账户指定的资金信息
        :param key:需要的资金信息的key
        :return:资金信息
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._money) == 0:
            return 0

        tMoneyModel = None
        if 'Base' in tUserInfoModel._money:
            tMoneyModel = tUserInfoModel._money['Base']

        if len(tUserInfoModel._money) > 0:
            tMoneyModelList = list(tUserInfoModel._money.values())
            tMoneyModel = tMoneyModelList[0]

        if not tMoneyModel or key not in tMoneyModel._metaData:
            return 0

        return tMoneyModel._metaData[key]
        
    def getSign(self, userNo):
        '''
        :return: 获取当前账户的服务器标识
        '''
        userInfo = self.getUserModel(userNo)
        if not userInfo:
            return None
        return userInfo.getSign()

    def getCost(self):
        '''
        :return: 当前公式应用的交易帐户的手续费
        '''
        return self.getDataFromTMoneyModel('Fee')

    def getCurrentEquity(self):
        '''
        :return:当前公式应用的交易帐户的动态权益
        '''
        return self.getDataFromTMoneyModel('Equity')

    def getFreeMargin(self):
        '''
        :return:当前公式应用的交易帐户的可用资金
        '''
        return self.getDataFromTMoneyModel('Available')

    def getProfitLoss(self):
        '''
        :return:当前公式应用的交易帐户的浮动盈亏
        '''
        return self.getDataFromTMoneyModel('FloatProfitTBT')

    def getTotalFreeze(self):
        '''
        :return:当前公式应用的交易帐户的冻结资金
        '''
        return self.getDataFromTMoneyModel('FrozenFee') + self.getDataFromTMoneyModel('FrozenDeposit')

    def getItemSumFromPositionModel(self, direct, contNo, key):
        '''
        获取某个账户下所有指定方向、指定合约的指标之和
        :param direct: 买卖方向，为空时表示所有方向
        :param contNo: 合约编号
        :param key: 指标名称
        :return:
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._position) == 0:
            return 0

        contractNo = self._config._metaData['Contract'][0] if not contNo else contNo
        itemSum = 0.0
        for orderNo, tPositionModel in tUserInfoModel._position.items():
            if tPositionModel._metaData['Cont'] == contractNo and key in tPositionModel._metaData:
                if not direct or tPositionModel._metaData['Direct'] == direct:
                    itemSum += tPositionModel._metaData[key]

        return itemSum

    def getBuyAvgPrice(self, contNo):
        '''
        :return:当前公式应用的帐户下当前商品的买入持仓均价
        '''
        totalPosPrice = self.getItemSumFromPositionModel('B', contNo, 'PositionPrice')
        totalPosQty = self.getItemSumFromPositionModel('B', contNo, 'PositionQty')
        return totalPosPrice/totalPosQty if totalPosQty > 0 else 0

    def getBuyPosition(self, contNo):
        '''
        :return:当前公式应用的帐户下当前商品的买入持仓
        '''
        return self.getItemSumFromPositionModel('B', contNo, 'PositionQty')

    def getBuyProfitLoss(self, contNo):
        '''
        :return:当前公式应用的帐户下当前商品的买入持仓盈亏
        '''
        return self.getItemSumFromPositionModel('B', contNo, 'FloatProfit')

    def getSellAvgPrice(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的卖出持仓均价
        '''
        totalPosPrice = self.getItemSumFromPositionModel('S', contNo, 'PositionPrice')
        totalPosQty = self.getItemSumFromPositionModel('S', contNo, 'PositionQty')
        return totalPosPrice / totalPosQty if totalPosQty > 0 else 0

    def getSellPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的卖出持仓
        '''
        return self.getItemSumFromPositionModel('S', contNo, 'PositionQty')

    def getSellProfitLoss(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的卖出持仓盈亏
        '''
        return self.getItemSumFromPositionModel('S', contNo, 'FloatProfit')

    def getTotalAvgPrice(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的持仓均价
        '''
        totalPosPrice = self.getItemSumFromPositionModel('', contNo, 'PositionPrice')
        totalPosQty = self.getItemSumFromPositionModel('', contNo, 'PositionQty')
        return totalPosPrice / totalPosQty if totalPosQty > 0 else 0

    def getTotalPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的总持仓
        '''
        return self.getItemSumFromPositionModel('', contNo, 'PositionQty')

    def getTotalProfitLoss(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的总持仓盈亏
        '''
        return self.getItemSumFromPositionModel('', contNo, 'FloatProfit')

    def getTodayBuyPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的当日买入持仓
        '''
        return self.getItemSumFromPositionModel('B', contNo, 'PositionQty') - self.getItemSumFromPositionModel('B', contNo, 'PrePositionQty')

    def getTodaySellPosition(self, contNo):
        '''
        :return: 当前公式应用的帐户下当前商品的当日卖出持仓
        '''
        return self.getItemSumFromPositionModel('S', contNo, 'PositionQty') - self.getItemSumFromPositionModel('S', contNo, 'PrePositionQty')

    def convertDateToTimeStamp(self, date):
        '''
        将日期转换为时间戳
        :param date: 日期
        :return:
        '''
        if not date:
            return 0

        struct_time = time.strptime(date, "%Y-%m-%d %H:%M:%S")
        timeStamp = time.mktime(struct_time)
        return timeStamp

    def getDataFromTOrderModel(self, orderNo, key):
        '''
        获取当前账号下的指定订单信息
        :param orderNo: 订单的委托编号，为空时，取最后提交的订单信息
        :param key: 指定信息对应的key，不可为空
        :return: 当前账号下的指定订单信息
        '''
        if not key:
            return 0

        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if len(tUserInfoModel._order) == 0:
            return 0

        if orderNo and orderNo not in tUserInfoModel._order:
            return 0

        tOrderModel = None
        if not orderNo:
            # 委托单号 为空
            lastOrderTime = self.convertDateToTimeStamp('1970-01-01 08:00:00')
            for orderModel in tUserInfoModel._order.values():
                insertTimeStamp = self.convertDateToTimeStamp(orderModel._metaData['InsertTime'])
                updateTimeStamp = self.convertDateToTimeStamp(orderModel._metaData['UpdateTime'])
                orderTime = insertTimeStamp if insertTimeStamp >= updateTimeStamp else updateTimeStamp
                if orderTime > lastOrderTime:
                    lastOrderTime = orderTime
                    tOrderModel = orderModel
        else:
            tOrderModel = tUserInfoModel._order[orderNo]

        if not tOrderModel or key not in tOrderModel._metaData:
            return 0

        return tOrderModel._metaData[key]

    def getOrderBuyOrSell(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的买卖类型。
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的买卖类型
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'Direct')

    def getOrderEntryOrExit(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的开平仓状态
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的开平仓状态
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'Offset')

    def getDataFromTMatchModel(self, orderNo, key):
        '''
        获取当前账号下的指定成交信息
        :param orderNo: 订单的委托编号，为空时，取最后提交的订单信息
        :param key: 指定信息对应的key，不可为空
        :return: 当前账号下的指定成交信息
        '''

        if not key:
            return 0

        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return 0

        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if len(tUserInfoModel._match) == 0:
            return 0

        if orderNo and orderNo not in tUserInfoModel._match:
            return 0

        tMatchModel = None
        if not orderNo:
            # 委托单号 为空
            lastMatchTime = self.convertDateToTimeStamp('1970-01-01 08:00:00')
            for matchModel in tUserInfoModel._match.values():
                matchTime = self.convertDateToTimeStamp(matchModel._metaData['MatchDateTime'])
                if matchTime > lastMatchTime:
                    lastMatchTime = matchTime
                    tMatchModel = matchModel
        else:
            tMatchModel = tUserInfoModel._order[orderNo]

        if not tMatchModel or key not in tMatchModel._metaData:
            return 0

        return tMatchModel._metaData[key]

    def getOrderFilledLot(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的成交数量
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的成交数量
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTMatchModel(orderNo, 'MatchQty')

    def getOrderFilledPrice(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的成交价格
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的成交价格
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTMatchModel(orderNo, 'MatchPrice')

    def getOrderLot(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托数量
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托数量
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'OrderQty')

    def getOrderPrice(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托价格
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托价格
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'OrderPrice')

    def getOrderStatus(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的状态
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的状态
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'OrderState')

    def getOrderTime(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托时间
        :param orderNo: 委托单号，为空时，使用当日最后提交的委托编号作为查询依据
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托时间
        '''
        orderNo = self._strategy.getOrderNo(eSession)
        return self.getDataFromTOrderModel(orderNo, 'InsertTime')

    def deleteOrder(self, eSession):
        '''
        针对当前公式应用的帐户、商品发送撤单指令。
        :param orderId: 所要撤委托单的定单号
        :return: 发送成功返回True, 发送失败返回False
        '''
        if not eSession:
            return False

        orderNo = self._strategy.getOrderNo(eSession)
        if not orderNo:
            return False

        orderId = None
        userNo = self._selectedUserNo
        userInfoModel = self._userInfo[userNo]
        for orderModel in userInfoModel._order.values():
            if orderModel._metaData['OrderNo'] == orderNo:
                orderId = orderModel._metaData['OrderId']

        if not orderId:
            return False

        aOrder = {
            "OrderId": orderId,
        }
        aOrderEvent = Event({
            "EventCode": EV_ST2EG_ACTUAL_CANCEL_ORDER,
            "StrategyId": self._strategy.getStrategyId(),
            "Data": aOrder
        })
        self._strategy.sendEvent2Engine(aOrderEvent)
        return True
