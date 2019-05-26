from capi.event import *

# #####################################交易数据模型#########################################
class TLogoinModel:
    '''登录账号信息'''
    def __init__(self, logger, loginNo, data):
        self.logger = logger
        self._loginNo = loginNo
        
        # print("TLogoinModel", data)
        self._metaData = {
            'LoginNo'   : data['LoginNo']    ,  #登录账号
            'Sign'      : data['Sign']       ,  #标识
            'LoginName' : data['LoginName']  ,  #登录名称
            'LoginApi'  : data['LoginApi']   ,  #api类型
            'TradeDate' : data['TradeDate']  ,  #交易日期
            'IsReady'   : data['IsReady']       #是否准备就绪
        }
        self._userInfo = {}
        
        self.logger.info("[LOGIN]%s,%s,%s,%s,%s,%s"%(
            data['LoginNo'], data['Sign'], data['LoginName'],
            data['LoginApi'], data['TradeDate'], data['IsReady']
        ))
        
    def updateUserInfo(self, userNo, userInfo):
        self._userInfo[userNo] = userInfo

    def copyLoginInfoMetaData(self):
        return deepcopy(self._metaData) if len(self._metaData) > 0 else {}

class TUserInfoModel:
    '''资金账号信息'''
    def __init__(self, logger, login, data):
        self.logger = logger
        self._loginInfo = login
        self._userNo = data['UserNo']
        
        #print("TUserInfoModel", data)
        
        self._metaData = {
                'UserNo'    : data['UserNo'],
                'Sign'      : data['Sign'],
                'LoginNo'   : data['LoginNo'],
                'UserName'  : data['UserName'],
        }
        
        self._money   = {} #{'currencyNo' : TMoneyModel}
        self._order   = {} #{'OrderNo'    : TOrderModel}
        self._match   = {} #{'OrderNo'    : TMatchModel}
        self._position = {} #{'PositionNo' : TPostionModel}
        
        self.logger.info("[USER]%s,%s,%s,%s"%(
            data['UserNo'], data['Sign'], data['LoginNo'], data['UserName']
        ))

    def getMetaData(self):
        return self._metaData
        
    def getSign(self):
        return self._metaData['Sign']

    def updateMoney(self, data):
        currencyNo = data['CurrencyNo']
        if currencyNo not in self._money:
            self._money[currencyNo] = TMoneyModel(self.logger, data)
        else:
            self._money[currencyNo].updateMoney(data)

    def updateOrder(self, data):
        orderNo = data['OrderNo']
        if orderNo not in self._order:
            self._order[orderNo] = TOrderModel(self.logger, data)
        else:
            order = self._order[orderNo]
            order.updateOrder(data)

    def updateMatch(self, data):
        orderNo = data['OrderNo']
        if orderNo not in self._match:
            self._match[orderNo] = TMatchModel(self.logger, data)
        else:
            match = self._match[orderNo]
            match.updateMatch(data)

    def updatePosition(self, data):
        posNo = data['PositionNo']
        if posNo not in self._position:
            self._position[posNo] = TPositionModel(self.logger, data)
        else:
            pos = self._position[posNo]
            pos.updatePosition(data)

    def updateMoneyFromDict(self, moneyInfoDict):
        if len(moneyInfoDict) == 0:
            self._money = {}
            return

        for currencyNo, moneyDict in moneyInfoDict.items():
            if currencyNo not in self._money:
                self._money[currencyNo] = TMoneyModel(self.logger, moneyDict)
            else:
                self._money[currencyNo].updateMoney(moneyDict)

    def updateOrderFromDict(self, orderInfoDict):
        if len(orderInfoDict) == 0:
            self._order = {}
            return

        for orderNo, orderDict in orderInfoDict.items():
            if orderNo not in self._order:
                self._order[orderNo] = TOrderModel(self.logger, orderDict)
            else:
                self._order[orderNo].updateOrder(orderDict)

    def updateMatchFromDict(self, matchInfoDict):
        if len(matchInfoDict) == 0:
            self._match = {}
            return

        for orderNo, matchDict in matchInfoDict.items():
            if orderNo not in self._match:
                self._match[orderNo] = TMatchModel(self.logger, matchDict)
            else:
                self._match[orderNo].updateMatch(matchDict)

    def updatePositionFromDict(self, positionInfoDict):
        if len(positionInfoDict) == 0:
            self._position = {}
            return

        for positionNo, positionDict in positionInfoDict.items():
            if positionNo not in self._position:
                self._position[positionNo] = TPositionModel(self.logger, positionDict)
            else:
                self._position[positionNo].updatePosition(positionDict)

    def formatUserInfo(self):
        data = {
            'metaData' : {},
            'money'    : {},
            'order'    : {},
            'match'    : {},
            'position' : {},
        }

        if len(self._metaData) > 0:
            data['metaData'] = deepcopy(self._metaData)

        # 资金信息
        if len(self._money) > 0 :
            moneyDict = {}
            for currencyNo, tMoneyModel in self._money.items():
                moneyDict[currencyNo] = deepcopy(tMoneyModel._metaData)
            data['money'] = moneyDict

        # 订单信息
        if len(self._order) > 0:
            orderDict = {}
            for orderNo, tOrderModel in self._order.items():
                orderDict[orderNo] = deepcopy(tOrderModel._metaData)
            data['order'] = orderDict

        # 成交信息
        if len(self._match) > 0:
            matchDict = {}
            for orderNo, tMatchModel in self._match.items():
                matchDict[orderNo] = deepcopy(tMatchModel._metaData)
            data['match'] = matchDict

        # 委托信息
        if len(self._position) > 0:
            positionDict = {}
            for positionNo, tPositionModel in self._position.items():
                positionDict[positionNo] = deepcopy(tPositionModel._metaData)
            data['position'] = positionDict

        return data

