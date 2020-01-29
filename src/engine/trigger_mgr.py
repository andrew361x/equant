import numpy as np
from capi.com_types import *
import copy

import pickle
from functools import wraps


# by gyt 便于调试
def debug(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        funcResult = func(*args, **kwargs)
        argsStr = "(" + ", ".join([str(positionArg) for positionArg in args])
        kwargsStr = ", " + repr(kwargs) + ")" if kwargs else ")"
        print(f"{func.__name__}{argsStr}{kwargsStr} -> {funcResult}")
        return funcResult

    return wrapper


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
            self._isReady.get(record["ContractNo"]).setdefault(kLineKey, False) # {'INDEX': {('INDEX', 1, 'D'): False}}
            #self._triggerMgr._isReady
            #{'SHFE|F|RB|2001': {('SHFE|F|RB|2001', 'D', 1): False},
             #'SHFE|F|RB|2005': {('SHFE|F|RB|2005', 'D', 1): False},
             #'SHFE|F|RB|2009': {('SHFE|F|RB|2009', 'D', 1): False},
             #'SHFE|Z|RB|INDEX': {('SHFE|Z|RB|INDEX', 'D', 1): False}}
    def updateData(self, key, kLine):
        # print("key = ", key, apiEvent.getData())
        self._data[key] = copy.deepcopy(kLine)
        self.setDataReady(key)

    def setDataReady(self, key):
        # assert self._isReady.get(key[0]).get(key) is False, "Error"
        self._isReady.get(key[0]).update({key:True})

    # 轮询机制
    def isAllDataReady(self, contractNo):
        # if not self._strategy.isRealTimeStatus():
        #     return True
        return all(self._isReady[contractNo])

    def resetAllData(self, contractNo):
        self._isReady[contractNo] = {k:False for k, _ in self._isReady[contractNo].items()}
        self._data = {}

    def getSyncTriggerInfo(self, contractNo):
        result = {}
        for k, v in self._data.items():
            if k[0] == contractNo:
                result[k] = v
        return result



