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
import copy
from collections import OrderedDict
from .trigger_mgr import TriggerMgr


class StartegyManager(object):
    '''策略进程管理器，负责进程创建、销毁、暂停等'''

    def __init__(self, logger, st2egQueue):
        self.logger = logger

        # 策略进程到引擎的队列
        self._st2egQueue = st2egQueue

        # 进程字典，{'id', Strategy}
        self._strategyDict = {}
        self._strategyInfo = {}
        self._strategyAttribute = {}
        self._isEquantExitStage = False
        self._isEquantExitCom = False

    @staticmethod
    def run(strategy):
        strategy.run()

    def getStrategyState(self, strategyId):
        assert strategyId in self._strategyInfo, 'error '
        return self._strategyInfo[strategyId]["StrategyState"]

    def handleStrategyException(self, event):
        strategyId = event.getStrategyId()
        if strategyId not in self._strategyInfo:
            return
        self._strategyInfo[strategyId]["StrategyState"] = ST_STATUS_EXCEPTION
        self.destroyProcessByStrategyId(event.getStrategyId())
        self._strategyInfo[strategyId]["Process"] = None

    def create(self, strategyId, eg2stQueue, eg2uiQueue, st2egQueue, event):
        qdict = {'eg2st': eg2stQueue, 'st2eg': st2egQueue, 'st2ui':eg2uiQueue}
        strategy = Strategy(self.logger, strategyId, qdict, event)
        self._strategyDict[strategyId] = strategy
        process = Process(target=self.run, args=(strategy,))
        process.daemon = True
        process.start()

        args = {
            "Config": event.getData()["Args"],
            # "UIConfig": copy.deepcopy(event.getData()["Args"]),
            "Path": event.getData()["Path"],
            "StrategyName": None,
            "StrategyId": strategyId,
        }

        self.insertNewStrategy(strategyId, process, args)

    # 新建策略、恢复策略调用
    def insertNewStrategy(self, strategyId, process, args):
        self._strategyInfo[strategyId] = {
            "StrategyId": strategyId,
            "Process": process,
            "StrategyState": ST_STATUS_NONE,
        }
        self._strategyAttribute[strategyId] = args

    def insertResumedStrategy(self, strategyId, args):
        self._strategyInfo[strategyId] = {
            "StrategyId": strategyId,
            "Process": None,
            "StrategyState": ST_STATUS_QUIT,
        }
        # 策略恢复的时候用
        self._strategyAttribute[strategyId] = args

    def quitStrategy(self, event):
        strategyId = event.getStrategyId()
        assert strategyId in self._strategyInfo and self._strategyInfo[strategyId]["Process"].is_alive(), " error "
        strategyInfo = self._strategyInfo[strategyId]
        strategyInfo["StrategyState"] = ST_STATUS_QUIT
        self.destroyProcess(self._strategyInfo[strategyId]["Process"], strategyId)
        strategyInfo["Process"] = None

    def removeQuitedStrategy(self, event):
        assert event.getStrategyId() in self._strategyInfo, "error"
        self._strategyInfo.pop(event.getStrategyId())
        self._strategyAttribute.pop(event.getStrategyId())

    def removeRunningStrategy(self, event):
        strategyId = event.getStrategyId()
        if strategyId not in self._strategyInfo:
            self.logger.error(f"策略{strategyId}在engine已经被删除了")
            return
        # assert strategyId in self._strategyInfo, "error"
        self.destroyProcess(self._strategyInfo[strategyId]['Process'], strategyId)
        self._strategyInfo.pop(strategyId)
        self._strategyAttribute.pop(event.getStrategyId())

    def removeExceptionStrategy(self, event):
        self.removeRunningStrategy(event)

    def restartStrategy(self, engineLoadFunc, event):
        assert event.getStrategyId() in self._strategyInfo, "error"
        strategyInfo = self._strategyAttribute[event.getStrategyId()]
        loadStrategyEvent = Event({
            'EventSrc': EEQU_EVSRC_UI,
            'EventCode': EV_UI2EG_LOADSTRATEGY,
            'SessionId': None,
            'StrategyId': 0,
            'UserNo': '',
            'Data': {
                'Path': strategyInfo["Path"],
                'Args': strategyInfo["Config"],
                "NoInitialize": True,
            }
        })
        engineLoadFunc(loadStrategyEvent, strategyId=event.getStrategyId())

    def singleStrategyExitComEquantExit(self, event):
        self._isEquantExitStage = True
        strategyId = event.getStrategyId()
        assert strategyId in self._strategyInfo, " error "
        strategyInfo = self._strategyInfo[event.getStrategyId()]
        strategyInfo["StrategyState"] = ST_STATUS_QUIT
        #

    def isAllStrategyQuit(self):
        result = True
        for k, v in self._strategyInfo.items():
            if v["StrategyState"] != ST_STATUS_QUIT and v["StrategyState"] != ST_STATUS_EXCEPTION:
                result = False
                break
        # print("now is equant exit complete ", result)
        return result

    def stopStrategy(self, strategyId):
        pass

    def resumeStrategy(self, strategyId):
        pass

    def destroyProcessByStrategyId(self, strategyId):
        assert strategyId in self._strategyInfo, " error "
        process = self._strategyInfo[strategyId]["Process"]
        self.destroyProcess(process, strategyId)
        self._strategyInfo[strategyId]["Process"] = None

    def destroyProcess(self, process, strategyId):
        if not process or not process.is_alive:
            self.logger.info(f"策略{strategyId}所在进程已经退出，将忽略")
            return
        try:
            process.terminate()
            process.join(timeout=1)
            self.logger.debug("strategy %d exit success" % strategyId)
        except Exception as e:
            # traceback.print_exc()
            self.logger.debug("strategy %d exit fail" % strategyId)

    def syncStrategyConfig(self, event):
        strategyId = event.getStrategyId()
        self._strategyAttribute[strategyId] = event.getData()

    def getStrategyConfig(self):
        result = {}
        for strategyId, value in self._strategyInfo.items():
            if value["StrategyState"] == ST_STATUS_EXCEPTION:
                continue
            v = self._strategyAttribute[strategyId]
            result[strategyId] = {
                "Config":v["Config"],
                "Path":v["Path"],
                "StrategyName":v["StrategyName"],
                "StrategyId":strategyId,
                #"UIConfig":v["UIConfig"]
            }
        result = OrderedDict(sorted(result.items(), key=lambda obj: str(obj[0])))
        return result

    def getStrategyAttribute(self, strategyId):
        return self._strategyAttribute[strategyId]


