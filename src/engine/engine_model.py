from capi.event import *
from copy import deepcopy
from .trade_model import TradeModel

class DataModel(object):
    def __init__(self, logger):
        self.logger = logger
        self._quoteModel = QuoteModel(logger)
        self._hisQuoteModel = HisQuoteModel(logger)
        self._tradeModel = TradeModel(logger)

    def getTradeModel(self):
        return self._tradeModel

    def getHisQuoteModel(self):
        return self._hisQuoteModel

    def getQuoteModel(self):
        return self._quoteModel
        
# 即时行情
class QuoteModel:
    def __init__(self, logger):
        self.logger = logger
        # 全量交易所、品种、合约
        self._exchangeData  = {}  #{key=ExchangeNo,value=ExchangeModel}
        self._commodityData = {}  #{key=CommodityNo, value=CommodityModel}
        self._contractData  = {}  #{key=ContractNo, value=QuoteDataModel}

        self._baseDataReady = False
        
    def getQuoteEvent(self, contractNo, strategyId):
        if contractNo not in self._contractData:
            return None
        contQuote = self._contractData[contractNo] 
        return contQuote.getEvent(strategyId)

    def getExchange(self):
        dataDict = {}
        for k, v in self._exchangeData.items():
            dataDict[k] = v.getExchange()
        return Event({'EventCode':EV_EG2ST_EXCHANGE_RSP, 'Data':dataDict})

    def getCommodity(self):
        dataDict = {}
        for k,v in self._commodityData.items():
            dataDict[k] = v.getCommodity()
        #TODO：先不拷贝
        return Event({'EventCode':EV_EG2ST_COMMODITY_RSP, 'Data':dataDict})

    # 交易所
    def updateExchange(self, apiEvent):
        dataList = apiEvent.getData()
        for dataDict in dataList:
            self._exchangeData[dataDict['ExchangeNo']] = ExchangeModel(self.logger, dataDict)
        if apiEvent.isChainEnd():
            self.logger.info('Initialize exchange data(%d) successfully!'%len(self._exchangeData))

    # 品种
    def updateCommodity(self, apiEvent):
        dataList = apiEvent.getData()
        for dataDict in dataList:
            self._commodityData[dataDict['CommodityNo']] = CommodityModel(self.logger, dataDict)    
        if apiEvent.isChainEnd():
            self.logger.info('Initialize commodity data(%d) successfully!' % len(self._commodityData))

    # 时间模板
    def updateTimeBucket(self, apiEvent):
        dataList = apiEvent.getData()

        if len(dataList) == 0:
            return 0

        dataDict = dataList[0]
        commodity = dataDict['Commodity']
        if commodity in self._commodityData:
            self._commodityData[commodity].updateTimeBucket(dataList)

        if apiEvent.isChainEnd():
            pass

    # 合约
    def updateContract(self, apiEvent):
        dataList = apiEvent.getData()
        for dataDict in dataList:
            self._contractData[dataDict['ContractNo']] = QuoteDataModel(self.logger, dataDict)
            
        if apiEvent.isChainEnd():
            self.logger.info('Initialize contract data(%d) successfully!'%len(self._contractData))
            self._baseDataReady = True

    def updateLv1(self, apiEvent):
        '''更新普通行情'''
        self._updateQuote(apiEvent, 'N')
       
    def updateLv2(self, apiEvent):
        '''更新深度行情'''
        self._updateQuote(apiEvent, 'D') 
        
    def _updateQuote(self, apiEvent, lv):
        contractNo = apiEvent.getContractNo()
        if contractNo not in self._contractData:
            #策略模块也使用该函数
            dataDict = {
                'ExchangeNo'  : '',
                'CommodityNo' : '',
                'ContractNo'  : contractNo,
            }
            self._contractData[contractNo] = QuoteDataModel(self.logger, dataDict)
            
        dataList = apiEvent.getData()
        data = self._contractData[contractNo]
        
        for oneDict in dataList:
            if lv == 'N':
                data.updateLv1(oneDict)
            else:
                data.updateLv2(oneDict)
        
class ExchangeModel:
    '''
    _metaData = {
        'ExchangeNo'   : 'ZCE',             #交易所编号
        'ExchangeName' : '郑州商品交易所'   #简体中文名称
    }
    '''
    def __init__(self, logger, dataDict):
        '''
        dataDict ={
            'ExchangeNo'  : value,
            'ExchangeName': value,
        } 
        '''
        self.logger = logger
        self._exchangeNo = dataDict['ExchangeNo']
        self._metaData = {
            'ExchangeNo'   : dataDict['ExchangeNo'],
            'ExchangeName' : dataDict['ExchangeName']
        }

    def getExchange(self):
        return self._metaData
        