class TMoneyModel:
    '''资金信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updateMoney(data)
        
    def updateMoney(self, data):    
        self._metaData['UserNo']           = data['UserNo']        
        self._metaData['Sign']             = data['Sign']          
        self._metaData['CurrencyNo']       = data['CurrencyNo']       #币种号
        self._metaData['ExchangeRate']     = data['ExchangeRate']     #币种汇率
        self._metaData['FrozenFee']        = data['FrozenFee']        #冻结手续费
        self._metaData['FrozenDeposit']    = data['FrozenDeposit']    #冻结保证金
        self._metaData['Fee']              = data['Fee']              #手续费(包含交割手续费)
        self._metaData['Deposit']          = data['Deposit']          #保证金
        self._metaData['FloatProfit']      = data['FloatProfit']      #盯式盈亏，不含LME持仓盈亏
        self._metaData['FloatProfitTBT']   = data['FloatProfitTBT']   #逐笔浮赢
        self._metaData['CoverProfit']      = data['CoverProfit']      #盯市平盈
        self._metaData['CoverProfitTBT']   = data['CoverProfitTBT']   #逐笔平盈
        self._metaData['Balance']          = data['Balance']          #今资金=PreBalance+Adjust+CashIn-CashOut-Fee(TradeFee+DeliveryFee+ExchangeFee)+CoverProfitTBT+Premium
        self._metaData['Equity']           = data['Equity']           #今权益=Balance+FloatProfitTBT(NewFloatProfit+LmeFloatProfit)+UnExpiredProfit
        self._metaData['Available']        = data['Available']        #今可用=Equity-Deposit-Frozen(FrozenDeposit+FrozenFee)
        self._metaData['UpdateTime']       = data['UpdateTime']       #资金更新时间戳
        
        '''self.logger.info("[MONEY]%s,%f,%f,%f,%f,%f,%f,%f,%f,%f,%s"%(
            data['CurrencyNo'], data['Fee'],data['Deposit'], data['FloatProfit'],
            data['FloatProfitTBT'],data['CoverProfit'],data['CoverProfitTBT'],
            data['Balance'], data['Equity'],data['Available'],data['UpdateTime']
        ))'''
        
class TOrderModel:
    '''委托信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updateOrder(data)
        
    def updateOrder(self, data):
        self._metaData['UserNo']            =  data['UserNo']          #             
        self._metaData['Sign']              =  data['Sign']           
        self._metaData['Cont']              =  data['Cont']              # 行情合约
        self._metaData['OrderType']         =  data['OrderType']         # 定单类型
        self._metaData['ValidType']         =  data['ValidType']         # 有效类型
        self._metaData['ValidTime']         =  data['ValidTime']         # 有效日期时间(GTD情况下使用)
        self._metaData['Direct']            =  data['Direct']            # 买卖方向
        self._metaData['Offset']            =  data['Offset']            # 开仓平仓 或 应价买入开平
        self._metaData['Hedge']             =  data['Hedge']             # 投机保值
        self._metaData['OrderPrice']        =  data['OrderPrice']        # 委托价格 或 期权应价买入价格
        self._metaData['TriggerPrice']      =  data['TriggerPrice']      # 触发价格
        self._metaData['TriggerMode']       =  data['TriggerMode']       # 触发模式
        self._metaData['TriggerCondition']  =  data['TriggerCondition']  # 触发条件
        self._metaData['OrderQty']          =  data['OrderQty']          # 委托数量 或 期权应价数量
        self._metaData['StrategyType']      =  data['StrategyType']      # 策略类型
        self._metaData['Remark']            =  data['Remark']            #下单备注字段，只有下单时生效。
        self._metaData['AddOneIsValid']     =  data['AddOneIsValid']     # T+1时段有效(仅港交所)
        self._metaData['OrderState']        =  data['OrderState']        # 委托状态
        self._metaData['OrderId']           =  data['OrderId']           # 定单号
        self._metaData['OrderNo']           =  data['OrderNo']           # 委托号
        self._metaData['MatchPrice']        =  data['MatchPrice']        # 成交价
        self._metaData['MatchQty']          =  data['MatchQty']          # 成交量
        self._metaData['ErrorCode']         =  data['ErrorCode']         # 最新信息码
        self._metaData['ErrorText']         =  data['ErrorText']         # 最新错误信息
        self._metaData['InsertTime']        =  data['InsertTime']        # 下单时间
        self._metaData['UpdateTime']        =  data['UpdateTime']        # 更新时间
        
        #self.logger.info("ORDER:%s,%f,%d"%(self._metaData['OrderNo'], self._metaData['OrderPrice'], self._metaData['OrderQty']))
        #print('updateOrder', self._metaData['OrderNo'], self._metaData['OrderPrice'], self._metaData['OrderQty'])
        