class StrategyContext:
    def __init__(self):
        self._strategyStatus = None
        self._triggerType = None
        self._conTractNo = None
        self._kLineType = None
        self._kLineSlice = None
        self._tradeDate = None
        self._dateTimeStamp = None
        self._triggerData = None
        self._parameter = {}

    def strategyStatus(self):
        return self._strategyStatus

    def triggerType(self):
        return self._triggerType

    def contractNo(self):
        return self._conTractNo

    def kLineType(self):
        return self._kLineType

    def kLineSlice(self):
        return self._kLineSlice

    def tradeDate(self):
        if self._tradeDate is not None:
            return str(self._tradeDate)
        else:
            return None

    def dateTimeStamp(self):
        if self._dateTimeStamp is not None:
            return str(self._dateTimeStamp)
        else:
            return None

    def triggerData(self):
        return self._triggerData

    def setCurTriggerSourceInfo(self, args):
        self._strategyStatus = copy.deepcopy(args["Status"])
        self._triggerType = copy.deepcopy(args["TriggerType"])
        self._conTractNo = copy.deepcopy(args["ContractNo"])
        self._kLineType = copy.deepcopy(args["KLineType"])
        self._kLineSlice = copy.deepcopy(args["KLineSlice"])
        self._tradeDate = copy.deepcopy(args["TradeDate"])
        self._dateTimeStamp = copy.deepcopy(args["DateTimeStamp"])
        self._triggerData = copy.deepcopy(args["TriggerData"])

    @property
    def params(self):
        return self._parameter

    @params.setter
    def params(self, parameter):
        self._parameter = parameter




class TradeRecord(object):
    def __init__(self, eSessionId, orderData={}):
        self._eSessionId = eSessionId   # eSessionId
        self._barInfo = None # 触发的Bar信息
        # SessionId
        self._sessionId = orderData['SessionId'] if 'SessionId' in orderData else None
        # 合约编号
        self._contNo = orderData['Cont'] if 'Cont' in orderData else None
        # 定单号
        self._orderId = orderData['OrderId'] if 'OrderId' in orderData else None
        # 委托单号
        self._orderNo = orderData['OrderNo'] if 'OrderNo' in orderData else None
        # 方向
        self._direct = orderData['Direct'] if 'Direct' in orderData else None
        # 开平
        self._offset = orderData['Offset'] if 'Offset' in orderData else None
        # 订单状态
        self._orderState = orderData['OrderState'] if 'OrderState' in orderData else None
        # 委托成交价
        self._matchPrice = orderData['MatchPrice'] if 'MatchPrice' in orderData else None
        # 委托成交量
        self._matchQty = orderData['MatchQty'] if 'MatchQty' in orderData else None

    def updateOrderInfo(self, eSessionId, orderData):
        if eSessionId != self._eSessionId:
            return

        if 'SessionId' in orderData:
            self._sessionId = orderData['SessionId']
        if 'Cont' in orderData:
            self._contNo = orderData['Cont']
        if 'OrderId' in orderData:
            self._orderId = orderData['OrderId']
        if 'OrderNo' in orderData:
            self._orderNo = orderData['OrderNo']
        if 'Direct' in orderData:
            self._direct = orderData['Direct']
        if 'Offset' in orderData:
            self._offset = orderData['Offset']
        if 'OrderState' in orderData:
            self._orderState = orderData['OrderState']
        if 'MatchPrice' in orderData:
            self._matchPrice = orderData['MatchPrice']
        if 'MatchQty' in orderData:
            self._matchQty = orderData['MatchQty']

    def getBarInfo(self):
        return self._barInfo


