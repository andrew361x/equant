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

    def getAllPositionSymbol(self):
        '''
        :return:所有持仓合约
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            return []

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._position) == 0:
            return []

        contList = []
        for positionNo in list(tUserInfoModel._position.keys()):
            position = tUserInfoModel._position[positionNo]
            contNo = position._metaData['Cont']
            if contNo not in contList:
                contList.append(contNo)
        return contList

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

    def getAMargin(self):
        return self.getDataFromTMoneyModel('Deposit')

    def getProfitLoss(self):
        '''
        :return:当前公式应用的交易帐户的浮动盈亏
        '''
        return self.getDataFromTMoneyModel('FloatProfitTBT')

    def getCoverProfit(self):
        return self.getDataFromTMoneyModel('CoverProfitTBT')

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

    def getOrderBuyOrSell(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的买卖类型。
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的买卖类型
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")

        tUserInfoModel = self._userInfo[self._selectedUserNo]

        tMatchModel = None
        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 'N'
            tMatchModel = tUserInfoModel._order[orderNo]
            return tMatchModel._metaData['Direct']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    return tMatchModel._metaData['Direct']
        return 'N'


    def getOrderEntryOrExit(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的开平仓状态
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的开平仓状态
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")
        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 'N'
            tMatchModel = tUserInfoModel._order[orderNo]
            return tMatchModel._metaData['Offset']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    return tMatchModel._metaData['Offset']
        return 'N'

    def getOrderFilledLot(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的成交数量
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的成交数量
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")
        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 0

            tMatchModel = tUserInfoModel._order[orderNo]
            return tMatchModel._metaData['MatchQty']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    return tMatchModel._metaData['MatchQty']
        return 0

    def getOrderFilledPrice(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的成交价格
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的成交价格
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")
        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 0

            tMatchModel = tUserInfoModel._order[orderNo]
            return tMatchModel._metaData['MatchPrice']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    return tMatchModel._metaData['MatchPrice']
        return 0


    def getOrderLot(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托数量
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托数量
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")
        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 0

            tOrderModel = tUserInfoModel._order[orderNo]
            return tOrderModel._metaData['OrderQty']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    return tMatchModel._metaData['OrderQty']
        return 0

    def getOrderPrice(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托价格
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托价格
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")
        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 0

            tOrderModel = tUserInfoModel._order[orderNo]
            return tOrderModel._metaData['OrderPrice']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    return tMatchModel._metaData['OrderPrice']
        return 0

    def getOrderStatus(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的状态
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的状态
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")
        tUserInfoModel = self._userInfo[self._selectedUserNo]

        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 'N'
            tOrderModel = tUserInfoModel._order[orderNo]
            return tOrderModel._metaData['OrderState']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    return tMatchModel._metaData['OrderState']
        return 'N'

    def getOrderTime(self, eSession):
        '''
        返回当前公式应用的帐户下当前商品的某个委托单的委托时间
        :param orderNo: 委托单号
        :return: 当前公式应用的帐户下当前商品的某个委托单的委托时间
        '''
        if len(self._userInfo) == 0 or self._selectedUserNo not in self._userInfo:
            raise Exception("请确保您的账号已经在客户端登录")
        tUserInfoModel = self._userInfo[self._selectedUserNo]

        insertTime = ''
        if isinstance(eSession, str) and '-' in eSession:
            orderNo = self._strategy.getOrderNo(eSession)
            if not orderNo or orderNo not in tUserInfoModel._order:
                return 0
            tOrderModel = tUserInfoModel._order[orderNo]

            if 'InsertTime' not in tOrderModel._metaData:
                return 0

            insertTime = tOrderModel._metaData['InsertTime']
        else:
            for orderNo in list(tUserInfoModel._order.keys()):
                tMatchModel = tUserInfoModel._order[orderNo]
                if tMatchModel._metaData['OrderId'] == eSession:
                    insertTime = tMatchModel._metaData['InsertTime']
                    break
        if not insertTime:
            return 0
        struct_time = time.strptime(insertTime, "%Y-%m-%d %H:%M:%S")
        timeStamp = time.strftime("%Y%m%d.%H%M%S", struct_time)
        return float(timeStamp)

    def getFirstOrderNo(self, contNo1, contNo2):
        if self._selectedUserNo not in self._userInfo:
            raise Exception("请先在极星客户端登录您的交易账号")

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._order) == 0:
            return -1

        orderId = -1
        for orderNo in list(tUserInfoModel._order.keys()):
            orderModel = tUserInfoModel._order[orderNo]
            if not contNo1 or contNo1 == orderModel._metaData['Cont']:
                if orderId == -1 or orderId > orderModel._metaData['OrderId']:
                    orderId = orderModel._metaData['OrderId']

        return orderId

    def getNextOrderNo(self, orderId, contNo1, contNo2):
        if self._selectedUserNo not in self._userInfo:
            raise Exception("请先在极星客户端登录您的交易账号")

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._order) == 0:
            return -1

        minOrderId = -1
        for orderNo in list(tUserInfoModel._order.keys()):
            orderModel = tUserInfoModel._order[orderNo]
            if not contNo1 or contNo1 == orderModel._metaData['Cont']:
                if orderModel._metaData['OrderId'] <= orderId:
                    continue
                # 获取大于orderId的值
                if minOrderId == -1:
                    minOrderId = orderModel._metaData['OrderId']
                # 找到大于orderId并最接近orderId的值
                if orderModel._metaData['OrderId'] < minOrderId:
                    minOrderId = orderModel._metaData['OrderId']

        return minOrderId

    def getFirstQueueOrderNo(self, contNo1, contNo2):
        if self._selectedUserNo not in self._userInfo:
            raise Exception("请先在极星客户端登录您的交易账号")

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._order) == 0:
            return -1

        orderId = -1
        for orderNo in list(tUserInfoModel._order.keys()):
            orderModel = tUserInfoModel._order[orderNo]
            if not contNo1 or contNo1 == orderModel._metaData['Cont']:
                # 排队中
                if orderModel._metaData['OrderState'] != osQueued:
                    continue
                if orderId == -1 or orderId > orderModel._metaData['OrderId']:
                    orderId = orderModel._metaData['OrderId']

        return orderId

    def getNextQueueOrderNo(self, orderId, contNo1, contNo2):
        if self._selectedUserNo not in self._userInfo:
            raise Exception("请先在极星客户端登录您的交易账号")

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._order) == 0:
            return -1

        minOrderId = -1
        for orderNo in list(tUserInfoModel._order.keys()):
            orderModel = tUserInfoModel._order[orderNo]
            if not contNo1 or contNo1 == orderModel._metaData['Cont']:
                # 排队中
                if orderModel._metaData['OrderState'] != osQueued:
                    continue
                if orderModel._metaData['OrderId'] <= orderId:
                    continue
                # 获取大于orderId的值
                if minOrderId == -1:
                    minOrderId = orderModel._metaData['OrderId']
                # 找到大于orderId并最接近orderId的值
                if orderModel._metaData['OrderId'] < minOrderId:
                    minOrderId = orderModel._metaData['OrderId']

        return minOrderId

    def getOrderContractNo(self, orderId):
        if self._selectedUserNo not in self._userInfo:
            raise Exception("请先在极星客户端登录您的交易账号")

        tUserInfoModel = self._userInfo[self._selectedUserNo]
        if len(tUserInfoModel._order) == 0:
            return ""

        for orderNo in list(tUserInfoModel._order.keys()):
            orderModel = tUserInfoModel._order[orderNo]
            if orderModel._metaData['OrderId'] == orderId:
                return orderModel._metaData['Cont']
        return ""

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

        return self.deleteOrderByOrderId(orderId)

    def deleteOrderByOrderId(self, orderId):
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
