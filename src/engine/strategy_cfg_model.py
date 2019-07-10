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

class StrategyConfig(object):
    '''
    功能：策略配置模块
    参数：
        {
	'Contract': ('ZCE|F|AP|911', ),
	'Trigger': {
		'Timer': None,
		'Cycle': None,
		'KLine': True,
		'SnapShot': True,
		'Trade': False
	},
	'Sample': {
		'KLineCount': 2000
	},
	'DefaultSample': {
		'ZCE|F|AP|911': [{
			'KLineType': 'M',
			'KLineSlice': 1
		}, {
			'KLineType': 'D',
			'KLineSlice': 1
		}],
		'ZCE|F|CY|910': [{
			'KLineType': 'M',
			'KLineSlice': 1
		}],
		'ZCE|F|CJ|912': [{
			'KLineType': 'D',
			'KLineSlice': 1
		}]
	},
	'RunMode': {
		'SendOrder': '1',
		'Simulate': {
			'Continues': True,
			'UseSample': True
		},
		'Actual': {
			'SendOrder2Actual': False
		}
	},
	'Money': {
		'UserNo': 'ET001',
		'InitFunds': 10000000.0,
		'MinQty': 1,
		'OrderQty': {
			'Type': '1',
			'Count': 1
		},
		'Hedge': 'T',
		'Margin': {
			'Type': 'R',
			'Value': 0.01
		},
		'OpenFee': {
			'Type': 'F',
			'Value': 1.0
		},
		'CloseFee': {
			'Type': 'F',
			'Value': 1.0
		},
		'CloseTodayFee': {
			'Type': 0,
			'Value': 0
		}
	},
	'Limit': {
		'OpenTimes': -1,
		'ContinueOpenTimes': -1,
		'OpenAllowClose': 0,
		'CloseAllowOpen': 0
	},
	'Other': {
		'Slippage': 1.0,
		'TradeDirection': 0
	},
	'Params': {}
    }
    '''
    def __init__(self, argsDict):
        ret = self._chkConfig(argsDict)
        if ret > 0:
            raise Exception(ret)

        if 'Display' in argsDict['Sample']:
            self._metaData = argsDict
        else:
            self._metaData = self.convertArgsDict(argsDict)

    def convertArgsDict(self, argsDict):
        # print("sun --------", argsDict)
        resDict = {}
        contList = argsDict['Contract']
        for key, value in argsDict.items():
            if key in ('Sample', 'DefaultSample'):
                continue
            resDict[key] = deepcopy(value)

        # 策略暂停向实盘下单
        resDict['Pending'] = False

        # Sample
        sample = argsDict['Sample']
        useSample = ('BeginTime' in sample) or ('KLineCount' in sample) or ('AllK' in sample)
        sampleInfo = {
            'BeginTime' : sample['BeginTime'] if 'BeginTime' in sample else '',
            'KLineCount': sample['KLineCount'] if 'KLineCount' in sample else 0,
            'AllK'      : sample['AllK'] if 'AllK' in sample else False,
            'UseSample' : useSample,
            'Trigger': True,
        }# 界面设置信息

        # DefaultSample
        subContract = []
        defaultSample = argsDict['DefaultSample']
        if len(defaultSample) == 0:
            # 界面未设置
            pass
        else:
            for contNo, kLineInfoList in defaultSample.items():
                subContract.append(contNo)
                for kLineInfo in kLineInfoList:
                    kLineInfo.update(sampleInfo)


        resDict['DefaultSample'] = defaultSample
        resDict['Sample'] = defaultSample

        # 合约列表
        resDict['SubContract'] = subContract

        if len(contList) > 0 and len(contList[0]) > 0:
        # 界面设置了基准合约和K线信息
            benchmark = contList[0]
            kLineInfo = defaultSample[benchmark][0]
            resDict['Sample']['Display'] = {"ContractNo": benchmark, "KLineType": kLineInfo['KLineType'], "KLineSlice": kLineInfo['KLineSlice']}

        # 触发方式，给setTriggerType清空界面设置用
        resDict['Trigger']['SetByUI'] = True

        # 订阅即使行情合约列表
        resDict['SubQuoteContract'] = []

        # 退订即使行情合约列表
        resDict['UnsubQuoteContract'] = []

        return resDict

    def updateBarInterval(self, contNo, inDict, fromDict):
        if contNo in inDict['Sample']:
            if not fromDict:
                return -1

            isExist = False
            for barDict in inDict['Sample'][contNo]:
                if barDict['KLineType'] == fromDict['KLineType'] \
                        and barDict['KLineSlice'] == fromDict['KLineSlice']\
                        and barDict['BeginTime'] == fromDict['BeginTime']\
                        and barDict['KLineCount'] == fromDict['KLineCount']\
                        and barDict['AllK'] == fromDict['AllK']\
                        and barDict['UseSample'] == fromDict['UseSample']\
                        and barDict['Trigger'] == fromDict['Trigger']:
                    isExist = True
                    break

            if not isExist:
                inDict['Sample'][contNo].append(fromDict)
        else:
            inDict['Sample'][contNo] = [fromDict]

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

        if 'DefaultSample' not in argsDict:
            return 7
            
        return 0

    def getConfig(self):
        return self._metaData

    def getBenchmark(self):
        '''获取基准合约'''
        showInfo = self.getKLineShowInfo()
        return showInfo['ContractNo']
        
    def getDefaultKey(self):
        '''获取基准合约配置'''
        showInfo = self.getKLineShowInfo()
        return (showInfo['ContractNo'], showInfo['KLineType'], showInfo['KLineSlice'])

    # *******************************************************
    # gyt test interface
    def getTriggerContract(self):
        return self.getContract()

    def getSampleInfo(self):
        kLineTypetupleList = []
        kLineTypeDictList = []
        subDict = {}
        for contNo, barList in self._metaData['Sample'].items():
            if contNo in ('Default', 'Display'):
                continue

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

    def getKLineSubsInfo(self):
        kLineTypetupleList, kLineTypeDictList, subDict = self.getSampleInfo()
        print(subDict.values())
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
        # 1、取界面设置的 2、取SetBarinterval第一个设置的
        if 'Display' not in self._metaData['Sample'] or not self._metaData['Sample']['Display']['ContractNo']:
            raise Exception("请确保在设置界面或者在策略中调用SetBarInterval方法设置展示的合约、K线类型和周期")
        return self._metaData['Sample']['Display']

    def getKLineShowInfoSimple(self):
        showInfoSimple = []
        showInfo = self.getKLineShowInfo()
        for value in showInfo.values():
            showInfoSimple.append(value)
        return tuple(showInfoSimple)

    priorityDict = {
        EEQU_KLINE_YEAR     : 90000,
        EEQU_KLINE_MONTH    : 80000,
        EEQU_KLINE_WEEK     : 70000,
        EEQU_KLINE_DayX     : 60000,
        EEQU_KLINE_DAY      : 50000,
        EEQU_KLINE_HOUR     : 40000,
        EEQU_KLINE_MINUTE   : 30000,
        EEQU_KLINE_SECOND   : 20000,
        EEQU_KLINE_TICK     : 10000,
        EEQU_KLINE_TIMEDIVISION: 0,
    }

    def getPriority(self, key):
        kLineTypetupleList = self.getKLineTriggerInfoSimple()
        return kLineTypetupleList.index(key)+self.priorityDict[key[1]]+int(key[2])

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
    # *******************************************************
    def getContract(self):
        '''获取合约列表'''
        contNoList = set(self._metaData['SubContract'])
        if len(self._metaData['SubQuoteContract']) > 0:
            contNoList = contNoList | set(self._metaData['SubQuoteContract'])
        if len(self._metaData['UnsubQuoteContract']) > 0:
            contNoList = contNoList - set(self._metaData['UnsubQuoteContract'])
        return list(contNoList)

    def setPending(self, pending):
        '''设置是否暂停向实盘下单标志'''
        self._metaData['Pending'] = pending

    def getPending(self):
        '''获取是否暂停向实盘下单标志'''
        return self._metaData['Pending'] if 'Pending' in self._metaData else False

    def addUserNo(self, userNo):
        '''设置交易使用的账户'''
        if isinstance(self._metaData['Money']['UserNo'], str):
            userNoStr = self._metaData['Money']['UserNo']
            if userNo == userNoStr:
                self._metaData['Money']['UserNo'] = [userNo]
            else:
                self._metaData['Money']['UserNo'] = [userNoStr, userNo]

        if isinstance(self._metaData['Money']['UserNo'], list):
            if userNo in self._metaData['Money']['UserNo']:
                return 0
            else:
                self._metaData['Money']['UserNo'].append(userNo)
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
        if type == 3 and value%100 != 0:
            return -1
        if type == 4 and isinstance(value, list):
            for timeStr in value:
                if len(timeStr) != 14 or not self.isVaildDate(timeStr, "%Y%m%d%H%M%S"):
                    return -1

        trigger = self._metaData['Trigger']
        # 清空界面设置的触发方式信息
        if 'SetByUI' in trigger and trigger['SetByUI']:
            trigger['SnapShot'] = False
            trigger['Trade'] = False
            trigger['Cycle'] = None
            trigger['Timer'] = []
            trigger['KLine'] = False
            trigger['SetByUI'] = False

        if type == 1:
            trigger['SnapShot'] = True
        elif type == 2:
            trigger['Trade'] = True
        elif type == 3:
            trigger['Cycle'] = value
        elif type == 4:
            trigger['Timer'] = value
        elif type ==5:
            trigger['KLine'] = True

        return 0

    def setWinPoint(self, winPoint, nPriceType, nAddTick, contractNo):
        if 'WinPoint' not in self._metaData:
            self._metaData['WinPoint'] = {}

        if nPriceType not in (0, 1, 2, 3, 4):
            raise Exception("参数nPriceType代表的平仓下单价格类型必须为0: 最新价，1：对盘价，2：挂单价，3：市价，4：停板价中的一个")

        if nAddTick not in (0, 1, 2):
            raise Exception("参数nAddTick代表的超价点数仅能为0，1，2")

        self._metaData['WinPoint'][contractNo] = {
            "StopPoint": winPoint,
            "AddPoint": nAddTick,
            "CoverPosOrderType": nPriceType,
        }
        return 0

    def getStopWinParams(self, contractNo=None):
        contNo = self.getBenchmark() if not contractNo else contractNo

        if 'WinPoint' not in self._metaData or contNo not in self._metaData['WinPoint']:
            return None

        return self._metaData['WinPoint'][contNo]

    def setStopPoint(self, stopPoint, nPriceType, nAddTick, contractNo):
        if 'StopPoint' not in self._metaData:
            self._metaData['StopPoint'] = {}

        if nPriceType not in (0, 1, 2, 3, 4):
            raise Exception("参数nPriceType代表的平仓下单价格类型必须为0: 最新价，1：对盘价，2：挂单价，3：市价，4：停板价中的一个")

        if nAddTick not in (0, 1, 2):
            raise Exception("参数nAddTick代表的超价点数仅能为0，1，2")

        self._metaData['StopPoint'][contractNo] = {
            "StopPoint": stopPoint,
            "AddPoint": nAddTick,
            "CoverPosOrderType": nPriceType,
        }
        return 0

    def getStopLoseParams(self, contractNo=None):
        contNo = self.getBenchmark() if not contractNo else contractNo

        if 'StopPoint' not in self._metaData or contNo not in self._metaData['StopPoint']:
            return None

        return self._metaData['StopPoint'][contNo]

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

    def setBarInterval(self, contNo, barType, barInterval, sampleConfig, trigger=True):
        '''设置K线类型和K线周期'''
        # if barType not in ('t', 'T', 'S', 'M', 'H', 'D', 'W', 'm', 'Y'):
        if barType not in ('T', 'S', 'M', 'D'):
            raise Exception("请确保设置的K线类型为 'T':分笔，'S':秒线，'M':分钟，'D':日线 中的一个！")
        if barType == 'S':
            barType = 'T'

        # 清空界面设置的合约K线信息
        contract = self._metaData['Contract']
        defaultBenchmark = contract[0] if len(contract) > 0 and len(contract[0]) else ""
        if len(defaultBenchmark) > 0:
            self._metaData['Contract'] = ()
            self._metaData['Sample'] = {}
            self._metaData['SubContract'] = []
            self._metaData['Sample']['Display'] = {}

        # 添加订阅合约
        if contNo not in self._metaData['SubContract']:
            self._metaData['SubContract'].append(contNo)

        # 记录展示的合约和K线信息
        if 'Display' not in self._metaData['Sample'] or not self._metaData['Sample']['Display']:
            self._metaData['Sample']['Display'] = {"ContractNo" : contNo, "KLineType": barType, "KLineSlice": barInterval}

        # 更新回测起始点信息
        kLineCount = 0
        beginTime = ''
        allK = False
        useSample = True
        if isinstance(sampleConfig, int):
            # kLineCount
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
        sampleInfo = {
            'KLineType': barType,
            'KLineSlice': barInterval,
            'BeginTime' : beginTime,
            'KLineCount' : kLineCount,
            'AllK' : allK,
            'UseSample' : useSample,
            'Trigger' : trigger,
        }

        self.updateBarInterval(contNo, self._metaData, sampleInfo)

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

    def setActual(self):
        self._metaData['RunMode']['Actual']['SendOrder2Actual'] = True

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

    def getTimerTrigger(self):
        return self._metaData['Trigger']['Timer']

    def hasCycleTrigger(self):
        return bool(self._metaData['Trigger']['Cycle'])

    def getCycleTrigger(self):
        return self._metaData['Trigger']['Cycle']

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

    def setParams(self, params):
        self._metaData["Params"] = params

    def getParams(self):
        if "Params" not in self._metaData:
            return {}
        return self._metaData["Params"]

    def updateSubQuoteContract(self, contNoList):
        if not isinstance(contNoList, list) or not contNoList:
            return

        self._metaData['SubQuoteContract'].extend(contNoList)

    def updateUnsubQuoteContract(self, contNoList):
        if not isinstance(contNoList, list) or not contNoList:
            return

        self._metaData['UnsubQuoteContract'].extend(contNoList)


