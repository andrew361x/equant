import numpy as np
from capi.com_types import *
from .engine_model import *
from copy import deepcopy
import talib
import time, sys
import datetime
from dateutil.relativedelta import relativedelta
import copy
import math
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


from datetime import datetime, timedelta

class StrategyConfig_new(object):
    '''
    {
            'SubContract': ['DCE|F|M|1909', 'ZCE|F|TA|909', 'ZCE|F|SR|001'],
            'Sample': {
                'DCE|F|M|1909': [{
                    'KLineType': 'M',
                    'KLineSlice': 1,
                    'BeginTime': '',
                    'KLineCount': 2,
                    'AllK': False,
                    'UseSample': True,
                    'Trigger': True
                }, {
                    'KLineType': 'D',
                    'KLineSlice': 1,
                    'BeginTime': '',
                    'KLineCount': 2,
                    'AllK': False,
                    'UseSample': True,
                    'Trigger': True
                }],
                'ZCE|F|TA|909': [{
                    'KLineType': 'M',
                    'KLineSlice': 1,
                    'BeginTime': '',
                    'KLineCount': 2,
                    'AllK': False,
                    'UseSample': True,
                    'Trigger': True
                }],
                'ZCE|F|SR|001': [{
                    'KLineType': 'D',
                    'KLineSlice': 1,
                    'BeginTime': '',
                    'KLineCount': 2,
                    'AllK': False,
                    'UseSample': True,
                    'Trigger': True
                }]
            },
            'Trigger': {
                'Timer': ['20190625121212', '20190625111111'],
                'Cycle': 200,
                'KLine': True,
                'SnapShot': True,
                'Trade': True
            },
            'RunMode': {
                'SendOrder': '1',
                'SendOrder2Actual': True
            },
            'Money': {
                'UserNo': 'Q912526205',
                'InitFunds': 10000000.0,
                'TradeDirection': 0,
                'OrderQty': {
                    'Type': '1',
                    'Count': 1
                },
                'MinQty': 88,
                'Hedge': 'T',
                'Margin': {
                    'DCE|F|M|1909' : {
                    'Type': 'R',
                    'Value': 0.88
                    }
                    ...
                },
                'OpenFee': {
                    'DCE|F|M|1909' : {
                    'Type': 'F',
                    'Value': 1.0
                    }
                    ...
                },
                'CloseFee': {
                    'DCE|F|M|1909' : {
                    'Type': 'F',
                    'Value': 1.0
                    }
                    ...
                },
                'CloseTodayFee': {
                    'DCE|F|M|1909' : {
                    'Type': 'F',
                    'Value': 1.0
                    }
                    ...
                },
                'Slippage': 5.0,
            },
            'Limit': {
                'OpenTimes': -1,
                'ContinueOpenTimes': -1,
                'OpenAllowClose': 0,
                'CloseAllowOpen': 0
            },
            'WinPoint' : {
                'DCE|F|M|1909' : {
                    'StopPoint': winPoint,
                    'AddPoint': nAddTick,
                    'CoverPosOrderType': nPriceType,
                },
                ...
            },
            'StopPoint' : {
                'DCE|F|M|1909' : {
                    'StopPoint': winPoint,
                    'AddPoint': nAddTick,
                    'CoverPosOrderType': nPriceType,
                },
                ...
            },
            'Params': {},
            'Pending': False,
        }
    '''
    def __init__(self):
        self._metaData = {
            'SubContract' : [],     # 订阅的合约信息，列表中的第一个合约为基准合约
            'Sample'      : {
            },
            'Trigger': {    # 触发方式
                'Timer': [],        # 指定时刻
                'Cycle': 0,         # 每隔固定毫秒数触发
                'KLine': False,     # K线触发
                'SnapShot': False,  # 即时行情触发
                'Trade': False,     # 交易数据触发
            },
            'RunMode': {    # 基础设置
                'SendOrder': '',            # 发单方式
                'SendOrder2Actual': False   # 运行模式-是否实盘运行
            },
            'Money': {      # 资金设置
                'UserNo': '', # 账户
                'InitFunds': 0, # 初始资金
                'TradeDirection': 0, # 交易方向
                'OrderQty': { # 默认下单量
                    'Type': '',
                    'Count': 0
                },
                'MinQty': 0,    # 最小下单量
                'Hedge': '',    # 投保标志
                'Margin': {},   # 保证金
                'OpenFee': {},  # 开仓手续费
                'CloseFee': {}, # 平仓手续费
                'CloseTodayFee': {},    # 平今手续费
                'Slippage': 0,    # 滑点损耗
            },
            'Limit': {  # 发单设置
                'OpenTimes': -1,        # 每根K线开仓次数
                'ContinueOpenTimes': -1, # 最大连续开仓次数
                'OpenAllowClose': 0, # 开仓的K线不允许反向下单
                'CloseAllowOpen': 0 # 平仓的K线不允许开仓
            },
            'WinPoint' : {},    # 止盈信息
            'StopPoint' : {},   # 止损信息
            'Params': {}, # 用户设置参数
            'Pending': False,
        }

    # ----------------------- 合约/K线类型/K线周期 ----------------------
    def setBarInfoInSample(self, contNo, kLineType, kLineSlice, sampleConfig, trigger=True):
        '''设置订阅的合约、K线类型和周期'''
        if not contNo:
            raise Exception("请确保在设置界面或者SetBarInterval方法中设置的合约编号不为空！")
        if kLineType not in ('t', 'T', 'S', 'M', 'H', 'D', 'W', 'm', 'Y'):
            raise Exception("请确保设置的K线类型为 't':分时，'T':分笔，'S':秒线，'M':分钟，'H':小时，'D':日线，'W':周线，'m':月线，'Y':年线 中的一个！")

        # 设置订阅的合约列表
        if contNo not in self._metaData['SubContract']:
            self._metaData['SubContract'].append(contNo)

        # 设置合约的K线类型和周期
        sampleDict = self.getSampleDict(kLineType, kLineSlice, sampleConfig, trigger)
        self.updateSampleDict(contNo, sampleDict)

    def deleteBarInfoInSample(self, contNo, kLineType, kLineSlice, sampleConfig, trigger=True):
        oldSampleDict = self.getSampleDict(kLineType, kLineSlice, sampleConfig, trigger)

        sample = self._metaData['Sample']
        if contNo not in sample:
            raise Exception("修改的合约/K线类型/K线周期/回测起始点信息不存在！")

        sampleDictList = sample[contNo]
        sameDict = self.getSameDictInList(oldSampleDict, sampleDictList)
        if sameDict:
            del sameDict

        if len(sample[contNo]) > 0:
            return

        # 更新订阅的合约列表
        del sample[contNo]
        subContractList = self._metaData['SubContract']
        if contNo in subContractList:
            subContractList.remove(contNo)

    def getSampleDict(self, kLineType, kLineSlice, sampleConfig, trigger=True):
        # 回测起始点信息
        kLineCount = 0
        beginTime = ''
        allK = False
        useSample = True
        if isinstance(sampleConfig, int):
            # 固定根数K线
            if sampleConfig > 0:
                kLineCount = sampleConfig
            else:
                kLineCount = 1
        elif sampleConfig == 'N':
            # 不使用K线
            kLineCount = 1
            # useSample = False
        elif isinstance(sampleConfig, str) and self.isVaildDate(sampleConfig, "%Y%m%d"):
            # 日期
            beginTime = sampleConfig
        elif sampleConfig == 'A':
            allK = True
        return {
                    'KLineType': kLineType,
                    'KLineSlice': kLineSlice,
                    'BeginTime': beginTime,    # 运算起始点-起始日期
                    'KLineCount': kLineCount,    # 运算起始点-固定根数
                    'AllK': allK,      # 运算起始点-所有K线
                    'UseSample': useSample, # 运算起始点-不执行历史K线
                    'Trigger': trigger     # 是否订阅历史K线
                }

    def isVaildDate(self, date, format):
        try:
            time.strptime(date, format)
            return True
        except:
            return False

    def updateSampleDict(self, contNo, sampleDict):
        sample = self._metaData['Sample']
        if contNo not in sample:
            sample[contNo] = sampleDict
            return

        sampleList = sample[contNo]
        isExist = True if self.getSameDictInList(sampleDict, sampleList) else False
        if not isExist:
            sampleList.append(sampleDict)

    def getSameDictInList(self, sampleDict, sampleList):
        sameDict = None
        for sampleInfo in sampleList:
            isEqual = True
            for key in sampleDict.keys():
                if sampleInfo[key] != sampleDict[key]:
                    isEqual = False
                    break
            if isEqual:
                # 存在相同的字典
                sameDict = sampleInfo
                break

        return sameDict

    # ----------------------- 触发方式 ----------------------
    def setTrigger(self, type, value=None):
        '''设置触发方式'''
        if type not in (1, 2, 3, 4, 5):
            raise Exception("触发方式可选的值只能 1: 即时行情触发，2: 交易数据触发，3: 每隔固定时间触发，4: 指定时刻触发 5:K线触发 是中的一个！")
        if type == 3 and value%100 != 0:
            raise Exception("当触发方式是 3: 每隔固定时间触发 时，指定的时间间隔必须是100的整数倍！")
        if type == 4:
            if not isinstance(value, list):
                raise Exception("当触发方式是 4: 指定时刻触发 时，时刻列表必须保存在一个列表中！")
            for timeStr in value:
                if len(timeStr) != 6 or not self.isVaildDate(timeStr, "%H%M%S"):
                    raise Exception("当触发方式是 4: 指定时刻触发 时，指定的时刻格式必须是HHMMSS！")

        trigger = self._metaData['Trigger']

        # TODO: 清空界面设置的触发方式
        if type == 1:
            trigger['SnapShot'] = True
        elif type == 2:
            trigger['Trade'] = True
        elif type == 3:
            trigger['Cycle'] = value
        elif type == 4:
            trigger['Timer'] = value
        elif type == 5:
            trigger['KLine'] = True

    def hasTimerTrigger(self):
        return bool(self._metaData['Trigger']['Timer'])

    def getTimerTrigger(self):
        return self._metaData['Trigger']['Timer']

    def hasCycleTrigger(self):
        return bool(self._metaData['Trigger']['Cycle'])

    def getCycleTrigger(self):
        return self._metaData['Trigger']['Cycle']

    def hasKLineTrigger(self):
        return bool(self._metaData['Trigger']['KLine'])

    def hasSnapShotTrigger(self):
        # return bool(self._metaData['Trigger']['SnapShot'])
        return True

    def hasTradeTrigger(self):
        return bool(self._metaData['Trigger']['Trade'])

    # ----------------------- 运行模式 ----------------------
    def setActual(self):
        '''设置是否实盘运行'''
        self._metaData['RunMode']['SendOrder2Actual'] = True

    def isActualRun(self):
        '''获取是否实盘运行标志位'''
        return bool(self._metaData['RunMode']['SendOrder2Actual'])

    # ----------------------- 发单方式 ----------------------
    def setOrderWay(self, type):
        '''设置发单方式'''
        if type not in (1, 2, '1', '2'):
            raise Exception("发单方式只能选择 1: 实时发单, 2: K线稳定后发单 中的一个！")
        self._metaData['RunMode']['SendOrder'] = str(type)

    def getSendOrder(self):
        '''获取发单方式'''
        return self._metaData['RunMode']['SendOrder']

    # ----------------------- 交易账户 ----------------------
    def setUserNo(self, userNo):
        '''设置交易账户'''
        self._metaData['Money']['UserNo'] = userNo

    def getUserNo(self):
        '''获取交易使用的账户'''
        return self._metaData['Money']['UserNo']

    # ----------------------- 初始资金 ----------------------
    def setInitCapital(self, capital, userNo=''):
        '''设置初始资金'''
        if not userNo:
            self._metaData['Money']['InitFunds'] = capital
        if userNo not in self._metaData['Money']:
            self._metaData['Money'][userNo] = {'InitFunds': capital}
        else:
            self._metaData['Money'][userNo]['InitFunds'] = capital

    def getInitCapital(self, userNo=''):
        '''获取初始资金'''
        if userNo in self._metaData:
            return self._metaData['Money'][userNo]['InitFunds']
        return self._metaData['Money']['InitFunds']

    # ----------------------- 交易方向 ----------------------
    def setTradeDirection(self, tradeDirection):
        '''设置交易方向'''
        if tradeDirection not in (0, 1, 2):
            raise Exception("交易方向只能是 0: 双向交易，1: 仅多头，2: 仅空头 中的一个！")
        self._metaData['Money']['TradeDirection'] = tradeDirection

    def getTradeDirection(self):
        '''获取交易方向'''
        return self._metaData['Money']['TradeDirection']

    # ----------------------- 默认下单量 ----------------------
    def setOrderQty(self, type, count):
        '''设置默认下单量'''
        self._metaData['Money']['OrderQty']['Type'] = type
        self._metaData['Money']['OrderQty']['Count'] = count

    def getOrderQtyType(self):
        '''设置默认下单量类型'''
        return self._metaData['Money']['OrderQty']['Type']

    def getOrderQtyCount(self):
        '''设置默认下单量数量'''
        return self._metaData['Money']['OrderQty']['Count']

    # ----------------------- 最小下单量 ----------------------
    def setMinQty(self, minQty):
        '''设置最小下单量'''
        if minQty <= 0:
            raise Exception("最小下单量必须为正数！")

        self._metaData['Money']['MinQty'] = minQty

    def getMinQty(self):
        '''获取最小下单量'''
        return self._metaData['Money']['MinQty']

    # ----------------------- 投保标志 ----------------------
    def setHedge(self, hedge):
        '''设置投保标志'''
        if hedge not in ('T', 'B', 'S', 'M'):
            raise Exception("投保标志只能是 'T': 投机，'B': 套保，'S': 套利，'M': 做市 中的一个！")

        self._metaData['Money']['Hedge'] = hedge

    def getHedge(self):
        '''获取投保标志'''
        return self._metaData['Money']['Hedge']

    # ----------------------- 保证金 ----------------------
    def setMargin(self, type, value, contNo=''):
        '''设置保证金的类型及比例/额度'''
        if value < 0 or type not in (EEQU_FEE_TYPE_RATIO, EEQU_FEE_TYPE_FIXED):
            raise Exception("保证金类型只能是 'R': 按比例收取，'F': 按定额收取 中的一个，并且保证金比例/额度不能小于0！")

        if contNo not in self._metaData['Money']:
            self._metaData['Money']['Margin'][contNo] = {'Type':'', 'Value':''}
        self._metaData['Money']['Margin'][contNo]['Type'] = type
        self._metaData['Money']['Margin'][contNo]['Value'] = value
        return 0

    def getMarginType(self, contNo=''):
        '''获取保证金类型'''
        if contNo not in self._metaData['Money']['Margin']:
            raise Exception("请确保为合约%s设置了保证金类型！"%contNo)

        return self._metaData['Money']['Margin'][contNo]['Type']

    def getMarginValue(self, contNo=''):
        '''获取保证金比例值'''
        if contNo in self._metaData['Money']['Margin']:
            raise Exception("请确保为合约%s设置了保证金比例/额度！"%contNo)
        return self._metaData['Money']['Margin'][contNo]['Value']

    # ----------------------- 交易手续费 ----------------------
    def setTradeFee(self, type, feeType, feeValue, contNo=''):
        '''设置交易手续费'''
        typeMap = {
            'A': ('OpenFee', 'CloseFee', 'CloseTodayFee'),
            'O': ('OpenFee',),
            'C': ('CloseFee',),
            'T': ('CloseTodayFee',),
        }
        if type not in typeMap:
            raise Exception("手续费类型只能取 'A': 全部，'O': 开仓，'C': 平仓，'T': 平今 中的一个！")

        if feeType not in (EEQU_FEE_TYPE_RATIO, EEQU_FEE_TYPE_FIXED):
            raise Exception("手续费收取方式只能取 'R': 按比例收取，'F': 按定额收取 中的一个！")

        keyList = typeMap[type]
        for key in keyList:
            feeDict = self._metaData['Money'][key]
            feeDict[contNo] = {
                'Type': feeType,
                'Value': feeValue
            }

    def getRatioOrFixedFee(self, feeType, isRatio, contNo=''):
        '''获取 开仓/平仓/今平 手续费率或固定手续费'''
        typeDict = {'OpenFee':'开仓', 'CloseFee':'平仓', 'CloseTodayFee':'平今'}
        if feeType not in typeDict:
            return 0

        openFeeType = EEQU_FEE_TYPE_RATIO if isRatio else EEQU_FEE_TYPE_FIXED
        if contNo not in self._metaData['Money'][feeType]:
            raise Exception("请确保为合约%s设置了%s手续费！"%(contNo, typeDict[feeType]))

        return self._metaData['Money'][feeType][contNo]['Value'] if self._metaData['Money'][feeType][contNo]['Type'] == openFeeType else 0

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

    # ----------------------- 滑点损耗 ----------------------
    def setSlippage(self, slippage):
        '''设置滑点损耗'''
        self._metaData['Money']['Slippage'] = slippage

    def getSlippage(self):
        '''滑点损耗'''
        return self._metaData['Money']['Slippage']

    # ----------------------- 发单设置 ----------------------
    def setLimit(self, openTimes, continueOpenTimes, openAllowClose, closeAllowOpen):
        '''设置发单参数'''
        limitDict = self._metaData['Limit']
        limitDict['OpenTimes'] = openTimes          # 每根K线开仓次数
        limitDict['ContinueOpenTimes'] = continueOpenTimes  # 最大连续开仓次数
        limitDict['OpenAllowClose'] = openAllowClose    # 开仓的K线不允许反向下单
        limitDict['CloseAllowOpen'] = closeAllowOpen    # 平仓的K线不允许开仓

    def getLimit(self):
        '''获取发单设置'''
        return self._metaData['Limit']

    # ----------------------- 止盈信息 ----------------------
    def setWinPoint(self, winPoint, nPriceType, nAddTick, contractNo):
        '''设置止盈信息'''
        if nPriceType not in (0, 1, 2, 3, 4):
            raise Exception("设置止盈点平仓下单价格类型必须为 0: 最新价，1：对盘价，2：挂单价，3：市价，4：停板价 中的一个！")

        if nAddTick not in (0, 1, 2):
            raise Exception("止盈点的超价点数仅能为0，1，2中的一个！")

        self._metaData['WinPoint'][contractNo] = {
            "StopPoint": winPoint,
            "AddPoint": nAddTick,
            "CoverPosOrderType": nPriceType,
        }

    def getStopWinParams(self, contractNo=None):
        '''获取止盈信息'''
        contNo = self.getBenchmark() if not contractNo else contractNo

        if contNo not in self._metaData['WinPoint']:
            return None

        return self._metaData['WinPoint'][contNo]
    # ----------------------- 止损信息 ----------------------
    def setStopPoint(self, stopPoint, nPriceType, nAddTick, contractNo):
        '''设置止损信息'''
        if nPriceType not in (0, 1, 2, 3, 4):
            raise Exception("设置止损点平仓下单价格类型必须为 0: 最新价，1：对盘价，2：挂单价，3：市价，4：停板价 中的一个！")

        if nAddTick not in (0, 1, 2):
            raise Exception("止损点的超价点数仅能为0，1，2中的一个！")

        self._metaData['StopPoint'][contractNo] = {
            "StopPoint": stopPoint,
            "AddPoint": nAddTick,
            "CoverPosOrderType": nPriceType,
        }

    def getStopLoseParams(self, contractNo=None):
        '''获取止损信息'''
        contNo = self.getBenchmark() if not contractNo else contractNo

        if contNo not in self._metaData['StopPoint']:
            return None

        return self._metaData['StopPoint'][contNo]

    # ----------------------- 用户设置参数 ----------------------
    def setParams(self, params):
        '''设置用户设置参数'''
        self._metaData["Params"] = params

    def getParams(self):
        '''获取用户设置参数'''
        if "Params" not in self._metaData:
            return {}
        return self._metaData["Params"]

    # ----------------------- 允许实盘交易 ----------------------
    def setPending(self, pending):
        '''设置是否暂停向实盘下单标志'''
        self._metaData['Pending'] = pending

    def getPending(self):
        '''获取是否暂停向实盘下单标志'''
        return self._metaData['Pending']

    # -----------------------------------------------------------
    def getConfig(self):
        return self._metaData

    def getBenchmark(self):
        '''获取基准合约'''
        showInfo = self.getKLineShowInfo()
        return showInfo['ContractNo']

    def getTriggerContract(self):
        return self._metaData['SubContract']

    def getSampleInfo(self):
        kLineTypetupleList = []
        kLineTypeDictList = []
        subDict = {}
        for contNo, barList in self._metaData['Sample'].items():
            for barInfo in barList:
                triggerTuple = (contNo, barInfo['KLineType'], barInfo['KLineSlice'])
                if triggerTuple not in kLineTypetupleList:
                    kLineTypetupleList.append(triggerTuple)
                    kLineTypeDictList.append({"ContractNo": contNo, "KLineType": barInfo['KLineType'], "KLineSlice": barInfo['KLineSlice']})

                if barInfo['UseSample']:
                    # 需要订阅历史K线
                    sampleInfo = self._getKLineCount(barInfo)
                    subDict[triggerTuple] = {"ContractNo": contNo, "KLineType": barInfo['KLineType'],
                                             "KLineSlice": barInfo['KLineSlice'], "BarCount": sampleInfo}
                elif triggerTuple in subDict:
                    # 不需要
                    del subDict[triggerTuple]

        return kLineTypetupleList, kLineTypeDictList, subDict

    def _getKLineCount(self, sampleDict):
        if not sampleDict['UseSample']:
            return 1

        if sampleDict['KLineCount'] > 0:
            return sampleDict['KLineCount']

        if len(sampleDict['BeginTime']) > 0:
            return sampleDict['BeginTime']

        if sampleDict['AllK']:
            nowDateTime = datetime.now()
            if self.getKLineType() == EEQU_KLINE_DAY:
                threeYearsBeforeDateTime = nowDateTime - relativedelta(years=3)
                threeYearsBeforeStr = datetime.strftime(threeYearsBeforeDateTime, "%Y%m%d")
                return threeYearsBeforeStr
            elif self.getKLineType() == EEQU_KLINE_HOUR or self.getKLineType() == EEQU_KLINE_MINUTE:
                oneMonthBeforeDateTime = nowDateTime - relativedelta(months=1)
                oneMonthBeforeStr = datetime.strftime(oneMonthBeforeDateTime, "%Y%m%d")
                return oneMonthBeforeStr
            elif self.getKLineType() == EEQU_KLINE_SECOND:
                oneWeekBeforeDateTime = nowDateTime - relativedelta(days=7)
                oneWeekBeforeStr = datetime.strftime(oneWeekBeforeDateTime, "%Y%m%d")
                return oneWeekBeforeStr
            else:
                raise NotImplementedError

    def getKLineSubsInfo(self):
        kLineTypetupleList, kLineTypeDictList, subDict = self.getSampleInfo()
        return subDict.values()

    def getKLineKindsInfo(self):
        kLineTypetupleList, kLineTypeDictList, subDict = self.getSampleInfo()
        for value in subDict.values():
            del value['BarCount']

        return subDict.values()

    def getKLineTriggerInfo(self):
        kLineTypetupleList, kLineTypeDictList, subDict = self.getSampleInfo()
        return kLineTypeDictList

    def getKLineTriggerInfoSimple(self):
        kLineTypetupleList, kLineTypeDictList, subDict = self.getSampleInfo()
        return kLineTypetupleList

    def getKLineShowInfo(self):
        # 1、取界面设置的第一个合约 2、取SetBarinterval第一个设置的合约
        subContract = self._metaData['SubContract']
        if not subContract or len(subContract) == 0:
            raise Exception("请确保在设置界面或者在策略中调用SetBarInterval方法设置展示的合约、K线类型和周期")

        displayCont = subContract[0]
        kLineInfo = self._metaData['Sample'][displayCont]

        return {
            'ContractNo': displayCont,
            'KLineType': kLineInfo['KLineType'],
            'KLineSlice': kLineInfo['KLineSlice']
        }

    def getKLineShowInfoSimple(self):
        showInfoSimple = []
        showInfo = self.getKLineShowInfo()
        for value in showInfo.values():
            showInfoSimple.append(value)
        return tuple(showInfoSimple)

    priorityDict = {
        EEQU_KLINE_YEAR: 90000,
        EEQU_KLINE_MONTH: 80000,
        EEQU_KLINE_WEEK: 70000,
        EEQU_KLINE_DayX: 60000,
        EEQU_KLINE_DAY: 50000,
        EEQU_KLINE_HOUR: 40000,
        EEQU_KLINE_MINUTE: 30000,
        EEQU_KLINE_SECOND: 20000,
        EEQU_KLINE_TICK: 10000,
        EEQU_KLINE_TIMEDIVISION: 0,
    }

    def getPriority(self, key):
        kLineTypetupleList = self.getKLineTriggerInfoSimple()
        return kLineTypetupleList.index(key) + self.priorityDict[key[1]] + int(key[2])

    def getContract(self):
        '''获取合约列表'''
        return self._metaData['SubContract']

    def getKLineType(self):
        '''获取K线类型'''
        kLineInfo = self.getKLineShowInfo()
        if 'KLineType' in kLineInfo:
            return kLineInfo['KLineType']

    def getKLineSlice(self):
        '''获取K线间隔'''
        kLineInfo = self.getKLineShowInfo()
        if 'KLineSlice' in kLineInfo:
            return kLineInfo['KLineSlice']

    def getDefaultKey(self):
        '''获取基准合约配置'''
        showInfo = self.getKLineShowInfo()
        return (showInfo['ContractNo'], showInfo['KLineType'], showInfo['KLineSlice'])