class TMatchModel:
    '''成交信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updateMatch(data)
        
    def updateMatch(self, data):
        self._metaData['UserNo']            =  data['UserNo']          #             
        self._metaData['Sign']              =  data['Sign']           
        self._metaData['Cont']              =  data['Cont']              # 行情合约
        self._metaData['Direct']            =  data['Direct']            # 买卖方向
        self._metaData['Offset']            =  data['Offset']            # 开仓平仓 或 应价买入开平
        self._metaData['Hedge']             =  data['Hedge']             # 投机保值
        self._metaData['OrderNo']           =  data['OrderNo']           # 委托号
        self._metaData['MatchPrice']        =  data['MatchPrice']        # 成交价
        self._metaData['MatchQty']          =  data['MatchQty']          # 成交量
        self._metaData['FeeCurrency']       =  data['FeeCurrency']       # 手续费币种
        self._metaData['MatchFee']          =  data['MatchFee']          # 手续费
        self._metaData['MatchDateTime']     =  data['MatchDateTime']     # 成交时间
        self._metaData['AddOne']            =  data['AddOne']            # T+1成交
        self._metaData['Deleted']           =  data['Deleted']           # 是否删除
        
class TPositionModel:
    '''持仓信息'''
    def __init__(self, logger, data):
        self.logger = logger
        self._metaData = {}
        self.updatePosition(data)
        
    def updatePosition(self, data):
        self._metaData['PositionNo']        =  data['PositionNo']
        self._metaData['UserNo']            =  data['UserNo']            #             
        self._metaData['Sign']              =  data['Sign']           
        self._metaData['Cont']              =  data['Cont']              # 行情合约
        self._metaData['Direct']            =  data['Direct']            # 买卖方向
        self._metaData['Hedge']             =  data['Hedge']             # 投机保值
        self._metaData['Deposit']           =  data['Deposit']           # 初始保证金
        self._metaData['PositionQty']       =  data['PositionQty']        # 总持仓
        self._metaData['PrePositionQty']    =  data['PrePositionQty']          # 昨持仓数量
        self._metaData['PositionPrice']     =  data['PositionPrice']       # 价格
        self._metaData['ProfitCalcPrice']   =  data['ProfitCalcPrice']          # 浮盈计算价
        self._metaData['FloatProfit']       =  data['FloatProfit']     # 浮盈
        self._metaData['FloatProfitTBT']    =  data['FloatProfitTBT']            # 逐笔浮盈
        
class TradeModel:
    
    def __init__(self, logger):
        self.logger = logger
        
        self._loginInfo = {} #登录账号{'LoginNo': {:}}
        self._userInfo = {}  #资金账号{'UserNo' : {:}}
        
        #先简单写，不使用状态机
        self._dataStatus = TM_STATUS_NONE
        
    ###################################################################
    def getStatus(self):
        return self._dataStatus

    def getUserInfo(self):
        return self._userInfo
        
    def getUserModel(self, userNo):
        if userNo not in self._userInfo:
            return None
        
        return self._userInfo[userNo]

    def isUserFill(self):
        return self._dataStatus >= TM_STATUS_USER
        
    def isOrderFill(self):
        return self._dataStatus >= TM_STATUS_ORDER    
        
    def setStatus(self, status):
        self._dataStatus = status
    
    def getMoneyEvent(self):
        #查询所有账号下的资金信息
        eventList = []
        for v in self._userInfo.values():
            #外盘只查基币，内盘全查
            loginApi = v._loginInfo._metaData['LoginApi']
            currencyNo = ''
            if loginApi == 'DipperTradeApi':
                currencyNo = 'Base'
                
            event = Event({
                'StrategyId' : 0,
                'Data' : 
                    {
                        'UserNo'     : v._metaData['UserNo'],
                        'Sign'       : v._metaData['Sign'],
                        'CurrencyNo' : currencyNo
                    }
            })
            eventList.append(event)
            
        return eventList
        
    def getOrderEvent(self):
        #查询所有账号下的委托信息
        eventList = []
        for v in self._userInfo.values():
            event = Event({
                'StrategyId' : 0,
                'Data' : 
                    {
                        'UserNo'     : v._metaData['UserNo'],
                        'Sign'       : v._metaData['Sign'],
                    }
            })
            eventList.append(event)
            
        return eventList
        
    def getMatchEvent(self):
        return self.getOrderEvent()
        
    def getPositionEvent(self):
        return self.getOrderEvent()

    def getTradeInfoEvent(self, stragetyId):
        pass


    ###################################################################
    def TLogoinModel(self, apiEvent):
        dataList = apiEvent.getData()

        for data in dataList:
            self._loginInfo[data['LoginNo']] = TLogoinModel(self.logger, data['LoginNo'], data)

    # 更新登录信息
    def updateLoginInfo(self, apiEvent):
        dataList = apiEvent.getData()
        for data in dataList:
            loginNo = data['LoginNo']
            if loginNo not in self._loginInfo:
                self._loginInfo[loginNo] = TLogoinModel(self.logger, loginNo, data)

    def updateLoginInfoFromDict(self, loginInfoDict):
        if len(loginInfoDict) == 0:
            return

        for loginNo, loginInfo in loginInfoDict.items():
            self._loginInfo[loginNo] = TLogoinModel(self.logger, loginNo, loginInfo)

    def updateUserInfoFromDict(self, userInfoDict):
        if len(userInfoDict) == 0:
            return

        for userNo, userInfo in userInfoDict.items():
            # 资金账号信息
            metaData = userInfo['metaData']
            tUserInfoModel = TUserInfoModel(self.logger, self._loginInfo, metaData)

            # 更新资金信息
            moneyInfoDict = userInfo['money']
            tUserInfoModel.updateMoneyFromDict(moneyInfoDict)

            # 更新订单信息
            orderInfoDict = userInfo['order']
            tUserInfoModel.updateOrderFromDict(orderInfoDict)

            # 更新成交信息
            matchInfoDict = userInfo['match']
            tUserInfoModel.updateMatchFromDict(matchInfoDict)

            # 更新持仓信息
            positionInfoDict = userInfo['position']
            tUserInfoModel.updatePositionFromDict(positionInfoDict)

            self._userInfo[userNo] = tUserInfoModel

    def updateUserInfo(self, apiEvent):
        dataList = apiEvent.getData()
        for data in dataList:
            loginNo = data['LoginNo']
            if loginNo not in self._loginInfo:
                self.logger.error("The login account(%s) doesn't login!"%loginNo)
                continue
                
            loginInfo = self._loginInfo[loginNo]
            userNo = data['UserNo']
            userInfo = TUserInfoModel(self.logger, loginInfo, data)

            self._loginInfo[loginNo].updateUserInfo(userNo, userInfo)
            self._userInfo[userNo] = userInfo
        
        # print(apiEvent.getData())

    def updateMoney(self, apiEvent):
        dataList = apiEvent.getData()

        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updateMoney]The user account(%s) doesn't login!"%userNo)
                continue
            self._userInfo[userNo].updateMoney(data)
            
        #print(apiEvent.getData())
        
    def updateOrderData(self, apiEvent):
        dataList = apiEvent.getData()

        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updateOrderData]The user account(%s) doesn't login!"%userNo)
                continue
                
            #self.logger.debug('[ORDER]%s'%data)
        
            self._userInfo[userNo].updateOrder(data)
            
    def updateMatchData(self, apiEvent):
        dataList = apiEvent.getData()
        
        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updateMatchData]The user account(%s) doesn't login!"%userNo)
                continue
            
            #self.logger.debug('[MATCH]%s'%data)
        
            self._userInfo[userNo].updateMatch(data)
            
    def updatePosData(self, apiEvent):
        dataList = apiEvent.getData()
        
        for data in dataList:
            userNo = data['UserNo']
            if userNo not in self._userInfo:
                self.logger.error("[updatePosData]The user account(%s) doesn't login!"%userNo)
                continue
                
            #self.logger.debug('[POS]%s'%data)
        
            self._userInfo[userNo].updatePosition(data)