class Strategy:
    def __init__(self, logger, id, args, event):
        self._strategyId = id
        self.logger = logger
        self._dataModel = None
        
        data = event.getData()
        self._filePath = data['Path']
        self._argsDict = data['Args']
        # 是否运行initialize函数
        self._noInitialize = "NoInitialize" in data and data["NoInitialize"]
        self._uiConfig = copy.deepcopy(data['Args'])

        self._eg2stQueue = args['eg2st']
        self._st2egQueue = args['st2eg']
        self._isSt2EgQueueEffective = True
        self._st2uiQueue = args['st2ui']
        moduleDir, moduleName = os.path.split(self._filePath)
        self._strategyName = ''.join(moduleName.split('.')[:-1])
        self._triggerMgr = None

        # 策略所在进程状态, Ready、Running、Exit、Pause
        self._strategyState = StrategyStatusReady
        #
        self._runStatus = ST_STATUS_NONE
        self._curTriggerSourceInfo = None
        self._firstTriggerQueueEmpty = True

        # self._strategyId+"-"+self._eSessionId 组成本地生成的eSessionId
        self._eSessionId = 1
        # 该策略的所有下单信息
        self._eSessionIdList = [] # 存储本地生成的eSessionId，为了保存下单顺序信息
        self._localOrder = {} # {本地生成的eSessionId : TradeRecode对象}
        
        self._moneyLastTime = 0
        #self._userModelDict = {}

    # ////////////////////////////对外接口////////////////////
    
    def _initialize(self):
        self._strategyState = StrategyStatusRunning
        #用户模板函数路径加入系统路径，并扩展baseapi的作用域
        workPath = os.path.abspath('.')
        userPath = workPath + "\strategy\FuncTemplate"
        if userPath not in sys.path:
            sys.path.insert(0, userPath)
        
        moduleDir, moduleName = os.path.split(self._filePath)
        moduleName = os.path.splitext(moduleName)[0]

        if moduleDir not in sys.path:
            sys.path.insert(0, moduleDir)
            
        # 3. 创建数据模块
        self._dataModel = StrategyModel(self)
        
        self._userModelDict = {}

        # 4. 初始化系统函数
        self._baseApi = base_api.baseApi.updateData(self, self._dataModel)
        # 扩展用户模板函数作用域
        if os.path.exists(userPath):
            userDir = os.listdir(userPath)
            for file in userDir:
                modelFile = os.path.splitext(file)[0]
                model = importlib.import_module(modelFile)
                model.__dict__.update(base_api.__dict__)
                self._userModelDict[modelFile] = model

        # 1. 加载用户策略
        userModule = importlib.import_module(moduleName)
        userModule.__dict__.update(base_api.__dict__)

        # 2. 创建策略上下文
        self._context = StrategyContext()

        # 5. 初始化用户策略参数
        if not self._noInitialize:
            userModule.initialize(self._context)
            self._argsDict["Params"] = self._context.params
            self._dataModel.getConfigModel().setParams(self._context.params)
        else:
            self._context.params = self._argsDict["Params"]

        self._userModule = userModule
        # 5.1 同步配置
        self._sendConfig2Engine()

        self._triggerMgr = TriggerMgr(list(self._dataModel.getConfigModel().getKLineKindsInfo()), self)

        # 6. 初始化model
        self._dataModel.initialize()

        # 7.  注册处理函数
        self._regEgCallback()

        # 8. 启动策略运行线程
        self._triggerQueue = queue.Queue()
        self._startStrategyThread()

        # 9. 启动策略心跳线程
        self._startStrategyTimer()

    def run(self):
        try:
            # 1. 内部初始化
            self._initialize()
            # 1.1 请求交易所、品种、合约等
            self._reqExchange()
            self._reqCommodity()
            # self._reqContract()
            # 1.2 请求主力/近月/指数合约映射合约信息
            self._reqUnderlayMap()
            # 2. 订阅即时行情
            self._subQuote()
            # 3. 请求历史行情
            self._reqHisQuote()
            # 4. 查询交易数据
            self._reqTradeData()
            # 5. 数据处理
            self._mainLoop()
        except Exception as e:
            self._strategyState = StrategyStatusExit
            self._isSt2EgQueueEffective = False
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
        while True:
            if self._isExit():
                time.sleep(0.2)
                self._clearQueue(self._eg2stQueue)
                continue
            event = self._eg2stQueue.get()
            code = event.getEventCode()
            if code not in self._egCallbackDict:
                self.logger.error("_egCallbackDict code(%d) not register!"%code)
                continue
            self._egCallbackDict[code](event) 

    def _clearQueue(self, someQueue):
        try:
            while True:
                someQueue.get_nowait()
        except queue.Empty:
            pass

    def _runStrategy(self):
        try:
            # 等待回测阶段
            self._runStatus = ST_STATUS_HISTORY
            self._send2UIStatus(self._runStatus)
            # runReport中会有等待

            self._dataModel.runReport(self._context, self._userModule.handle_data)

            # 持续运行阶段
            # 1. 中间阶段, 实际上还是作为历史回测
            # 2. 真正的实时阶段
            # self._runStatus = ST_STATUS_HISTORY
            # self._send2UIStatus(self._runStatus)
            #
            
            if not self._dataModel.getConfigModel().isActualRun():
                self.logger.warn(f"未选择实盘运行，如果需要请在设置界面勾选'实盘运行'，或者在策略代码中调用SetActual()")

            while not self._isExit():
                try:
                    event = self._triggerQueue.get_nowait()
                    # 发单方式，实时发单、k线稳定后发单。
                    self._dataModel.runRealTime(self._context, self._userModule.handle_data, event)
                except queue.Empty as e:
                    if self._firstTriggerQueueEmpty:
                        self._runStatus = ST_STATUS_CONTINUES
                        self._send2UIStatus(self._runStatus)
                        self._firstTriggerQueueEmpty = False
                    else:
                        time.sleep(0.1)
        except Exception as e:
                self._strategyState = StrategyStatusExit
                self._isSt2EgQueueEffective = False
                errorText = traceback.format_exc()
                # traceback.print_exc()
                self._exit(-1, errorText)

    def _startStrategyThread(self):
        '''历史数据准备完成后，运行策略'''
        self._stThread = Thread(target=self._runStrategy)
        self._stThread.start()
        
    def _triggerTime(self):
        '''检查定时触发'''
        if not self._dataModel.getConfigModel().hasTimerTrigger() or not self.isRealTimeStatus():
            return

        nowStr = datetime.now().strftime("%Y%m%d%H%M%S")
        for i,timeSecond in enumerate(self._dataModel.getConfigTimer()):
            if 0<=(int(nowStr)-int(timeSecond))<1 and not self._isTimeTriggered[i]:
                self._isTimeTriggered[i] = True
                key = self._dataModel.getConfigModel().getKLineShowInfoSimple()
                dateTimeStamp, tradeDate, lv1Data = self.getTriggerTimeAndData(key[0])
                event = Event({
                    "EventCode" : ST_TRIGGER_TIMER,
                    "ContractNo": None,
                    "KLineType" : None,
                    "KLineSlice": None,
                    "Data":{
                        "TradeDate": tradeDate,
                        "DateTimeStamp": dateTimeStamp,
                        "Data":timeSecond
                    }
                })
                self._triggerQueue.put(event)
        
    def _triggerCycle(self):
        '''检查周期性触发'''
        if not self._dataModel.getConfigModel().hasCycleTrigger():
            return

        if not self.isRealTimeStatus():
            return

        nowTime = datetime.now()
        cycle = self._dataModel.getConfigCycle()
        if (nowTime - self._nowTime).total_seconds()*1000>cycle:
            self._nowTime = nowTime
            key = self._dataModel.getConfigModel().getKLineShowInfoSimple()
            dateTimeStamp, tradeDate, lv1Data = self.getTriggerTimeAndData(key[0])
            event = Event({
                "EventCode": ST_TRIGGER_CYCLE,
                "ContractNo": None,
                "KLineType" : None,
                "KLineSlice": None,
                "Data":{
                    "TradeDate": tradeDate,
                    "DateTimeStamp": dateTimeStamp,
                    "Data": None,
                }
            })
            self._triggerQueue.put(event)
            
    def _triggerMoney(self):
        nowTime = datetime.now()
        if self._moneyLastTime == 0 or (nowTime - self._moneyLastTime).total_seconds() > 1:
            self._moneyLastTime = nowTime
            data = self._dataModel.getMonResult()
            if len(data) == 0:
                return
            event = Event({
                "StrategyId" : self._strategyId,
                "EventCode": EV_EG2ST_MONITOR_INFO,
                "Data": self._dataModel.getMonResult()
            })

            self.sendEvent2UI(event)

        
    def _runTimer(self):
        timeList = self._dataModel.getConfigTimer()
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
            # 通知资金变化
            self._triggerMoney()
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
        self.sendEvent2UI(event)
    
    def _regEgCallback(self):
        self._egCallbackDict = {
            EV_EG2ST_EXCHANGE_RSP           : self._onExchange         ,
            EV_EG2ST_COMMODITY_RSP          : self._onCommodity        ,
            EV_EG2ST_CONTRACT_RSP           : self._onContract         ,
            EV_ST2EG_UNDERLAYMAPPING_RSP    : self._onUnderlayMap      ,
            EV_EG2ST_SUBQUOTE_RSP           : self._onQuoteRsp         ,
            EV_EG2ST_SNAPSHOT_NOTICE        : self._onQuoteNotice      ,
            EV_EG2ST_DEPTH_NOTICE           : self._onDepthNotice      ,
            EV_EG2ST_HISQUOTE_RSP           : self._onHisQuoteRsp      ,
            EV_EG2ST_HISQUOTE_NOTICE        : self._onHisQuoteNotice   ,
            EV_UI2EG_REPORT                 : self._onReport           ,
            EV_UI2EG_LOADSTRATEGY           : self._onLoadStrategyResponse,
            EV_EG2ST_TRADEINFO_RSP          : self._onTradeInfo         ,

            EEQU_SRVEVENT_TRADE_LOGINQRY    : self._onTradeLoginQry,
            EEQU_SRVEVENT_TRADE_LOGINNOTICE : self._onTradeLoginNotice,
            EEQU_SRVEVENT_TRADE_USERQRY     : self._onTradeUserQry,
            EEQU_SRVEVENT_TRADE_MATCHQRY    : self._onTradeMatchQry,
            EEQU_SRVEVENT_TRADE_MATCH       : self._onTradeMatch,
            EEQU_SRVEVENT_TRADE_POSITQRY    : self._onTradePositionQry,
            EEQU_SRVEVENT_TRADE_POSITION    : self._onTradePosition,
            EEQU_SRVEVENT_TRADE_FUNDQRY     : self._onTradeFundRsp,
            EEQU_SRVEVENT_TRADE_ORDERQRY    : self._onTradeOrderQry,
            EEQU_SRVEVENT_TRADE_ORDER       : self._onTradeOrder,
            EEQU_SRVEVENT_TRADE_EXCSTATEQRY : self._onExchangeStateNotice      ,
            EEQU_SRVEVENT_TRADE_EXCSTATE    : self._onExchangeStateNotice      ,
            

            EV_UI2EG_STRATEGY_QUIT          : self._onStrategyQuit,
            EV_UI2EG_EQUANT_EXIT            : self._onEquantExit,
            EV_UI2EG_STRATEGY_FIGURE        : self._switchStrategy,
            EV_UI2EG_STRATEGY_REMOVE        : self._onStrategyRemove,

            EV_EG2ST_STRATEGY_SYNC          : self._onSyncEngineInfo,
        }
    
    # ////////////////////////////内部数据请求接口////////////////////
    def _reqExchange(self):
        self._dataModel.reqExchange()

    def _reqCommodity(self):
        self._dataModel.reqCommodity()

    def _reqContract(self):
        self._dataModel.reqContract()

    def _reqUnderlayMap(self):
        self._dataModel.reqUnderlayMap()

    # 订阅即时tick、 k线
    def _subQuote(self):
        self._dataModel.subQuote()

    # 请求历史tick、k线数据
    def _reqHisQuote(self):
        self._dataModel.getHisQuoteModel().reqAndSubKLine()

    # 查询交易数据
    def _reqTradeData(self):
        self._dataModel.reqTradeData()
        
    # ////////////////////////////内部数据应答接口////////////////////
    def _onExchange(self, event):
        '''交易所信息应答'''
        self._dataModel.onExchange(event)

    def _onCommodity(self, event):
        '''品种查询应答'''
        self._dataModel.onCommodity(event)
        self._dataModel.initializeCalc()

    def _onContract(self, event):
        self._dataModel.onContract(event)

    def _onUnderlayMap(self, event):
        self._dataModel.onUnderlayMap(event)
       
    def _onExchangeStateNotice(self, event):
        '''交易所状态'''
        self._dataModel.onExchangeStatus(event)
            
    def _onQuoteRsp(self, event):
        '''行情应答，来着策略引擎'''
        self._dataModel.onQuoteRsp(event)
        
    def _onQuoteNotice(self, event):
        self._dataModel.onQuoteNotice(event)
        self._snapShotTrigger(event)

    # def _calcProfitByQuote(self, event):
    #     data = event.getData()
    #     if len(data) == 0 or (4 not in data[0]["FieldData"]):
    #         # 4:最新价
    #         return
    #
    #     priceInfos = {}
    #     priceInfos[event.getContractNo()] = {
    #         "LastPrice": data[0]["FieldData"][4],
    #         "TradeDate": data[0]["UpdateTime"]//1000000000,
    #         "DateTimeStamp" : data[0]["UpdateTime"],
    #         "LastPriceSource": LastPriceFromQuote
    #     }
    #     self._dataModel.getHisQuoteModel().calcProfitByQuote(event.getContractNo(), priceInfos)

    def _onDepthNotice(self, event):
        self._dataModel.onDepthNotice(event)

    def _onHisQuoteRsp(self, event):
        '''历史数据请求应答'''
        self._dataModel.getHisQuoteModel().onHisQuoteRsp(event)
        
    def _onHisQuoteNotice(self, event):
        self._dataModel.getHisQuoteModel().onHisQuoteNotice(event)
        if self.isRealTimeStatus():
            self._triggerMgr.updateData(event)
            if self._triggerMgr.isAllDataReady(event.getContractNo()):
                self._sendSyncTriggerEvent(event.getContractNo())
                self._triggerMgr.restAllData(event.getContractNo())

    def _sendSyncTriggerEvent(self, contractNo):
        syncTriggerInfo = self._triggerMgr.getSyncTriggerInfo(contractNo)

        # 发送填充k线事件
        for record, dataEvent in syncTriggerInfo.items():
            if record[1] ==0 or record[2] == 0:
                continue

            event = Event({
                "EventCode": ST_TRIGGER_FILL_DATA,
                "ContractNo": record[0],
                "KLineType": record[1],
                "KLineSlice": record[2],
                "Data": {
                    "Data": dataEvent.getData()[0],
                    "Status": ST_STATUS_CONTINUES
                }
            })
            self.sendTriggerQueue(event)

        for record, dataEvent in syncTriggerInfo.items():
            if record == (contractNo, 0, 0):
                dateTimeStamp, tradeDate, lv1Data = self.getTriggerTimeAndData(contractNo)
                event = Event({
                    "EventCode": ST_TRIGGER_SANPSHOT_FILL,
                    "ContractNo": contractNo,
                    "KLineType": None,
                    "KLineSlice": None,
                    "Data": {
                        "Data": lv1Data,
                        "DateTimeStamp": dateTimeStamp,
                        "TradeDate": tradeDate,
                        "IsLastPriceChanged": 4 in dataEvent.getData()[0]["FieldData"],  # 最新价是否改变
                    }
                })
            else:
                event = Event({
                    "EventCode": ST_TRIGGER_KLINE,
                    "ContractNo": record[0],
                    "KLineType": record[1],
                    "KLineSlice": record[2],
                    "Data": {
                        "Data": dataEvent.getData()[0],
                        "DateTimeStamp": dataEvent.getData()[0]["DateTimeStamp"],
                        "TradeDate": dataEvent.getData()[0]["TradeDate"],
                    }
                })
            self.sendTriggerQueue(event)

    # 报告事件, 发到engine进程中，engine进程 再发到ui进程。
    def _onReport(self, event):
        data = self._dataModel.getCalcCenter().testResult()
        responseEvent = Event({
            "EventCode":EV_EG2UI_REPORT_RESPONSE,
            "StrategyId":self._strategyId,
            "Data":{
                "Result":data,
            }
        })
        self.sendEvent2UI(responseEvent)

    def getQueues(self):
        return self._eg2stQueue, self._st2egQueue

    def _onLoadStrategyResponse(self, event):
        '''向界面返回策略加载应答'''
        cfg = self._dataModel.getConfigData()
        key = self._dataModel.getConfigModel().getKLineShowInfoSimple()
        revent = Event({
            "EventCode" : EV_EG2UI_LOADSTRATEGY_RESPONSE,
            "StrategyId": self._strategyId,
            "Data":{
                "StrategyId"   : self._strategyId,
                "StrategyName" : self._strategyName,
                "StrategyState": self._runStatus,
                "ContractNo"   : key[0],
                "KLineType"    : key[1],
                "KLinceSlice"  : key[2],
                "IsActualRun"  : self._dataModel.getConfigModel().isActualRun(),
                "InitialFund"  : self._dataModel.getConfigModel().getInitCapital(),
                "Config"       : cfg,
                "Params"       : self._context.params,
            }
        })
        self.sendEvent2UI(revent)

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
        eSessionId = apiEvent.getESessionId()
        for data in dataList:
            self.updateLocalOrder(eSessionId, data)
        if self.isRealTimeStatus():
            self._tradeTriggerOrder(apiEvent)

    def _onTradeLoginQry(self, apiEvent):
        self._dataModel._trdModel.updateLoginInfo(apiEvent)

    def _onTradeLoginNotice(self, apiEvent):
        self._dataModel._trdModel.updateLoginInfo(apiEvent)

    def _onTradeUserQry(self, apiEvent):
        self._dataModel._trdModel.updateUserInfo(apiEvent)
        self._dataModel._trdModel.updateLoginInfo(apiEvent)

    def _onTradeMatchQry(self, apiEvent):
        self._dataModel._trdModel.updateMatchData(apiEvent)

    def _onTradePositionQry(self, apiEvent):
        self._dataModel._trdModel.updatePosData(apiEvent)

    def _onTradeOrderQry(self, apiEvent):
        self._dataModel._trdModel.updateOrderData(apiEvent)

    def _onTradeMatch(self, apiEvent):
        '''
        交易成交信息发生变化时，更新交易模型信息
        :param apiEvent: 引擎返回事件
        :return: None
        '''
        self._dataModel._trdModel.updateMatchData(apiEvent)
        self._tradeTriggerMatch(apiEvent)

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

    def getLocalOrder(self):
        return self._localOrder

    def getESessionIdList(self):
        return self._eSessionIdList

    def updateLocalOrder(self, eSesnId, data):
        # 更新本地订单信息
        if eSesnId in self._localOrder:
            tradeRecode = self._localOrder[eSesnId]
            tradeRecode.updateOrderInfo(eSesnId, data)
        else:
            self._localOrder[eSesnId] = TradeRecord(eSesnId, data)
            self._eSessionIdList.append(eSesnId)

    def updateBarInfoInLocalOrder(self, eSessionId, barInfo):
        if not barInfo:
            return
        if eSessionId not in self._localOrder:
            return
        tradeRecode = self._localOrder[eSessionId]
        tradeRecode._barInfo = barInfo

    def getContNo(self, eSessionId):
        if eSessionId not in self._localOrder:
            return ''
        tradeRecord = self._localOrder[eSessionId]
        return tradeRecord._contNo

    def getOrderNo(self, eSessionId):
        if eSessionId not in self._localOrder:
            return 0
        tradeRecord = self._localOrder[eSessionId]
        return tradeRecord._orderNo

    def getOrderId(self, eSessionId):
        if eSessionId not in self._localOrder:
            return 0
        tradeRecord = self._localOrder[eSessionId]
        return tradeRecord._orderId

    def getStrategyName(self):
        return self._strategyName

    def isRealTimeStatus(self):
        return self._runStatus == ST_STATUS_CONTINUES

    def isHisStatus(self):
        return self._runStatus == ST_STATUS_HISTORY

    def getStatus(self):
        return self._runStatus

    def sendEvent2Engine(self, event):
        if self._isSt2EgQueueEffective:
            while True:
                try:
                    self._st2egQueue.put_nowait(event)
                    break
                except queue.Full:
                    time.sleep(0.1)
                    self.logger.error(f"策略{self._strategyId}向引擎传递事件{event.getEventCode()}时卡住")

    def sendEvent2EngineForce(self, event):
        while True:
            try:
                self._st2egQueue.put_nowait(event)
                break
            except queue.Full:
                time.sleep(0.1)
                self.logger.error(f"策略{self._strategyId}强制向引擎传递事件{event.getEventCode()}时卡住")

    def sendEvent2UI(self, event):
        self._st2uiQueue.put(event)

    def sendTriggerQueue(self, event):
        self._triggerQueue.put(event)

    def _exit(self, errorCode, errorText):
        event = Event({
            "EventCode": EV_EG2UI_CHECK_RESULT,
            "StrategyId": self._strategyId,
            "Data": {
                "ErrorCode": errorCode,
                "ErrorText": errorText,
            }
        })
        self.sendEvent2EngineForce(event)
        self._onStrategyQuit(None, ST_STATUS_EXCEPTION)

    # 停止策略
    def _onStrategyQuit(self, event=None, status=ST_STATUS_QUIT):
        self._isSt2EgQueueEffective = False
        self._strategyState = StrategyStatusExit
        config = None if self._dataModel is None else self._dataModel.getConfigData()
        result = None
        if self._dataModel and self._dataModel.getCalcCenter():
            result = self._dataModel.getCalcCenter().testResult()
        quitEvent = Event({
            "EventCode": EV_EG2UI_STRATEGY_STATUS,
            "StrategyId": self._strategyId,
            "Data":{
                "Status":status,
                "Config":config,
                "Pid":os.getpid(),
                "Path":self._filePath,
                "StrategyName": self._strategyName,
                "Result":result
            }
        })
        self.sendEvent2UI(quitEvent)
        self.sendEvent2EngineForce(quitEvent)
        self.logger.info(f"策略已经将停止完成信号发送到UI和engine,策略{self._strategyId}")
        # 保证该进程is_alive， 使得队列可用
        while True:
            time.sleep(2)

    def _onEquantExit(self, event):
        self._isSt2EgQueueEffective = False
        self._strategyState = StrategyStatusExit
        config = None if self._dataModel is None else self._dataModel.getConfigData()
        responseEvent = Event({
            "EventCode": EV_EG2UI_STRATEGY_STATUS,
            "StrategyId": self._strategyId,
            "Data": {
                "Status": event.getEventCode(),
                "Config": config,
                "Pid": os.getpid(),
                "Path": self._filePath,
                "StrategyName":self._strategyName,
            }
        })
        self.sendEvent2EngineForce(responseEvent)

    def _switchStrategy(self, event):
        self._dataModel.getHisQuoteModel()._switchKLine()

    def _onStrategyRemove(self, event):
        self._isSt2EgQueueEffective = False
        self._strategyState = StrategyStatusExit
        config = None if self._dataModel is None else self._dataModel.getConfigData()
        responseEvent = Event({
            "EventCode": EV_EG2UI_STRATEGY_STATUS,
            "StrategyId": self._strategyId,
            "Data": {
                "Status": ST_STATUS_REMOVE,
                "Config": config,
                "Pid": os.getpid(),
                "Path": self._filePath,
                "StrategyName": self._strategyName,
            }
        })
        self.sendEvent2UI(responseEvent)
        self.sendEvent2EngineForce(responseEvent)
        self.logger.info(f"策略已经将删除完成信号发送到UI和engine,策略{self._strategyId}, {EV_EG2UI_STRATEGY_STATUS}")

        # 保证该进程is_alive， 使得队列可用
        while True:
            time.sleep(2)

    def _snapShotTrigger(self, event):
        # 未选择即时行情触发
        # if not self._dataModel.getConfigModel().hasSnapShotTrigger() or not self.isRealTimeStatus():
        #     return
        #
        # # 该合约不触发
        # if event.getContractNo() not in self._dataModel.getConfigModel().getTriggerContract():
        #     return

        if not self.isRealTimeStatus():
            return

        # 对应字段没有变化不触发
        data = event.getData()
        if len(data)==0 or (not set(data[0]["FieldData"].keys())&set([4, 11, 17, 18, 19, 20])):
            # 4:最新价 11:成交量 17:最优买价 18:买量 19:最优卖价 20:卖量
            return

        # 如果有成交量变化，将等待该合约所有k线到达后再触发。
        # if 11 in data[0]["FieldData"].keys():
        #     self._triggerMgr.updateData(event)
        #     # ************************************
        #     if self._triggerMgr.isAllDataReady(event.getContractNo()):
        #         self._sendSyncTriggerEvent(event.getContractNo())
        #         self._triggerMgr.restAllData(event.getContractNo())
        #     return
            # ************************************

        dateTimeStamp, tradeDate, lv1Data = self.getTriggerTimeAndData(event.getContractNo())
        event = Event({
            "EventCode" : ST_TRIGGER_SANPSHOT_FILL,
            "ContractNo": event.getContractNo(),
            "KLineType" : None,
            "KLineSlice": None,
            "Data":{
                "Data": lv1Data,
                "DateTimeStamp": dateTimeStamp,
                "TradeDate": tradeDate,
                "IsLastPriceChanged": 4 in data[0]["FieldData"],   # 最新价是否改变
            }
        })
        self.sendTriggerQueue(event)

    def setCurTriggerSourceInfo(self, args):
        self._curTriggerSourceInfo = args

    def getCurTriggerSourceInfo(self):
        return self._curTriggerSourceInfo

    #
    def _tradeTriggerOrder(self, apiEvent):
        if not self._dataModel.getConfigModel().hasTradeTrigger() or len(apiEvent.getData()) == 0:
            return

        if apiEvent.getEventCode() == EEQU_SRVEVENT_TRADE_ORDER and str(apiEvent.getStrategyId()) == str(self._strategyId):
            contractNo = apiEvent.getData()[0]["Cont"]
            dateTimeStamp, tradeDate, lv1Data = self.getTriggerTimeAndData(contractNo)

            tradeTriggerEvent = Event({
                "EventCode":ST_TRIGGER_TRADE_ORDER,
                "ContractNo": contractNo,
                "KLineType" : None,
                "KLineSlice": None,
                "Data":{
                    "Data": apiEvent.getData()[0],
                    "DateTimeStamp": dateTimeStamp,
                    "TradeDate": tradeDate,
                }
            })
            # 交易触发
            self.sendTriggerQueue(tradeTriggerEvent)

    def _tradeTriggerMatch(self, apiEvent):
        if not self._dataModel.getConfigModel().hasTradeTrigger() or len(apiEvent.getData()) == 0:
            return

        if apiEvent.getEventCode() == EEQU_SRVEVENT_TRADE_MATCH and str(apiEvent.getStrategyId()) == str(self._strategyId):
            contractNo = apiEvent.getData()[0]["Cont"]
            dateTimeStamp, tradeDate, lv1Data = self.getTriggerTimeAndData(contractNo)

            tradeTriggerEvent = Event({
                "EventCode":ST_TRIGGER_TRADE_MATCH,
                "ContractNo": contractNo,
                "KLineType" : None,
                "KLineSlice": None,
                "Data":{
                    "Data": apiEvent.getData()[0],
                    "DateTimeStamp": dateTimeStamp,
                    "TradeDate": tradeDate,
                }
            })

            # 交易触发
            self.sendTriggerQueue(tradeTriggerEvent)

    def getTriggerTimeAndData(self, contractNo):
        lv1DataAndUpdateTime = self._dataModel.getQuoteModel().getLv1DataAndUpdateTime(contractNo)
        if lv1DataAndUpdateTime is not None:
            dateTimeStamp = lv1DataAndUpdateTime["UpdateTime"]
            tradeDate = dateTimeStamp // 1000000000
            lv1Data = lv1DataAndUpdateTime["Lv1Data"]
        else:
            dateTimeStamp = None
            tradeDate = None
            lv1Data = None

        return dateTimeStamp, tradeDate, lv1Data

    def _sendConfig2Engine(self):
        event = Event({
            "EventCode": ST_ST2EG_SYNC_CONFIG,
            "StrategyId": self._strategyId,
            "ContractNo": None,
            "KLineType": None,
            "KLineSlice": None,
            "Data": {
                "UIConfig": self._uiConfig,
                "Config": self._dataModel.getConfigModel().getConfig(),
                "Path": self._filePath,
                "StrategyName": self._strategyName,
                "StrategyId": self._strategyId,
            }
        })
        self.sendEvent2Engine(event)

    def _onSyncEngineInfo(self, event):
        orderId = event.getData()["MaxOrderId"]
        self._eSessionId = orderId

    def getTriggerMgr(self):
        return self._triggerMgr
