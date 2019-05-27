import numpy as np
from capi.com_types import *
from .engine_model import *
import time, sys
from .trade_model import TradeModel

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

        contractNo = self._config.getBenchmark() if not contNo else contNo
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
            for orderNo in list(tUserInfoModel._order.keys()):
                orderModel = tUserInfoModel._order[orderNo]
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
