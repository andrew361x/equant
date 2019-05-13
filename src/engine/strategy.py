#-*-:conding:utf-8-*-

from multiprocessing import Process, Queue
from threading import Thread
from .thread import QuantThread
import time, os, sys
from capi.com_types import *
from api import base_api
from .strategy_model import StrategyModel
from .engine_model import DataModel
from capi.event import Event
import traceback
import importlib
import queue
import datetime
from datetime import datetime


class StartegyManager(object):
    '''策略进程管理器，负责进程创建、销毁、暂停等'''

    def __init__(self, logger, st2egQueue):
        self.logger = logger

        # 策略进程到引擎的队列
        self._st2egQueue = st2egQueue

        # 进程字典，{'id', Strategy}
        self._strategyDict = {}
        self._strategyProcess = {}

    @staticmethod
    def run(strategy):
        strategy.run()
        
    def stop(self, strategyId=0, mode='S'):
        '''
        说明: 停止策略线程
        参数:
              strategyId, 策略id，为0则停止所有策略
              mode,停止的线程,A-停止进程,S-停止策略线程
        '''
        pass

    def create(self, id, queue, event):
        qdict = {'eg2st': queue, 'st2eg': self._st2egQueue}
        strategy = Strategy(self.logger, id, event, qdict)
        self._strategyDict[id] = strategy

        process = Process(target=self.run, args=(strategy,))
        process.daemon = True
        process.start()
        self._strategyProcess[id] = process

    def sendEvent2Strategy(self, id, event):
        if id not in self._strategyDict:
            self.logger.info("策略 %d 不存在" % id)
            return
        strategy = self._strategyDict[id]
        eg2stQueue, _ = strategy.getQueues()
        eg2stQueue.put(event)
        
    def _stopStrategy(self, strategyId, mode):
        pass

class StrategyContext:
    def __init__(self):
        pass


