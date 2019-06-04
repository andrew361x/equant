import copy
from capi.com_types import *
from capi.event import *

class EngineOrderModel:
    def __init__(self, strategyOrder={}):

        self._localOrder = {}
        self._epoleStarOrder = {}
        # 从文件中恢复的对应关系
        self._orderNo2OtherMap = {}

        if strategyOrder:
            # self._localOrder = strategyOrder["LocalOrder"]
            # self._epoleStarOrder = strategyOrder["EpoleStarOrder"]
            self._orderNo2OtherMap = strategyOrder["EpoleStarOrder2LocalOrderMap"]

        strategyId = 0
        self._localOrder.update({strategyId:SingleStrategyLocalOrder(strategyId)})
        self._epoleStarOrder.update({strategyId:EpoleStarOrder(strategyId)})

    def getStrategyOrder(self, strategyId):
        resultEvent = []
        if strategyId not in self._epoleStarOrder:
            return resultEvent
        if strategyId == 0:
            for strategyId, v in self._epoleStarOrder.items():
                curStrategyEPSOrder = self._epoleStarOrder[strategyId]
                resultEvent.extend(curStrategyEPSOrder.getRecord())
        elif strategyId > 0:
            curStrategyEPSOrder = self._epoleStarOrder[strategyId]
            resultEvent.extend(curStrategyEPSOrder.getRecord())
            curStrategyEPSOrder0 = self._epoleStarOrder[0]
            resultEvent.extend(curStrategyEPSOrder0.getRecord())
        return resultEvent

    def updateLocalOrder(self, event):
        strategyId = event.getStrategyId()
        if strategyId not in self._localOrder:
            self._localOrder[strategyId] = SingleStrategyLocalOrder(strategyId)
        record = event.getData()
        record['StrategyId'] = strategyId; record['ESessionId'] = event.getESessionId()
        self._localOrder[strategyId].updateLocalOrder(record)

    # response and notice
    def updateEpoleStarOrder(self, apiEvent):
        eventCode = apiEvent.getEventCode()
        if eventCode == EEQU_SRVEVENT_TRADE_ORDERQRY:
            self._updateEpoleStarOrderResponse(apiEvent)
        elif eventCode == EEQU_SRVEVENT_TRADE_ORDER:
            self._updateEpoleStarOrderNotice(apiEvent)
        elif eventCode == EEQU_SRVEVENT_TRADE_MATCHQRY:
            pass
            # self._updateEpoleStarOrderResponse(apiEvent)
        elif eventCode == EEQU_SRVEVENT_TRADE_MATCH:
            pass
            # self._updateEpoleStarOrderNotice(apiEvent)
        else:
            raise NotImplementedError

    #
    def _updateEpoleStarOrderResponse(self, event):
        for record in event.getData():
            if record["OrderNo"] and record["OrderNo"] in self._orderNo2OtherMap:
                strategyIdAndOrderId = self._orderNo2OtherMap[record["OrderNo"]]
                record["StrategyId"] = strategyIdAndOrderId["StrategyId"]
                record["ESessionId"] = strategyIdAndOrderId["ESessionId"]
            else:
                record['StrategyId'] = 0
                record["ESessionId"] = 0

            ePoleStarOrderEvent = Event({
                "EventCode":EEQU_SRVEVENT_TRADE_ORDERQRY,
                "ContractNo":record["Cont"],
                "StrategyId":record["StrategyId"],
                "ESessionId":record["ESessionId"],
                "Data":[record]
            })
            if record["StrategyId"] not in self._epoleStarOrder:
                self._epoleStarOrder.update({record["StrategyId"]:EpoleStarOrder(record["StrategyId"])})
            self._epoleStarOrder[record["StrategyId"]].updateEpoleOrderResponse(ePoleStarOrderEvent)

    def _updateEpoleStarOrderNotice(self, apiEvent):
        assert len(apiEvent.getData()) == 1, "error"
        record = apiEvent.getData()[0]
        strategyId, eSessionId = apiEvent.getStrategyId(), apiEvent.getESessionId()
        record["StrategyId"] = strategyId; record["ESessionId"] = eSessionId
        if strategyId not in self._epoleStarOrder:
            self._epoleStarOrder.update({strategyId: EpoleStarOrder(strategyId)})

        ePoleStarOrderEvent = Event({
            "EventCode": EEQU_SRVEVENT_TRADE_ORDERQRY,
            "ContractNo": record["Cont"],
            "StrategyId": record["StrategyId"],
            "ESessionId": record["ESessionId"],
            "Data": [record]
        })
        self._epoleStarOrder[strategyId].updateEpoleStarOrderNotice(ePoleStarOrderEvent)
        # self._localOrder[strategyId].updateLocalOrder()
        if strategyId > 0 and record["OrderNo"]:
            self._orderNo2OtherMap[record["OrderNo"]] = {"StrategyId":strategyId, "ESessionId":eSessionId}

    def getLocalOrderData(self):
        data = {}
        for strategyId, obj in self._localOrder.items():
            data[strategyId] = obj.getLocalOrder()
        return data

    def getEpoleStarOrder(self):
        data = {}
        for strategyId, obj in self._epoleStarOrder.items():
            data[strategyId] = obj.getEpoleStarOrder()
        return data

    def getData(self):
        result = {
            "LocalOrder":{},                                        # self.getLocalOrderData(),
            "EpoleStarOrder":{},                                    # self.getEpoleStarOrder(),
            "EpoleStarOrder2LocalOrderMap":self._orderNo2OtherMap
        }
        return result


# 实盘本地订单
class SingleStrategyLocalOrder:
    def __init__(self, strategyId):
        self._strategyId = strategyId
        self._localOrder = {}
        self._localOrderFlow = []

    def updateLocalOrder(self, record):
        self._localOrder[record["ESessionId"]] = record
        self._localOrderFlow.append({record["ESessionId"]:record})

    def getLocalOrder(self):
        return self._localOrder

    def removeLocalOrder(self, event):
        pass


class EpoleStarOrder:
    def __init__(self, strategyId):
        self._strategyId = strategyId
        self._epoleStarOrder = {}
        self._epoleStarOrderFlow = []

        if self._strategyId == 0:
            self._eSessionId = 1

    # 更新response存储
    def updateEpoleOrderResponse(self, ePoleStarOrderEvent):
        self.resetESessionId(ePoleStarOrderEvent)
        self._epoleStarOrder[ePoleStarOrderEvent.getESessionId()] = ePoleStarOrderEvent
        self._epoleStarOrderFlow.append(ePoleStarOrderEvent)

    # 更新notice存储
    def updateEpoleStarOrderNotice(self, ePoleStarOrderEvent):
        self.updateEpoleOrderResponse(ePoleStarOrderEvent)

    def resetESessionId(self, ePoleStarOrderEvent):
        if self._strategyId == 0 and ePoleStarOrderEvent.getESessionId() == 0:
            eSessionId = str(self._strategyId)+'-'+str(self._eSessionId)
            ePoleStarOrderEvent.setESessionId(eSessionId)
            self._eSessionId += 1

    def getEpoleStarOrder(self):
        result = {}
        for eSessionId, apiEvent in self._epoleStarOrder.items():
            result[eSessionId] = apiEvent.getData()[0]
        return result

    def getRecord(self):
        return list(self._epoleStarOrder.values())

    def clear(self):
        self._epoleStarOrder = {}
        self._epoleStarOrderFlow = []



