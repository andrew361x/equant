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

        if 'Default' in argsDict['Sample']:
            self._metaData = argsDict
        else:
            self._metaData = self.convertArgsDict(argsDict)

    def convertArgsDict(self, argsDict):
        resDict = {}
        contList = argsDict['Contract']
        for key, value in argsDict.items():
            if key in ('Sample'):
                continue
            resDict[key] = deepcopy(value)

        # 策略暂停向实盘下单
        resDict['Pending'] = False

        # Sample
        sample = argsDict['Sample']
        useSample = ('BeginTime' in sample) or ('KLineCount' in sample) or ('AllK' in sample)
        defaultSample = {
            'KLineType' : sample['KLineType'],
            'KLineSlice': sample['KLineSlice'],
            'BeginTime' : sample['BeginTime'] if 'BeginTime' in sample else '',
            'KLineCount': sample['KLineCount'] if 'KLineCount' in sample else 0,
            'AllK'      : sample['AllK'] if 'AllK' in sample else False,
            'UseSample' : useSample,
            'Trigger': True,
        }# 界面设置信息
        resDict['Sample'] = {
            'Default': [deepcopy(defaultSample)],
        }

        benchmark = ''
        if len(contList) > 0 and len(contList[0]) > 0:
            # 界面设置了基准合约和K线信息
            benchmark = contList[0]
            resDict['Sample'][benchmark] = [deepcopy(defaultSample)]
            resDict['SubContract'] = [benchmark]
        else:
            resDict['SubContract'] = []

        resDict['Sample']['Display'] = {"ContractNo" : benchmark, "KLineType": sample['KLineType'], "KLineSlice": sample['KLineSlice']}

        # print("sun ------- ", resDict)
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
        return self._metaData['SubContract']

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
        if not self._metaData['Sample']['Display']['ContractNo']:
            raise Exception("请确保在设置界面或者在策略中调用SetBarInterval方法设置展示的合约、K线类型和周期")
        return self._metaData['Sample']['Display']

    def getKLineShowInfoSimple(self):
        showInfoSimple = []
        showInfo = self.getKLineShowInfo()
        for value in showInfo.values():
            showInfoSimple.append(value)
        return tuple(showInfoSimple)

    def getPriority(self, key):
        kLineTypetupleList = self.getKLineTriggerInfoSimple()
        if key in kLineTypetupleList:
            return 1 + kLineTypetupleList.index(key)
        else:
            raise IndexError

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
        return self._metaData['SubContract']

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

    def setTrigger(self, contNo, type, value):
        '''设置触发方式'''
        if type not in (1, 2, 3, 4):
            return -1
        if type == 3 and value%100 != 0:
            return -1
        if type == 4 and isinstance(value, list):
            for timeStr in value:
                if len(timeStr) != 14 or not self.isVaildDate(timeStr, "%Y%m%d%H%M%S"):
                    return -1

        if len(contNo) > 0:
            self._metaData['SubContract'].append(contNo)
        trigger = self._metaData['Trigger']

        trigger['SnapShot'] = True if type == 1 else False
        trigger['Trade'] = True if type == 2 else False
        trigger['Cycle'] = value if type == 3 else None
        trigger['Timer'] = value if type ==4 else None

        return 0

    def setSample(self, sampleType, sampleValue):
        '''设置样本数据'''
        pass
        '''
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
        '''

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

    def getBarIntervalList(self, contNo):
        if contNo not in self._metaData['BarInterval']:
            return []
        return self._metaData['BarInterval'][contNo]

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

    def setBarInterval(self, contNo, barType, barInterval, sampleConfig, trigger=True):
        '''设置K线类型和K线周期'''
        if barType not in ('t', 'T', 'S', 'M', 'H', 'D', 'W', 'm', 'Y'):
            return -1

        # 清空界面设置的合约K线信息
        contract = self._metaData['Contract']
        defaultBenchmark = contract[0] if len(contract) > 0 and len(contract[0]) else ""
        if len(defaultBenchmark) > 0:
            if defaultBenchmark in self._metaData['Sample']:
                del self._metaData['Sample'][defaultBenchmark]
            self._metaData['Sample']['Display']['ContractNo'] = None
            self._metaData['SubContract'] = []

        # 添加订阅合约
        self._metaData['SubContract'].append(contNo)

        # 记录展示的合约和K线信息
        if barType == EEQU_KLINE_SECOND:
            barType = EEQU_KLINE_TICK
        elif barType == EEQU_KLINE_HOUR:
            barType = EEQU_KLINE_MINUTE
            barInterval = barInterval * 60
        elif barType == EEQU_KLINE_TICK:
            barInterval = 0
        if not self._metaData['Sample']['Display']['ContractNo']:
            self._metaData['Sample']['Display'] = {"ContractNo" : contNo, "KLineType": barType, "KLineSlice": barInterval}

        # 更新回测起始点信息
        sampleInfo = {
            'KLineType': barType,
            'KLineSlice': barInterval,
            'BeginTime' : sampleConfig if isinstance(sampleConfig, str) and self.isVaildDate(sampleConfig, "%Y%m%d") else '',
            'KLineCount' : sampleConfig if isinstance(sampleConfig, int) and sampleConfig > 0 else (1 if sampleConfig == 'N' else 0),
            'AllK' : True if sampleConfig == 'A' else False,
            'UseSample' : False if sampleConfig == 'N' else True,
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
