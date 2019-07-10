import numpy as np
from capi.com_types import *
import copy


class TriggerMgr(object):
    def __init__(self, subsInfo, strategy):
        self._strategy = strategy
        self._kLineSubsInfo = subsInfo
        self._isReady = {}
        self._data = {}
        for record in self._kLineSubsInfo:
            kLineKey = (record["ContractNo"], record["KLineType"], record["KLineSlice"])
            self._isReady.setdefault(record["ContractNo"], {})
            # k线订阅
            self._isReady.get(record["ContractNo"]).setdefault(kLineKey, False)

    def updateData(self, apiEvent):
        if apiEvent.getEventCode() == EV_EG2ST_HISQUOTE_NOTICE:
            key = (apiEvent.getContractNo(), apiEvent.getKLineType(), apiEvent.getKLineSlice())
        else:
            return

        print("key = ", key, apiEvent.getData())
        self._data[key] = copy.deepcopy(apiEvent)
        self.setDataReady(key)

    def setDataReady(self, key):
        #assert self._isReady.get(key[0]).get(key) is False, "Error"
        self._isReady.get(key[0]).update({key:True})

    # 轮询机制
    def isAllDataReady(self, contractNo):
        # if not self._strategy.isRealTimeStatus():
        #     return True

        result = np.array(list(self._isReady[contractNo].values()))
        return result.all()

    def restAllData(self, contractNo):
        self._isReady[contractNo] = {k:False for k, _ in self._isReady[contractNo].items()}
        self._data = {}

    def getSyncTriggerInfo(self, contractNo):
        result = {}
        for k, v in self._data.items():
            if k[0] == contractNo:
                result[k] = v
        return result