class CommodityModel:
    '''
    _metaData = {
        'ExchangeNo'   : 'ZCE'             # value,str 交易所编号
        'CommodityNo'  : 'ZCE|F|SR'        # value,str 品种编号
        'CommodityType': 'F'               # value,str 品种类型
        'CommodityName': '白糖'            # value,str 品种名称
        'PriceNume'    : 1                 # value,float 报价分子
        'PriceDeno'    : 1                 # value,float 报价分母
        'PriceTick'    : 1                 # value,float 最小变动价
        'PricePrec'    : 1                 # value,float 价格精度
        'TradeDot'     : 10                # value,float 每手乘数
        'CoverMode'    : 'C'               # value,str 平仓方式，区分开平
        'TimeBucket'   : []                # 时间模板信息
    }
    '''
    def __init__(self, logger, dataDict):
        self.logger = logger
        self.commdityNo = dataDict['CommodityNo']
        timeBucket = dataDict['TimeBucket'] if 'TimeBucket' in dataDict else []

        self._metaData = {
            'ExchangeNo'    : dataDict['ExchangeNo'],
            'CommodityNo'   : dataDict['CommodityNo'],
            'CommodityType' : dataDict['CommodityType'],
            'CommodityName' : dataDict['CommodityName'],
            'PriceNume'     : dataDict['PriceNume'],
            'PriceDeno'     : dataDict['PriceDeno'],
            'PriceTick'     : dataDict['PriceTick'],
            'PricePrec'     : dataDict['PricePrec'],
            'TradeDot'      : dataDict['TradeDot'],
            'CoverMode'     : dataDict['CoverMode'],
            'TimeBucket'    : timeBucket,
        }
        
    def getCommodity(self):
        return self._metaData

    def updateTimeBucket(self, dataList):
        self._metaData['TimeBucket'] = dataList

class QuoteDataModel:
    '''
    _metaData = {
        'UpdateTime' : 20190401090130888, # 时间戳
        'Lv1Data'    : {                  # 普通行情
            '0'      : 5074,              # 昨收盘
            '1'      : 5052,              # 昨结算
            '2'      : 269272,            # 昨持仓
            '3'      : 5067,              # 开盘价
            '4'      : 5084,              # 最新价
            ...
            '126'    : 1                  # 套利行情系数
            },
        'Lv2BidData' :[
            5083,                         # 买1
            5082,                         # 买2
            5082,                         # 买3
            5080,                         # 买4
            5079,                         # 买5
        ],
        'Lv2AskData':[
            5084,                         # 卖1
            5085,                         # 卖2
            5086,                         # 卖3
            5087,                         # 卖4
            5088,                         # 卖5
        ]
    }
    '''
        
    def __init__(self, logger, dataDict):
        '''
        dataDict ={
            'ExchangeNo' : value,
            'CommodityNo': value,
            'ContractNo' : value,
        } 
        '''
        
        self.logger = logger
        self._contractNo = dataDict['ContractNo']
        self._metaData = {
            'ExchangeNo' : dataDict['ExchangeNo'],    # 交易所编号
            'CommodityNo': dataDict['CommodityNo'],   # 品种编号
            'UpdateTime' : 0,                         # 行情时间戳
            'Lv1Data'    : {},                        # 普通行情
            'Lv2BidData' : [0 for i in range(10)],    # 买深度
            'Lv2AskData' : [0 for i in range(10)]     # 卖深度
        }
        
    def getEvent(self, strategyId):
        data = deepcopy(self._metaData)
        msg = {
            'EventSrc'   : EEQU_EVSRC_ENGINE     ,  
            'EventCode'  : EV_EG2ST_SUBQUOTE_RSP ,
            'StrategyId' : strategyId            ,
            'SessionId'  : 0                     ,
            'ContractNo' : self._contractNo      ,
            'Data'       : data                  ,
        }

        return Event(msg)
        
    def updateLv1(self, oneDict):
        '''
        功能：更新普通行情
        参数: oneDict = {
            UpdateTime : value,
            FieldData  : {
                'FidMean1' : 'FidValue1',
                'FidMean2' : 'FidValue2'
                ...
            }
        }
        '''
        self._metaData['UpdateTime'] = oneDict['UpdateTime']
        fieldDict = oneDict['FieldData']
        
        for k, v in fieldDict.items():
            self._metaData['Lv1Data'][k] = v
        
    def updateLv2(self, oneDict):
        '''
        功能：更新深度行情
        参数：oneDict = {
            'Bid' : [
                {'Price' : Price1,  'Qty' : Qty1},
                {'Price' : Price2,  'Qty' : Qty2},
                ...
                {'Price' : Price10, 'Qty' : Qty10}
            ], 
            
            'Ask' : [
                {'Price' : Price1,  'Qty' : Qty1},
                {'Price' : Price2,  'Qty' : Qty2},
                ...
                {'Price' : Price10, 'Qty' : Qty10}
            ],
        }
        '''
        # 9.5传递全量深度，直接拷贝
        self._metaData['Lv2BidData'] = oneDict['Bid'][:]
        self._metaData['Lv2AskData'] = oneDict['Ask'][:]

    def getLv1Data(self, key, errRet):
        if key not in self._metaData['Lv1Data']:
            return errRet
        return self._metaData['Lv1Data'][key]

# 历史行情
class HisQuoteModel:
    '''K线Model中不缓存，直接分发'''
    def __init__(self, logger):
        self.logger = logger
        
    def updateKline(self, apiEvent):
        strategyId = apiEvent.getStrategyId()
        sessionId = apiEvent.getSessionId()
        contractNo = apiEvent.getContractNo()
        klineType = apiEvent.getKLineType()
        data = apiEvent.getData()
        chain = apiEvent.getChain()
        #print("%d,%d,%s,%s,%s,%s"%(strategyId,sessionId, contractNo,klineType,chain, data))