class Strategy:
    def __init__(self, logger, id, event, args):
        self._strategyId = id
        self.logger = logger
        
        data = event.getData()
        self._filePath = data['Path']
        self._argsDict = data['Args']
        self._isInitialize = True
        if "NoInitialize" in data:
            self._isInitialize = False

        # print("now config is")
        # for k, v in self._argsDict.items():
        #    print(k,":",v)

        self._eg2stQueue = args['eg2st']
        self._st2egQueue = args['st2eg']
        moduleDir, moduleName = os.path.split(self._filePath)
        self._strategyName = ''.join(moduleName.split('.')[:-1])

        # 策略所在进程状态, Ready、Running、Exit、Pause
        self._strategyState = StrategyStatusReady
        #
        self._runStatus = ST_STATUS_NONE
        self._runRealTimeStatus = ST_STATUS_NONE

        # self._strategyId+"-"+self._eSessionId 组成本地生成的eSessionId
        self._eSessionId = 1
        # 该策略的所有下单信息
        self._localOrder = {} # {本地生成的eSessionId : 下单数据}
        # api 返回的SessionId到本地生成的eSessionId的映射关系
        self._sesnId2eSesnIdMap = {} # {api 返回的SessionId : 本地生成的eSessionId}
        # 本地生成的eSessionId到委托号的映射关系
        self._eSesnId2orderNoMap = {} # {本地生成的eSessionId : 委托号}

    # ////////////////////////////对外接口////////////////////
    def _initialize(self):
        self._strategyState = StrategyStatusRunning
        moduleDir, moduleName = os.path.split(self._filePath)
        moduleName = os.path.splitext(moduleName)[0]

        if moduleDir not in sys.path:
            sys.path.insert(0, moduleDir)
        try:
            # 1. 加载用户策略
            userModule = importlib.import_module(moduleName)
            
            # 2. 创建策略上下文
            self._context = StrategyContext()
            
            # 3. 创建数据模块
            self._dataModel = StrategyModel(self)
            
            # 4. 初始化系统函数
            self._baseApi = base_api.baseApi.updateData(self, self._dataModel)
            userModule.__dict__.update(base_api.__dict__)
            
            # 5. 初始化用户策略参数
            if self._isInitialize:
                userModule.initialize(self._context)
                # print("strategy config is ")
                # print(self._dataModel.getConfigModel().getConfig())
            self._userModule = userModule
            
            # 6. 初始化model
            self._dataModel.initialize()

            # 7.  注册处理函数
            self._regEgCallback()
            
            # 8. 启动策略运行线程
            self._triggerQueue = queue.Queue()
            self._startStrategyThread()
            
            # 9. 启动策略心跳线程
            self._startStrategyTimer()

        except Exception as e:
            errorText = traceback.format_exc()
            # traceback.print_exc()
            self._strategyState = StrategyStatusExit
            self._exit(-1, errorText)

    def run(self):
        try:
            # 1. 内部初始化
            self._initialize()
            # 2. 请求交易所、品种等
            self._reqCommodity()
            # 2. 订阅即时行情
            self._subQuote()
            # 3. 请求历史行情
            self._reqHisQuote()
            # 4. 查询交易数据
            self._reqTradeData()
            # 5. 数据处理
            self._mainLoop()
        except Exception as e:
            errorText = traceback.format_exc()
            # traceback.print_exc()
            self._exit(-1, errorText)
    
    # ////////////////////////////内部接口////////////////////
    def _isExit(self):
        return self._strategyState == StrategyStatusExit

    def _isPause(self):
        return self._strategyState == StrategyStatusPause

    # 从engine进程接受事件并处理
    def _mainLoop(self):
        while not self._isExit():
            event = self._eg2stQueue.get()
            code = event.getEventCode()
            if code not in self._egCallbackDict:
                self.logger.error("_egCallbackDict code(%d) not register!"%code)
                continue
            self._egCallbackDict[code](event) 
        
    def _runStrategy(self):
        # 等待回测阶段
        self._runStatus = ST_STATUS_HISTORY
        self._send2UIStatus(self._runStatus)
        # runReport中会有等待
        self._dataModel.runReport(self._context, self._userModule.handle_data)

        # 持续运行阶段
        self._runStatus = ST_STATUS_CONTINUES
        self._send2UIStatus(self._runStatus)
        
        while not self._isExit():
            event = self._triggerQueue.get()
            # 发单方式，实时发单、k线稳定后发单。
            eventCode = event.getEventCode()
            if self._isPause():
                if eventCode == ST_TRIGGER_FILL_DATA:
                    self._dataModel.runRealTime(self._context, self._userModule.handle_data, event)
                else:
                    continue
            else:
                self._dataModel.runRealTime(self._context, self._userModule.handle_data, event)

    def _startStrategyThread(self):
        '''历史数据准备完成后，运行策略'''
        self._stThread = Thread(target=self._runStrategy)
        self._stThread.start()
        
    def _triggerTime(self):
        '''检查定时触发'''
        if not self._dataModel.getConfigModel().hasTimerTrigger():
            return

        nowStr = datetime.now().strftime("%Y%m%d%H%M%S")
        for i,timeSecond in enumerate(self._dataModel.getConfigData()['Trigger']['Timer']):
            if 0<=(int(nowStr)-int(timeSecond))<1 and not self._isTimeTriggered[i]:
                self._isTimeTriggered[i] = True
                event = Event({
                    "EventCode" : ST_TRIGGER_TIMER,
                    "ContractNo": self._dataModel.getConfigModel().getBenchmark(),
                    "Data":{
                        "TriggerType":"Timer"
                    }
                })
                self._triggerQueue.put(event)
        
    def _triggerCycle(self):
        '''检查周期性触发'''
        if not self._dataModel.getConfigModel().hasCycleTrigger():
            return

        nowTime = datetime.now()
        cycle = self._dataModel.getConfigData()['Trigger']['Cycle']
        if (nowTime - self._nowTime).total_seconds()*1000>cycle:
            self._nowTime = nowTime
            event = Event({
                "EventCode": ST_TRIGGER_CYCLE,
                "ContractNo": self._dataModel.getConfigModel().getBenchmark(),
                "Data":{
                    "TriggerType":"CYCLE"
                }
            })
            self._triggerQueue.put(event)
        
    def _runTimer(self):
        timeList = self._dataModel.getConfigData()['Trigger']['Timer']
        if timeList is None:
            timeList = []
        self._isTimeTriggered = [False for i in timeList]
        self._nowTime = datetime.now()
        '''秒级定时器'''
        while not self._isExit() and not self._isPause():
            # 定时触发
            self._triggerTime()
            # 周期性触发
            self._triggerCycle()
            # 休眠100ms
            time.sleep(0.1)
        
    def _startStrategyTimer(self):
        self._stTimer = Thread(target=self._runTimer)
        self._stTimer.start()
        
    def _send2UIStatus(self, status):
        '''通知界面策略运行状态'''
        event = Event({
            "StrategyId" : self._strategyId,
            "EventCode"  : EV_EG2UI_STRATEGY_STATUS,
            "Data"       : {
                'Status' : status
            }
        })
        
        self.sendEvent2Engine(event)
    
    def _regEgCallback(self):
        self._egCallbackDict = {
            EV_EG2ST_COMMODITY_RSP          : self._onCommodity        ,
            EV_EG2ST_SUBQUOTE_RSP           : self._onQuoteRsp         ,
            EV_EG2ST_SNAPSHOT_NOTICE        : self._onQuoteNotice      ,
            EV_EG2ST_DEPTH_NOTICE           : self._onDepthNotice      ,
            EV_EG2ST_HISQUOTE_RSP           : self._onHisQuoteRsp      ,
            EV_EG2ST_HISQUOTE_NOTICE        : self._onHisQuoteNotice   ,
            EV_UI2EG_REPORT                 : self._onReport           ,
            EV_UI2EG_LOADSTRATEGY           : self._onLoadStrategyResponse,

            EV_EG2ST_TRADEINFO_RSP          : self._onTradeInfo         ,
            EEQU_SRVEVENT_TRADE_ORDER       : self._onTradeOrder        ,
            EV_EG2ST_ACTUAL_ORDER_ENGINE_RESPONSE: self._onTradeOrderEngineResponse,
            EV_EG2ST_ACTUAL_ORDER_SESSION_MAP: self._onOrderSessionMap,
            EEQU_SRVEVENT_TRADE_MATCH       : self._onTradeMatch        ,
            EEQU_SRVEVENT_TRADE_POSITION    : self._onTradePosition     ,
            EEQU_SRVEVENT_TRADE_FUNDQRY     : self._onTradeFundRsp      ,

            EV_UI2EG_STRATEGY_QUIT          : self._onStrategyQuit,
            EV_UI2EG_EQUANT_EXIT            : self._onEquantExit,
            EV_UI2EG_STRATEGY_FIGURE        : self._switchStrategy,
        }
    
    # ////////////////////////////内部数据请求接口////////////////////
    def _reqCommodity(self):
        self._dataModel.reqCommodity()

    # 订阅即时tick、 k线
    def _subQuote(self):
        self._dataModel.subQuote()

    # 请求历史tick、k线数据
    def _reqHisQuote(self):
        self._dataModel.reqHisQuote()

    # 查询交易数据
    def _reqTradeData(self):
        self._dataModel.reqTradeData()
        
    #////////////////////////////内部数据应答接口////////////////////
    def _onCommodity(self, event):
        '''品种查询应答'''
        self._dataModel.onCommodity(event)
        self._dataModel.initializeCalc()
            
    def _onQuoteRsp(self, event):
        '''行情应答，来着策略引擎'''
        self._dataModel.onQuoteRsp(event)
        
    def _onQuoteNotice(self, event):
        self._dataModel.onQuoteNotice(event)
        
    def _onDepthNotice(self, event):
        self._dataModel.onDepthNotice(event)

    def _onHisQuoteRsp(self, event):
        '''历史数据请求应答'''
        self._dataModel.onHisQuoteRsp(event)
        
    def _onHisQuoteNotice(self, event):
        self._dataModel.onHisQuoteNotice(event)

    # 报告事件, 发到engine进程中，engine进程 再发到ui进程。
    def _onReport(self, event):
        data = self._dataModel.getCalcCenter().testResult()
        responseEvent = Event({
            "EventCode":EV_EG2UI_REPORT_RESPONSE,
            "StrategyId":self._strategyId,
            "Data":{
                "Result":data,
                "BeginTradeDate":self._dataModel.getHisQuoteModel().getBeginDate(),
                "EndTradeDate":self._dataModel.getHisQuoteModel().getEndDate(),
            }
        })
        self.sendEvent2Engine(responseEvent)

    def getQueues(self):
        return self._eg2stQueue, self._st2egQueue

    def _onLoadStrategyResponse(self, event):
        '''向界面返回策略加载应答'''
        cfg = self._dataModel.getConfigData()
        
        revent = Event({
            "EventCode" : EV_EG2UI_LOADSTRATEGY_RESPONSE,
            "StrategyId": self._strategyId,
            "ErrorCode" : 0,
            "ErrorText" : "",
            "Data":{
                "StrategyId"   : self._strategyId,
                "StrategyName" : self._strategyName,
                "StrategyState": self._runStatus,
                "Config"       : cfg,
            }
        })
        
        self.sendEvent2Engine(revent)

    def _onTradeInfo(self, event):
        '''
        请求用户登录/账户信息
        :param event: 引擎返回事件
        :return: None
        '''
        data = event.getData()
        if len(data) == 0:
            # 用户未登录
            return

        # 更新登录账号信息
        loginInfo = data['loginInfo']
        self._dataModel._trdModel.updateLoginInfoFromDict(loginInfo)

        # 更新资金账号信息
        userInfo = data['userInfo']
        self._dataModel._trdModel.updateUserInfoFromDict(userInfo)

    def _onTradeOrder(self, apiEvent):
        '''
        交易委托信息发生变化时，更新交易模型信息
        :param apiEvent: 引擎返回事件
        :return: None
        '''
        self._dataModel._trdModel.updateOrderData(apiEvent)

        # 更新本地订单信息
        dataList = apiEvent.getData()
        for data in dataList:
            sessionId = data['SessionId']
            if sessionId in self._sesnId2eSesnIdMap:
                self._eSesnId2orderNoMap[self._sesnId2eSesnIdMap[sessionId]] = data['OrderNo']

        if not self._dataModel.getConfigModel().hasTradeTrigger():
            return

        # print(apiEvent.getEventCode(), apiEvent.getStrategyId())
        if apiEvent.getEventCode() == EEQU_SRVEVENT_TRADE_ORDER and str(apiEvent.getStrategyId()) == str(self._strategyId):
            # print("交易触发===================11111")
            tradeTriggerEvent = Event({
                "EventCode":ST_TRIGGER_TRADE,
                "Data":{
                    "TriggerType":"Trade",
                    "Data": apiEvent.getData()
                }
            })

            # 交易触发
            self.sendTriggerQueue(tradeTriggerEvent)

    def _onTradeOrderEngineResponse(self, event):
        self._dataModel.getTradeModel().updateEquantOrder(event)

    def _onOrderSessionMap(self, event):
        self.updateSesnId2eSesnIdMap(event.getSessionId(), event.getESessionId())

    def _onTradeMatch(self, apiEvent):
        '''
        交易成交信息发生变化时，更新交易模型信息
        :param apiEvent: 引擎返回事件
        :return: None
        '''
        self._dataModel._trdModel.updateMatchData(apiEvent)

    def _onTradePosition(self, apiEvent):
        '''
        交易持仓信息发生变化时，更新交易模型信息
        :param apiEvent: 引擎返回事件
        :return: None
        '''
        self._dataModel._trdModel.updatePosData(apiEvent)

    def _onTradeFundRsp(self, apiEvent):
        '''
        交易资金信息发生变化时，更新交易模型信息
        :param apiEvent: 引擎返回事件
        :return: None
        '''
        self._dataModel._trdModel.updateMoney(apiEvent)

    def getStrategyId(self):
        return self._strategyId

    def getESessionId(self):
        return self._eSessionId

    def setESessionId(self, eSessionId):
        if eSessionId <= 0:
            return 0
        self._eSessionId = eSessionId

    def updateSesnId2eSesnIdMap(self, sesnId, eSesnId):
        self._sesnId2eSesnIdMap[sesnId] = eSesnId

    def updateLocalOrder(self, eSesnId, data):
        self._localOrder[eSesnId] = data

    def getOrderNo(self, eSessionId):
        if eSessionId in self._eSesnId2orderNoMap:
            return self._eSesnId2orderNoMap[eSessionId]
        return 0

    def getSessionId(self, eSessionId):
        for sesn, sSesn in self._sesnId2eSesnIdMap.item():
            if sSesn == eSessionId:
                return sesn
        return 0

    def getStrategyName(self):
        return self._strategyName

    def isRealTimeStatus(self):
        return self._runStatus == ST_STATUS_CONTINUES and self._runRealTimeStatus == ST_STATUS_CONTINUES_AS_REALTIME

    def isHisStatus(self):
        return self._runStatus == ST_STATUS_HISTORY

    def isRealTimeAsHisStatus(self):
        return self._runStatus == ST_STATUS_CONTINUES and self._runRealTimeStatus == ST_STATUS_CONTINUES_AS_HISTORY

    # set run real time status
    def setRunRealTimeStatus(self, status):
        self._runRealTimeStatus = status

    def sendEvent2Engine(self, event):
        self._st2egQueue.put(event)

    def sendTriggerQueue(self, event):
        self._triggerQueue.put(event)

    def _exit(self, errorCode, errorText):
        event = Event({
            "EventCode":EV_EG2UI_CHECK_RESULT,
            "StrategyId":self._strategyId,
            "Data":{
                "ErrorCode":errorCode,
                "ErrorText":errorText,
            }
        })

        self.sendEvent2Engine(event)
        import time,os
        time.sleep(5)
        os._exit(0)

    # 停止策略
    def _onStrategyQuit(self, event):
        self._strategyState = StrategyStatusExit
        quitEvent = Event({
            "EventCode": EV_EG2UI_STRATEGY_STATUS,
            "StrategyId": self._strategyId,
            "Data":{
                "Status":ST_STATUS_QUIT,
                "Config":self._dataModel.getConfigData(),
                "Pid":os.getpid(),
                "Path":self._filePath,
                "StrategyName": self._strategyName,
            }
        })

        self.sendEvent2Engine(quitEvent)

    def _onEquantExit(self, event):
        self._strategyState = StrategyStatusExit
        responseEvent = Event({
            "EventCode": EV_EG2UI_STRATEGY_STATUS,
            "StrategyId": self._strategyId,
            "Data": {
                "Status": event.getEventCode(),
                "Config": self._dataModel.getConfigData(),
                "Pid": os.getpid(),
                "Path": self._filePath,
                "StrategyName":self._strategyName,
            }
        })
        self.sendEvent2Engine(responseEvent)

    def _switchStrategy(self, event):
        contNo = self._dataModel.getConfigModel().getContract()[0]
        self._dataModel.getHisQuoteModel()._switchKLine(contNo)