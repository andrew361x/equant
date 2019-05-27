

#BaseApi类定义
class BaseApi(object):
    # 单例模式
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls)
            #print("create singleton instance of BaseAPI ", cls._instance)
        else:
            #print("BaseAPI instance has existed")
            pass
        return cls._instance

    def __init__(self, strategy = None, dataModel = None):
        self.updateData(strategy, dataModel)

    def updateData(self, strategy, dataModel):
        # 关联的策略
        self._strategy = strategy
        # 子进程数据模型
        self._dataModel = dataModel

    #/////////////////////////K线数据/////////////////////////////
    def Date(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              当前Bar的日期

        【语法】
              string Date(string contractNo, char kLineType, int kLineValue)

        【参数】
			  contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              简写D,返回格式为YYYYMMDD的字符串

        【实例】
              当前Bar对应的日期为2019-03-25，则Date返回值为"20190325"
        '''
        return self._dataModel.getBarDate(contractNo, kLineType, kLineValue)

    def Time(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              当前Bar的时间

        【语法】
              string Time(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              简写T, 返回格式为HHMMSSmmm的字符串

        【实例】
              当前Bar对应的时间为11:34:21.356，Time返回值为"113421356"
              当前Bar对应的时间为09:34:00.000，Time返回值为"093400000"
              当前Bar对应的时间为11:34:00.000，Time返回值为"113400000"
        '''
        return self._dataModel.getBarTime(contractNo, kLineType, kLineValue)

    def Open(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约指定周期的开盘价

        【语法】
              array Open(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              简写O, 返回值numpy数组包含截止当前Bar的所有开盘价
              Open()[-1] 表示当前Bar开盘价，Open()[-2]表示上一个Bar开盘价，以此类推

        【实例】
              Open('ZCE|F|SR|905', 'M', 1) 获取白糖905合约1分钟K线的所有开盘价列表
        '''
        return self._dataModel.getBarOpen(contractNo, kLineType, kLineValue)

    def High(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约指定周期的最高价

        【语法】
              array High(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              简写H, Tick时为当时的委托卖价
              返回numpy数组，包括截止当前Bar的所有最高价
              High('ZCE|F|SR|905', 'M', 1)[-1] 表示当前Bar最高价，High('ZCE|F|SR|905', 'M', 1)[-2]表示上一个Bar最高价，以此类推

        【实例】
              High('ZCE|F|SR|905', 'M', 1) 获取白糖905合约1分钟K线的所有最高价列表
        '''
        return self._dataModel.getBarHigh(contractNo, kLineType, kLineValue)

    def Low(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约指定周期的最低价

        【语法】
              array Low(string contractNo, char klineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              简写H, Tick时为当时的委托卖价
              返回numpy数组，包括截止当前Bar的所有最低价
              Low()[-1] 表示当前Bar最低价，Low()[-2]表示上一个Bar最低价，以此类推

        【实例】
              Low('ZCE|F|SR|905', 'M', 1) 获取白糖905合约1分钟K线的所有最低价列表
        '''
        return self._dataModel.getBarLow(contractNo, kLineType, kLineValue)

    def Close(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约指定周期的收盘价

        【语法】
              array Close(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              简写C, 返回numpy数组，包括截止当前Bar的所有收盘价
              Close()[-1] 表示当前Bar收盘价，Close()[-2]表示上一个Bar收盘价，以此类推

        【实例】
              Close('ZCE|F|SR|905', 'M', 1) 获取白糖905合约1分钟K线的所有收盘价列表
        '''
        return self._dataModel.getBarClose(contractNo, kLineType, kLineValue)

    def Vol(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约指定周期的成交量

        【语法】
              array Vol(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              简写V, 返回numpy数组，包括截止当前Bar的所有成交量
              Vol()[-1] 表示当前Bar成交量，Vol()[-2]表示上一个Bar成交量，以此类推

        【实例】
              Vol('ZCE|F|SR|905', 'M', 1) 获取白糖905合约1分钟K线的所有成交量列表
        '''
        return self._dataModel.getBarVol(contractNo, kLineType, kLineValue)

    def OpenInt(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约指定周期的持仓量

        【语法】
              numpy.array OpenInt(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              返回numpy数组，包括截止当前Bar的所有持仓量
              OpenInt()[-1] 表示当前Bar持仓量，OpenInt()[-2]表示上一个Bar持仓量，以此类推

        【实例】
              OpenInt('ZCE|F|SR|905', 'M', 1) 获取白糖905合约所有1分钟K线上的持仓量列表
        '''
        return self._dataModel.getBarOpenInt(contractNo, kLineType, kLineValue)

    def TradeDate(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约当前Bar的交易日

        【语法】
              string TradeDate(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              返回格式为YYYYMMDD的字符串

        【实例】
              当前Bar对用的日期为2019-03-25，则Date返回值为"20190325"
        '''
        return self._dataModel.getBarTradeDate(contractNo, kLineType, kLineValue)

    def BarCount(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约Bar的总数

        【语法】
              int BarCount(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              返回值为整型

        【实例】
              无
        '''
        return self._dataModel.getBarCount(contractNo, kLineType, kLineValue)

    def CurrentBar(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约当前Bar的索引值

        【语法】
              int CurrentBar(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              第一个Bar返回值为0，其他Bar递增

        【实例】
              无
        '''
        return self._dataModel.getCurrentBar(contractNo, kLineType, kLineValue)

    def BarStatus(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约当前Bar的状态值

        【语法】
              int BarStatus(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              返回值整型, 0表示第一个Bar,1表示中间普通Bar,2表示最后一个Bar

        【实例】
              无
        '''
        return self._dataModel.getBarStatus(contractNo, kLineType, kLineValue)

    def HistoryDataExist(self, contractNo, kLineType, kLineValue):
        '''
        【说明】
              指定合约的历史数据是否有效

        【语法】
              bool HistoryDataExist(string contractNo, char kLineType, int kLineValue)

        【参数】
              contractNo 合约编号
              kLineType K线类型，可选值请参阅周期类型枚举函数
              kLineValue K线周期
              contractNo、kLineType和kLineValue均可为空，为空时取界面设置或者SetbarInterval函数设置的第一个合约编号和K线类型周期

        【备注】
              返回Bool值，有效返回True，否则返回False

        【实例】
              无
        '''
        return self._dataModel.isHistoryDataExist(contractNo, kLineType, kLineValue)

    def HisData(self, dataType, periodType, interval, contractNo, maxLength):
        '''
        【说明】
              获取各种历史数据数组

        【语法】
               numpy.array HisData(enum dataType, enum periodType, int interval, string contractNo, int maxLength)

        【参数】
              dataType 指定历史数据的种类，可选的枚举函数和相应含义为：
                Enum_Data_Close         : 收盘价
                Enum_Data_Open          : 开盘价
                Enum_Data_High          : 最高价
                Enum_Data_Low           : 最低价
                Enum_Data_Median        : 中间价
                Enum_Data_Typical       : 标准价
                Enum_Data_Weighted      : 加权收盘价
                Enum_Data_Vol           : 成交量
                Enum_Data_Opi           : 持仓量
                Enum_Data_Time          : K线时间
				
              periodType 指定周期类型，可选的枚举函数和相应含义为：
                Enum_Period_Tick        : 周期类型_分笔
                Enum_Period_Dyna        : 周期类型_分时
                Enum_Period_Second      : 周期类型_秒线
                Enum_Period_Min         : 周期类型_分钟
                Enum_Period_Hour        : 周期类型_小时
                Enum_Period_Day         : 周期类型_日线
                Enum_Period_Week        : 周期类型_周线
                Enum_Period_Month       : 周期类型_月线
                Enum_Period_Year        : 周期类型_年线
				
              interval 周期数， 如：5分钟线，周期数就是5；50秒线，周期数为50
              contractNo 合约编号, 为空时取界面设置或者SetbarInterval函数设置的第一个合约编号
              maxLength 定返回历史数据数组的最大长度，默认值为100

        【备注】
              返回numpy数组，包括截止当前Bar的最多maxLength个指定的种类的历史数据

        【实例】
              closeList = HisData(Enum_Data_Close(), Enum_Period_Min(), 5, "ZCE|F|SR|906", 1000) # 获取合约ZCE|F|SR|906包含当前Bar在内的之前1000个5分钟线的收盘价
              closeList[-1] # 当前Bar的收盘价
              closeList[-2] # 上一个Bar的收盘价
        '''
        return self._dataModel.getHisData(dataType, periodType, interval, contractNo, maxLength)

    #/////////////////////////即时行情/////////////////////////////
    def Q_UpdateTime(self, contractNo):
        '''
        【说明】
              获取指定合约即时行情的更新时间

        【语法】
              string Q_UpdateTime(string contractNo)

        【参数】
              contractNo 合约编号, 默认当前合约

        【备注】
              返回格式为"YYYYMMDDHHMMSSmmm"的字符串，
              若指定合约即时行情的更新时间为2019-05-21 10:07:46.000，则该函数放回为20190521100746000

        【实例】
              无
        '''
        return self._dataModel.getQUpdateTime(contractNo)

    def Q_AskPrice(self, contractNo='', level=1):
        '''
        【说明】
              合约最新卖价

        【语法】
              float Q_AskPrice(string contractNo, int level)

        【参数】
              contractNo 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新卖价

        【实例】
              无
        '''
        return self._dataModel.getQAskPrice(contractNo, level)

    def Q_AskPriceFlag(self, contractNo=''):
        '''
        【说明】
              卖盘价格变化标志

        【语法】
              int Q_AskPriceFlag(string contractNo)

        【参数】
              contractNo 合约编号, 默认当前合约

        【备注】
              返回整型，1为上涨，-1为下跌，0为不变

        【实例】
              无
        '''
        return self._dataModel.getQAskPriceFlag(contractNo)

    def Q_AskVol(self, contractNo='', level=1):
        '''
        【说明】
              合约最新卖量

        【语法】
              float Q_AskVol(string contractNo, int level)

        【参数】
              contractNo 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新卖量

        【实例】
              无
        '''
        return self._dataModel.getQAskVol(contractNo, level)

    def Q_AvgPrice(self, contractNo=''):
        '''
        【说明】
              当前合约的历史数据是否有效

        【语法】
              float Q_AvgPrice(string contractNo)

        【参数】
              contractNo 合约编号, 默认当前合约

        【备注】
              返回浮点数，返回实时均价即结算价

        【实例】
              无
        '''
        return self._dataModel.getQAvgPrice(contractNo)

    def Q_BidPrice(self, contractNo='', level=1):
        '''
        【说明】
              合约最新买价

        【语法】
              float Q_BidPrice(string contractNo, int level)

        【参数】
              contractNo 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新买价

        【实例】
              无
        '''
        return self._dataModel.getQBidPrice(contractNo, level)

    def Q_BidPriceFlag(self, contractNo=''):
        '''
        【说明】
              买盘价格变化标志

        【语法】
              int Q_AskPriceFlag(string contractNo)

        【参数】
              contractNo 合约编号,  默认当前合约

        【备注】
              返回整型，1为上涨，-1为下跌，0为不变

        【实例】
              无
        '''
        return self._dataModel.getQBidPriceFlag(contractNo)


    def Q_BidVol(self, contractNo='', level=1):
        '''
        【说明】
              合约最新买量

        【语法】
              float Q_BidVol(string contractNo, int level)

        【参数】
              contractNo 合约编号, 默认当前合约;level 档位数,默认1档

        【备注】
              返回浮点数, 可获取指定合约,指定深度的最新买量

        【实例】
              无
        '''
        return self._dataModel.getQBidVol(contractNo, level)

    def Q_Close(self, contractNo=''):
        '''
        【说明】
              当日收盘价，未收盘则取昨收盘

        【语法】
              float Q_Close(string contractNo)

        【参数】
              contractNo 合约编号,默认当前合约

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQClose(contractNo)

    def Q_High(self, contractNo=''):
        '''
        【说明】
              当日最高价

        【语法】
              float Q_High(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQHigh(contractNo)

    def Q_HisHigh(self, contractNo=''):
        '''
        【说明】
              历史最高价

        【语法】
              float Q_HisHigh(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQHisHigh(contractNo)

    def Q_HisLow(self, contractNo=''):
        '''
        【说明】
              历史最低价

        【语法】
              float Q_HisLow(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQHisLow(contractNo)

    def Q_InsideVol(self, contractNo=''):
        '''
        【说明】
              内盘量

        【语法】
              float Q_InsideVol(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数, 买入价成交为内盘

        【实例】
              无
        '''
        return self._dataModel.getQInsideVol(contractNo)

    def Q_Last(self, contractNo=''):
        '''
        【说明】
              最新价

        【语法】
              float Q_Last(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQLast(contractNo)

    def Q_LastDate(self, contractNo=''):
        '''
        【说明】
              最新成交日期

        【语法】
              int Q_LastDate(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回Date类型

        【实例】
              无
        '''
        return self._dataModel.getQLastDate(contractNo)

    def Q_LastFlag(self, contractNo=''):
        '''
        【说明】
              最新价变化标志

        【语法】
              int Q_LastFlag(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回整型, 1为上涨, -1为下跌, 0为不变

        【实例】
              无
        '''
        return self._dataModel.getQLastFlag(contractNo)

    def Q_LastTime(self, contractNo=''):
        '''
        【说明】
              最新成交时间

        【语法】
              float Q_LastTime(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回Time类型

        【实例】
              无
        '''
        return self._dataModel.getQLastTime(contractNo)

    def Q_LastVol(self, contractNo=''):
        '''
        【说明】
              现手

        【语法】
              float Q_LastVol(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数，单位为手

        【实例】
              无
        '''
        return self._dataModel.getQLastVol(contractNo)

    def Q_Low(self, contractNo=''):
        '''
        【说明】
              当日最低价

        【语法】
              float Q_Low(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQLow(contractNo)

    def Q_LowLimit(self, contractNo=''):
        '''
        【说明】
              当日跌停板价

        【语法】
              float Q_LowLimit(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQLowLimit(contractNo)

    def Q_Open(self, contractNo=''):
        '''
        【说明】
              当日开盘价

        【语法】
              float Q_Open(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQOpen(contractNo)

    def Q_OpenInt(self, contractNo=''):
        '''
        【说明】
              持仓量

        【语法】
              float Q_OpenInt(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数, 单位为手

        【实例】
              无
        '''
        return self._dataModel.getQOpenInt(contractNo)

    def Q_OpenIntFlag(self, contractNo=''):
        '''
        【说明】
              持仓量变化标志

        【语法】
              int  Q_OpenIntFlag(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回整型, 1为增加，-1为下降，0为不变

        【实例】
              无
        '''
        return self._dataModel.getQOpenIntFlag(contractNo)

    def Q_OutsideVol(self, contractNo=''):
        '''
        【说明】
              外盘量

        【语法】
              float Q_OutsideVol(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数，卖出价成交为外盘

        【实例】
              无
        '''
        return self._dataModel.getQOutsideVol(contractNo)

    def Q_PreOpenInt(self, contractNo=''):
        '''
        【说明】
              昨持仓量

        【语法】
              float Q_PreOpenInt(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPreOpenInt(contractNo)

    def Q_PreSettlePrice(self, contractNo=''):
        '''
        【说明】
              昨结算

        【语法】
              float Q_PreSettlePrice(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPreSettlePrice(contractNo)

    def Q_PriceChg(self, contractNo=''):
        '''
        【说明】
              当日涨跌

        【语法】
              float Q_PriceChg(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPriceChg(contractNo)


    def Q_PriceChgRadio(self, contractNo=''):
        '''
        【说明】
              当日涨跌幅

        【语法】
              float Q_PriceChgRadio(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQPriceChgRadio(contractNo)

    def Q_TodayEntryVol(self, contractNo=''):
        '''
        【说明】
              当日开仓量

        【语法】
              float Q_TodayEntryVol(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTodayEntryVol(contractNo)

    def Q_TodayExitVol(self, contractNo=''):
        '''
        【说明】
              当日平仓量

        【语法】
              float Q_TodayExitVol(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTodayExitVol(contractNo)

    def Q_TotalVol(self, contractNo=''):
        '''
        【说明】
              当日成交量

        【语法】
              float Q_TotalVol(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTotalVol(contractNo)

    def Q_TurnOver(self, contractNo=''):
        '''
        【说明】
              当日成交额

        【语法】
              float Q_TurnOver(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQTurnOver(contractNo)

    def Q_UpperLimit(self, contractNo=''):
        '''
        【说明】
              当日涨停板价

        【语法】
              float Q_UpperLimit(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回浮点数

        【实例】
              无
        '''
        return self._dataModel.getQUpperLimit(contractNo)

    def QuoteDataExist(self, contractNo=''):
        '''
        【说明】
              行情数据是否有效

        【语法】
              Bool QuoteDataExist(string contractNo)

        【参数】
              contractNo 合约编号

        【备注】
              返回Bool值，数据有效返回True，否则False

        【示例】
              无
        '''
        return self._dataModel.getQuoteDataExist(contractNo)

    #/////////////////////////策略交易/////////////////////////////
    def Buy(self, contractNo, share=0, price=0):
        '''
        【说明】
              产生一个多头建仓操作

        【语法】
              Bool Buy(int Share=0,float Price=0)

        【参数】
              Share 买入数量，为整型值，默认使用系统设置
              Price 买入价格，为浮点数，默认使用现价(非最后Bar为Close)。

        【备注】
              产生一个多头建仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于多头建仓，其处理规则如下：
              如果当前持仓状态为持平，该函数按照参数进行多头建仓。
              如果当前持仓状态为空仓，该函数平掉所有空仓，同时按照参数进行多头建仓，两个动作同时发出。
              如果当前持仓状态为多仓，该函数将继续建仓，但具体是否能够成功建仓要取决于系统中关于连续建仓的设置，以及资金，最大持仓量等限制。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用buy(1,10)发单，委托价将以50发单。

        【示例】
              在当前没有持仓或者持有多头仓位的情况下：
              Buy(50,10.2) 表示用10.2的价格买入50张合约。
              Buy(10,Close) 表示用当前Bar收盘价买入10张合约，马上发送委托。
              Buy(5,0) 表示用现价买入5张合约，马上发送委托。
              Buy(0,0) 表示用现价按交易设置中设置的手数,马上发送委托。

              在当前持有空头仓位的情况下：
              Buy(10,Close) 表示平掉所有空仓，并用当前Bar收盘价买入10张合约，马上发送委托。
        '''
        return self._dataModel.setBuy(contractNo, share, price)

    def BuyToCover(self, contractNo, share=0, price=0):
        '''
        【说明】
              产生一个空头平仓操作

        【语法】
              Bool BuyToCover(int Share=0,float Price=0)

        【参数】
              Share 买入数量，为整型值，默认为平掉当前所有持仓；
              Price 买入价格，为浮点数，默认=0时为使用现价(非最后Bar为Close)。

        【备注】
              产生一个空头平仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于空头平仓，其处理规则如下：
              如果当前持仓状态为持平，该函数不执行任何操作。
              如果当前持仓状态为多仓，该函数不执行任何操作。
              如果当前持仓状态为空仓，如果此时Share使用默认值，该函数将平掉所有空仓，达到持平的状态，否则只平掉参数Share的空仓。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用BuyToCover(1,10)发单，委托价将以50发单。

        【示例】
              在持有空头仓位的情况下：
              BuyToCover(50,10.2) 表示用10.2的价格空头买入50张合约。
              BuyToCover(10,Close) 表示用当前Bar收盘价空头买入10张合约，马上发送委托。
              BuyToCover(5,0) 表示用现价空头买入5张合约)，马上发送委托。
              BuyToCover(0,0) 表示用现价按交易设置中的设置,马上发送委托。
        '''
        return self._dataModel.setBuyToCover(contractNo, share, price)

    def Sell(self, contractNo, share=0, price=0):
        '''
        【说明】
              产生一个多头平仓操作

        【语法】
              Bool Sell(int Share=0,float Price=0)

        【参数】
              Share 卖出数量，为整型值，默认为平掉当前所有持仓；
              Price 卖出价格，为浮点数，默认=0时为使用现价(非最后Bar为Close)。

        【备注】
              产生一个多头平仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于多头平仓，其处理规则如下：
              如果当前持仓状态为持平，该函数不执行任何操作。
              如果当前持仓状态为空仓，该函数不执行任何操作。
              如果当前持仓状态为多仓，如果此时Share使用默认值，该函数将平掉所有多仓，达到持平的状态，否则只平掉参数Share的多仓。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用sell(1,10)发单，委托价将以50发单。

        【示例】
              在持有多头仓位的情况下：
              Sell(50,10.2) 表示用10.2的价格卖出50张合约。
              Sell(10,Close) 表示用当前Bar收盘价卖出10张合约，马上发送委托。
              Sell(5,0) 表示用现价卖出5张合约，马上发送委托。
              Sell(0,0) 表示用现价按交易设置中的设置,马上发送委托。
        '''
        return self._dataModel.setSell(contractNo, share, price)

    def SellShort(self, contractNo, share=0, price=0):
        '''
        【说明】
              产生一个空头建仓操作

        【语法】
              Bool SellShort(int Share=0,float Price=0)

        【参数】
              Share 卖出数量，为整型值，默认为使用系统设置参数；
              Price 卖出价格，为浮点数，默认=0时为使用现价(非最后Bar为Close)。

        【备注】
              产生一个空头建仓操作，返回值为布尔型，执行成功返回True，否则返回False。
              该函数仅用于空头建仓，其处理规则如下：
              如果当前持仓状态为持平，该函数按照参数进行空头建仓。
              如果当前持仓状态为多仓，该函数平掉所有多仓，同时按照参数进行空头建仓，两个动作同时发出
              如果当前持仓状态为空仓，该函数将继续建仓，但具体是否能够成功建仓要取决于系统中关于连续建仓的设置，以及资金，最大持仓量等限制。
              当委托价格超出k线的有效范围，在历史数据上，将会取最接近的有效价格发单；在实盘中，将会按照实际委托价格发单。
              例如：当前k线有效价格为50-100，用SellShort(1,10)发单，委托价将以50发单。

        【示例】
              在没有持仓或者持有空头持仓的情况下：
              SellShort(50,10.2) 表示用10.2的价格空头卖出50张合约。
              SellShort(10,Close) 表示用当前Bar收盘价空头卖出10张合约，马上发送委托。
              SellShort(5,0) 表示用现价空头卖出5张合约，马上发送委托。
              SellShort(0,0) 表示用现价按交易设置中设置的手数,马上发送委托。
              在MarketPosition=1的情况下：（当前持有多头持仓）
              SellShort(10,Close) 表示平掉所有多头仓位，并用当前Bar收盘价空头卖出10张合约，马上发送委托。

        '''
        return self._dataModel.setSellShort(contractNo, share, price)
        
    #/////////////////////////属性函数/////////////////////////////
    def BarInterval(self, contractNo):
        '''
        【说明】
              合约图表周期数值

        【语法】
              list BarInterval(string contractNo)

        【参数】
              contractNo 合约编号，为空时取的时设置界面设置的周期数值

        【备注】
              返回周期数值列表，通常和BarType一起使用进行数据周期的判别

        【示例】
              当前数据周期为1日线，BarInterval等于1；
              当前数据周期为22日线，BarInterval等于22；
              当前数据周期为60分钟线，BarInterval等于60；
              当前数据周期为1TICK线，BarInterval等于1；br> 当前数据周期为5000量线，BarInterval等于5000。
        '''
        return self._dataModel.getBarInterval(contractNo)
        
    def BarType(self, contractNo):
        '''
        【说明】
              合约图表周期类型值

        【语法】
              int BarType()

        【参数】
              contractNo 合约编号，为空时取的时设置界面设置的周期数值

        【备注】
              返回值为整型，通常和BarInterval一起使用进行数据周期的判别
              返回值如下定义：
              0 分时
              1 TICK线
              2 秒线
              3 分钟线
              4 小时线
              5 日线
              6 周线
              7 月线
              8 年线


        【示例】
              当前数据周期为22日线，BarType等于5；
              当前数据周期为60分钟线，BarType等于3；
              当前数据周期为1TICK线，BarType等于1；
              当前数据周期为3秒线，BarType等于2。
        '''
        return self._dataModel.getBarType(contractNo)
        
    def BidAskSize(self, contractNo):
        '''
        【说明】
              买卖盘个数

        【语法】
              int BidAskSize(contractNo)

        【参数】
              contractNo: 合约编号，为空时，取基准合约。

        【备注】
              返回整型

        【示例】
              郑商所白糖的买卖盘个数为5个，因此其BidAskSize等于5；
              郑商所棉花的买卖盘个数为1个，因此其BidAskSize等于1。 
        '''
        return self._dataModel.getBidAskSize(contractNo)

    def CanTrade(self, contractNo):
        '''
        【说明】
              合约是否支持交易

        【语法】
              Bool CanTrade(contractNo)

        【参数】
              contractNo: 合约编号，为空时，取基准合约。

        【备注】
              返回Bool值，支持返回True，否则返回False

        【示例】
              无 
        '''
        return self._dataModel.getCanTrade(contractNo)
        
    def ContractUnit(self, contractNo):
        '''
        【说明】
              每张合约包含的基本单位数量, 即每手乘数

        【语法】
              int ContractUnit(contractNo)

        【参数】
              contractNo: 合约编号，为空时，取基准合约。

        【备注】
              返回整型，1张合约包含多少标底物。

        【示例】
              无 
        '''
        return self._dataModel.getContractUnit(contractNo)
        
    def ExchangeName(self, contractNo):
        '''
        【说明】
              合约对应交易所名称

        【语法】
              string ExchangeName(contractNo)

        【参数】
              contractNo: 合约编号，为空时，取基准合约。

        【备注】
              返回字符串

        【示例】
              郑商所下各合约的交易所名称为："郑州商品交易所"
        '''
        return self._dataModel.getExchangeName(contractNo)
        
    def ExpiredDate(self, contractNo):
        '''
        【说明】
              合约最后交易日

        【语法】
              string ExpiredDate(contractNo)

        【参数】
              contractNo: 合约编号，为空时，取基准合约。

        【备注】
              返回字符串

        【示例】
              无
        '''
        return self._dataModel.getExpiredDate()
        
    def GetSessionCount(self, contractNo):
        '''
        【说明】
              获取交易时间段的个数

        【语法】
              int GetSessionCount(contractNo)

        【参数】
              contractNo: 合约编号，为空时，取基准合约。

        【备注】
              返回整型

        【示例】
              无
        '''
        return self._dataModel.getGetSessionCount(contractNo)

    def GetSessionEndTime(self, contractNo, index):
        '''
        【说明】
              获取指定交易时间段的结束时间。

        【语法】
              float GetSessionEndTime(contractNo, index)

        【参数】
              contractNo 合约编号，为空时，取基准合约。
              index 交易时间段的索引值, 从0开始。

        【备注】
              返回浮点数

        【示例】
              contractNo = "ZCE|F|SR|905"
              sessionCount = GetSessionCount(contractNo)
              for i in range(0, sessionCount-1):
                sessionEndTime = GetSessionEndTime(contractNo, i)
        '''
        return self._dataModel.getSessionEndTime(contractNo, index)

    def GetSessionStartTime(self, contractNo, index):
        '''
        【说明】
              获取指定交易时间段的开始时间。

        【语法】
              float GetSessionStartTime(contractNo, index)

        【参数】
              contractNo 合约编号，为空时，取基准合约。
              index 交易时间段的索引值, 从0开始。

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getGetSessionStartTime(contractNo, index)

    def GetNextTimeInfo(self, contractNo, timeStr):
        '''
        【说明】
              获取指定合约指定时间点的下一个时间点及交易状态。

        【语法】
              dict GetNextTimeInfo(contractNo, timeStr)

        【参数】
              contractNo 合约编号，为空时，取基准合约。
              timeStr 指定的时间点，格式为HH:MM:SS。

        【备注】
              返回时间字典，结构如下：
              {
                'Time' : 210000000,
                'TradeState' : 3
              }
              其中Time对应的值表示指定时间timeStr的下一个时间点，数据格式为整数，例如210000000表示格式化的时间为21:00:00.000
              TradeState表示对应时间点的交易状态，数据类型为字符，可能出现的值及相应的状态含义如下：
                1 : 集合竞价
                2 : 集合竞价撮合
                3 : 连续交易
                4 : 暂停
                5 : 闭市
                6 : 闭市处理时间
                0 : 交易日切换时间
                N : 未知状态
                I : 正初始化
                R : 准备就绪
              异常情况返回为空字典：{}

        【示例】
              GetNextTimeInfo('SHFE|F|CU|1907', '22:00:00') # 获取22:00:00后下一个时间点的时间和交易状态
              获取当前时间下一个时间点的时间和交易状态
              import time # 需要在策略头部添加time库
              curTime = time.strftime('%H:%M:%S',time.localtime(time.time()))
              timeInfoDict = GetNextTimeInfo("SHFE|F|CU|1907", curTime)
        '''
        return self._dataModel.getNextTimeInfo(contractNo, timeStr)

    def MarginRatio(self, contractNo):
        '''
        【说明】
              获取合约默认保证金比率

        【语法】
              float MarginRatio()

        【参数】
              contractNo 合约编号，为空时，取基准合约。

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getMarginRatio(contractNo)
        
    def MaxBarsBack(self):
        '''
        【说明】
              最大回溯Bar数

        【语法】
              float  MaxBarsBack()

        【参数】
              无

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getMaxBarsBack()
        
    def MaxSingleTradeSize(self):
        '''
        【说明】
              单笔交易限量

        【语法】
              int MaxSingleTradeSize()

        【参数】
              无

        【备注】
              返回整型，单笔交易限量，对于不能交易的商品，返回-1，对于无限量的商品，返回0

        【示例】
              无
        '''
        return self._dataModel.getMaxSingleTradeSize()

    def PriceTick(self, contractNo):
        '''
        【说明】
              合约最小变动价

        【语法】
              int PriceTick(contractNo)

        【参数】
              contractNo 合约编号，为空时，取基准合约。

        【备注】
              无

        【示例】
              沪铝的最小变动价为5，因此其PriceTick等于5
        '''
        return self._dataModel.getPriceTick(contractNo)
        
    def OptionStyle(self, contractNo):
        '''
        【说明】
              期权类型，欧式还是美式

        【语法】
              int OptionStyle()

        【参数】
              contractNo 合约编号，为空时，取基准合约。

        【备注】
              返回整型，0为欧式，1为美式

        【示例】
              无
        '''
        return self._dataModel.getOptionStyle(contractNo)
        
    def OptionType(self, contractNo):
        '''
        【说明】
              返回期权的类型，是看涨还是看跌期权

        【语法】
              int OptionType()

        【参数】
              无

        【备注】
              返回整型，0为看涨，1为看跌， -1为异常。

        【示例】
              无
        '''
        return self._dataModel.getOptionType(contractNo)
        
    def PriceScale(self, contractNo):
        '''
        【说明】
              合约价格精度

        【语法】
              float PriceScale()

        【参数】
              无

        【备注】
              返回浮点数

        【示例】
              上期沪金的报价精确到小数点2位，则PriceScale为1/100，PriceScale的返回值为0.01
        '''
        return self._dataModel.getPriceScale(contractNo)
        
    def RelativeSymbol(self):
        '''
        【说明】
              关联合约

        【语法】
              string RelativeSymbol()

        【参数】
              无

        【备注】
              返回字符串
              主连或者近月合约，返回具体的某个月份的合约
              期权返回标的合约
              套利返回单腿合约，以逗号分隔
              其他，返回空字符串

        【示例】
              "ZCE|O|SR|905C5000"白糖期权的关联合约为"ZCE|F|SR|905"
              "SPD|m|OI/Y|001|001"菜油豆油价比的关联合约为"ZCE|F|OI|001,DCE|F|Y|001"
        '''
        return self._dataModel.getRelativeSymbol()
        
    def StrikePrice(self):
        '''
        【说明】
              获取期权行权价

        【语法】
              float StrikePrice()

        【参数】
              无

        【备注】
              返回浮点数

        【示例】
              无
        '''
        return self._dataModel.getStrikePrice()
        
    def Symbol(self):
        '''
        【说明】
              获取合约编号

        【语法】
              string Symbol()

        【参数】
              无

        【备注】
              期货、现货、指数: <EXG>|<TYPE>|<ROOT>|<YEAR><MONTH>[DAY]
              
              期权            : <EXG>|<TYPE>|<ROOT>|<YEAR><MONTH>[DAY]<CP><STRIKE>
              
              跨期套利        : <EXG>|<TYPE>|<ROOT>|<YEAR><MONTH>[DAY]|<YEAR><MONTH>[DAY]
              
              跨品种套利      : <EXG>|<TYPE>|<ROOT&ROOT>|<YEAR><MONTH>[DAY]
              
              极星跨期套利    : <EXG>|s|<ROOT>|<YEAR><MONTH>[DAY]|<YEAR><MONTH>[DAY]
              
              极星跨品种套利  : <EXG>|m|<ROOT-ROOT>|<YEAR><MONTH>|<YEAR><MONTH>
              
              极星现货期货套利: <EXG>|p|<ROOT-ROOT>||<YEAR><MONTH>

        【示例】
              "ZCE|F|SR|001", "ZCE|O|SR|001C5000"
        '''
        return self._dataModel.getSymbol()
        
    def SymbolName(self, contractNo):
        '''
        【说明】
              获取合约名称

        【语法】
              string SymbolName()

        【参数】
              无

        【备注】
              返回字符串

        【示例】
              "ZCE|F|SR|001"的合约名称为"白糖001"
        '''
        return self._dataModel.getSymbolName(contractNo)
        
    def SymbolType(self, contractNo):
        '''
        【说明】
              获取合约所属的品种编号

        【语法】
              string SymbolType()

        【参数】
              无

        【备注】
              返回字符串

        【示例】
              "ZCE|F|SR|001"的品种编号为"ZCE|F|SR"
        '''
        return self._dataModel.getSymbolType(contractNo)

    # //////////////////////策略状态////////////////////
    def AvgEntryPrice(self, contractNo):
        '''
        【说明】
              获得当前持仓指定合约的平均建仓价格。

        【语法】
              float AvgEntryPrice(string contractNo)

        【参数】
              contractNo 合约编号，默认为基准合约。

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getAvgEntryPrice(contractNo)

    def BarsSinceEntry(self, contractNo):
        '''
        【说明】
              获得当前持仓中指定合约的第一个建仓位置到当前位置的Bar计数。

        【语法】
              int BarsSinceEntry(string contractNo)

        【参数】
              contractNo 合约编号，默认为基准合约。

        【备注】
              获得当前持仓指定合约的第一个建仓位置到当前位置的Bar计数，返回值为整型。
              只有当MarketPosition != 0时，即有持仓的状况下，该函数才有意义，否则返回0。
              注意：在开仓Bar上为0。

        【示例】
              无
        '''
        return self._dataModel.getBarsSinceEntry(contractNo)

    def MarketPosition(self, contractNo):
        '''
        【说明】
               获得当前持仓状态 。

        【语法】
              int MarketPosition(string contractNo)

        【参数】
              contractNo 合约编号，默认为基准合约。

        【备注】
              获得当前持仓状态，返回值为整型。
              返回值定义如下：
                -1 当前位置为持空仓
                0 当前位置为持平
                1 当前位置为持多仓

        【示例】
              if(MarketPosition("ZCE|F|SR|905")==1)判断合约ZCE|F|SR|905当前是否持多仓
              if(MarketPosition("ZCE|F|SR|905")!=0)判断合约ZCE|F|SR|905当前是否有持仓，无论持空仓或多仓
        '''
        return self._dataModel.getMarketPosition(contractNo)

    #////////////////////////////策略性能/////////////////
    def Available(self):
        '''
        【说明】
              返回策略当前可用虚拟资金。

        【语法】
              float Available()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getAvailable()

    def FloatProfit(self, contractNo):
        '''
        【说明】
              返回某个合约或者所有合约的浮动盈亏。

        【语法】
              float FloatProfit(string contractNo)

        【参数】
              contractNo 合约编号，为空时返回所有合约的浮动盈亏。

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getFloatProfit(contractNo)

    def GrossLoss(self):
        '''
        【说明】
              返回累计总亏损。

        【语法】
              float GrossLoss()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getGrossLoss()

    def GrossProfit(self):
        '''
        【说明】
              返回累计总利润。

        【语法】
              float GrossProfit()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getGrossProfit()

    def Margin(self, contractNo):
        '''
        【说明】
              返回某个合约或者所有合约的持仓保证金。

        【语法】
              float Margin(string contractNo)

        【参数】
              contractNo 合约编号，为空时返回所有合约的浮动盈亏。

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getMargin(contractNo)

    def NetProfit(self):
        '''
        【说明】
              返回该账户下的平仓盈亏。

        【语法】
              float NetProfit()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNetProfit()

    def NumEvenTrades(self):
        '''
        【说明】
              返回该账户下保本交易的总手数。

        【语法】
              int NumEvenTrades()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNumEvenTrades()

    def NumLosTrades(self):
        '''
        【说明】
              返回该账户下亏损交易的总手数。

        【语法】
              int NumLosTrades()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNumLosTrades()

    def NumWinTrades(self):
        '''
        【说明】
              返回该账户下盈利交易的总手数。

        【语法】
              int NumWinTrades()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNumWinTrades()

    def NumAllTimes(self):
        '''
        【说明】
              返回该账户的开仓次数。

        【语法】
              int NumAllTimes()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNumAllTimes()

    def NumWinTimes(self):
        '''
        【说明】
              返回该账户的盈利次数。

        【语法】
              int NumWinTimes()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNumWinTimes()

    def NumLoseTimes(self):
        '''
        【说明】
              返回该账户的亏损次数。

        【语法】
              int NumLoseTimes()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNumLoseTimes()

    def NumEventTimes(self):
        '''
        【说明】
              返回该账户的保本次数。

        【语法】
              int NumEventTimes()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getNumEventTimes()

    def PercentProfit(self):
        '''
        【说明】
              返回该账户的盈利成功率。

        【语法】
              float PercentProfit()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getPercentProfit()

    def TradeCost(self):
        '''
        【说明】
              返回该账户交易产生的手续费。

        【语法】
              float TradeCost()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getTradeCost()

    def TotalTrades(self):
        '''
        【说明】
              返回该账户的交易总开仓手数。

        【语法】
              int TotalTrades()

        【参数】
              无

        【备注】
              无

        【示例】
              无
        '''
        return self._dataModel.getTotalTrades()


    #////////////////////////////账户函数/////////////////
    def A_AccountID(self):
        '''
        【说明】
              返回当前公式应用的交易帐户ID。

        【语法】
              string A_AccountID()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户ID，返回值为字符串，无效时返回空串。
              注：不能用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getAccountId()

    def A_Cost(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的手续费。

        【语法】
              string A_Cost()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的手续费，返回值为浮点数。

        【示例】
              无
        '''
        return self._dataModel.getCost()

    def A_CurrentEquity(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的动态权益。

        【语法】
              float A_CurrentEquity()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的动态权益，返回值为浮点数。

        【示例】
              无
        '''
        return self._dataModel.getCurrentEquity()

    def A_FreeMargin(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的可用资金。

        【语法】
              float A_FreeMargin()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的可用资金，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getFreeMargin()

    def A_ProfitLoss(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的浮动盈亏。

        【语法】
              float A_ProfitLoss()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的浮动盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getProfitLoss()

    def A_TotalFreeze(self):
        '''
        【说明】
              返回当前公式应用的交易帐户的冻结资金。

        【语法】
              float A_TotalFreeze()

        【参数】
              无

        【备注】
              返回当前公式应用的交易帐户的冻结资金，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
        '''
        return self._dataModel.getTotalFreeze()

    def A_BuyAvgPrice(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的买入持仓均价。

        【语法】
              float A_BuyAvgPrice(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的买入持仓均价，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getBuyAvgPrice(contractNo)

    def A_BuyPosition(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的买入持仓。

        【语法】
              float A_BuyPosition(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的买入持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              当前持多仓2手，A_BuyPosition返回2。
         '''
        return self._dataModel.getBuyPosition(contractNo)

    def A_BuyProfitLoss(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的买入持仓盈亏。

        【语法】
              float A_BuyProfitLoss(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的买入持仓盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getBuyProfitLoss(contractNo)

    def A_SellAvgPrice(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的卖出持仓均价。

        【语法】
              float A_SellAvgPrice(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的卖出持仓均价，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getSellAvgPrice(contractNo)

    def A_SellPosition(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的卖出持仓。

        【语法】
              float A_SellPosition(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的卖出持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              当前持空仓3手，A_SellPosition返回3。
         '''
        return self._dataModel.getSellPosition(contractNo)

    def A_SellProfitLoss(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的卖出持仓盈亏。

        【语法】
              float A_SellProfitLoss(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的卖出持仓盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getSellProfitLoss(contractNo)

    def A_TotalAvgPrice(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的持仓均价。

        【语法】
              float A_TotalAvgPrice(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的持仓均价，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTotalAvgPrice(contractNo)

    def A_TotalPosition(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的总持仓。

        【语法】
              int A_TotalPosition(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的总持仓，返回值为浮点数。
              该持仓为所有持仓的合计值，正数表示多仓，负数表示空仓，零为无持仓。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTotalPosition(contractNo)

    def A_TotalProfitLoss(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的总持仓盈亏。

        【语法】
              float A_TotalProfitLoss(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的总持仓盈亏，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTotalProfitLoss(contractNo)

    def A_TodayBuyPosition(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的当日买入持仓。

        【语法】
              float A_TodayBuyPosition(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的当日买入持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTodayBuyPosition(contractNo)

    def A_TodaySellPosition(self, contractNo):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的当日卖出持仓。

        【语法】
              float A_TodaySellPosition(string contractNo)

        【参数】
              contractNo，指定商品的合约编号，为空时采用基准合约编号。

        【备注】
              返回当前公式应用的帐户下当前商品的当日卖出持仓，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getTodaySellPosition(contractNo)

    def A_OrderBuyOrSell(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的买卖类型。

        【语法】
              char A_OrderBuyOrSell(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的买卖类型，返回值为：
              B : 买入
              S : 卖出
              A : 双边
              该函数返回值可以与Enum_Buy、Enum_Sell等买卖状态枚举值进行比较，根据类型不同分别处理。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              nBorS = A_OrderBuyOrSell('1-1')
              if nBorS == Enum_Buy():
                ...
         '''
        return self._dataModel.getOrderBuyOrSell(orderId)

    def A_OrderEntryOrExit(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的开平仓状态。

        【语法】
              char A_OrderEntryOrExit(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的开平仓状态，返回值：
              N : 无
              O : 开仓
              C : 平仓
              T : 平今
              1 : 开平，应价时有效, 本地套利也可以
              2 : 平开，应价时有效, 本地套利也可以
              该函数返回值可以与Enum_Entry、Enum_Exit等开平仓状态枚举值进行比较，根据类型不同分别处理。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              orderFlag = A_OrderEntryOrExit('1-1')
              if orderFlag == Enum_Exit():
                ...
         '''
        return self._dataModel.getOrderEntryOrExit(orderId)

    def A_OrderFilledLot(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的成交数量。

        【语法】
              float A_OrderFilledLot(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的成交数量，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderFilledLot(orderId)

    def A_OrderFilledPrice(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的成交价格。

        【语法】
              float A_OrderFilledPrice(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的成交价格，返回值为浮点数。
              该成交价格可能为多个成交价格的平均值。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderFilledPrice(orderId)

    def A_OrderLot(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的委托数量。

        【语法】
              float A_OrderLot(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的委托数量，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderLot(orderId)

    def A_OrderPrice(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的委托价格。

        【语法】
              float A_OrderPrice(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的委托价格，返回值为浮点数。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderPrice(orderId)

    def A_OrderStatus(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的状态。

        【语法】
              char A_OrderStatus(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的状态，返回值：
              N : 无
              0 : 已发送
              1 : 已受理
              2 : 待触发
              3 : 已生效
              4 : 已排队
              5 : 部分成交
              6 : 完全成交
              7 : 待撤
              8 : 待改
              9 : 已撤单
              A : 已撤余单
              B : 指令失败
              C : 待审核
              D : 已挂起
              E : 已申请
              F : 无效单
              G : 部分触发
              H : 完全触发
              I : 余单失败
              该函数返回值可以与委托状态枚举函数Enum_Sended、Enum_Accept等函数进行比较，根据类型不同分别处理。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderStatus(orderId)

    def A_OrderTime(self, orderId):
        '''
        【说明】
              返回当前公式应用的帐户下当前商品的某个委托单的委托时间。

        【语法】
              struct_time A_OrderTime(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号。

        【备注】
              返回当前公式应用的帐户下当前商品的某个委托单的委托时间，返回值为格式化的时间。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.getOrderTime(orderId)

    def A_SendOrder(self, userNo, contractNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
        '''
        【说明】A_SendOrder
              针对指定的帐户、商品发送委托单。

        【语法】
              bool A_SendOrder(string userNo, string contractNo, char orderType, char validType, char orderDirct, char entryOrExit, char hedge, float orderPrice, int orderQty)

        【参数】
              userNo 指定的账户名称，
              contractNo 商品合约编号，
              orderType 订单类型，字符类型，可选值为：
                '1' : 市价单
                '2' : 限价单
                '3' : 市价止损
                '4' : 限价止损
                '5' : 行权
                '6' : 弃权
                '7' : 询价
                '8' : 应价
                '9' : 冰山单
                'A' : 影子单
                'B' : 互换
                'C' : 套利申请
                'D' : 套保申请
                'F' : 行权前期权自对冲申请
                'G' : 履约期货自对冲申请
                'H' : 做市商留仓
                可使用如Enum_Order_Market、Enum_Order_Limit等订单类型枚举函数获取相应的类型，
              validType 订单有效类型，字符类型， 可选值为：
                '0' : 当日有效
                '1' : 长期有效
                '2' : 限期有效
                '3' : 即时部分
                '4' : 即时全部
                可使用如Enum_GFD、Enum_GTC等订单有效类型枚举函数获取相应的类型，
              orderDirct 发送委托单的买卖类型，取值为Enum_Buy或Enum_Sell之一，
              entryOrExit 发送委托单的开平仓类型，取值为Enum_Entry,Enum_Exit,Enum_ExitToday之一，
              hedge 投保标记，字符类型，可选值为：
                'T' : 投机
                'B' : 套保
                'S' : 套利
                'M' : 做市
                可使用如Enum_Speculate、Enum_Hedge等订单投保标记枚举函数获取相应的类型，
              orderPrice 委托单的交易价格，
              orderQty 委托单的交易数量。

        【备注】
              针对当前公式指定的帐户、商品发送委托单，发送成功返回如"1-2"的下单编号，发送失败返回空字符串""。
              返回结果形式未：retCode, retMsg，retCode的数据类型为可以为负的整数, retMsg的数据类型为字符串。
              其中发送成功时retCode为0，retMsg为返回的下单编号，其组成规则为：策略id-该策略中发送委托单的次数，所以下单编号"1-2"表示在策略id为1的策略中的第2次发送委托单返回的下单编号。
              当发送失败时retCode为负数，retMsg为返回的发送失败的原因。
              该函数直接发单，不经过任何确认，并会在每次公式计算时发送，一般需要配合着仓位头寸进行条件处理，在不清楚运行机制的情况下，请慎用。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              retCode, retMsg = A_SendOrder(UserId, ContractId, Enum_Order_Limit(), Enum_FOK(), Enum_Buy(), Enum_Exit(), Enum_Speculate(), Q_AskPrice(), OrderNum)
              当retCode为0时表明发送订单信息成功。
         '''
        return self._dataModel.sendOrder(userNo, contractNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)

    def A_DeleteOrder(self, orderId):
        '''
        【说明】
              针对当前公式应用的帐户、商品发送撤单指令。

        【语法】
              bool A_DeleteOrder(string orderId)

        【参数】
              orderId 使用A_SendOrder返回的下单编号，为空时使用当日最后成交的委托编号作为查询依据。

        【备注】
              针对当前公式应用的帐户、商品发送撤单指令，发送成功返回True, 发送失败返回False。
              该函数直接发单，不经过任何确认，并会在每次公式计算时发送，一般需要配合着仓位头寸进行条件处理，在不清楚运行机制的情况下，请慎用。
              注：不能使用于历史测试，仅适用于实时行情交易。

        【示例】
              无
         '''
        return self._dataModel.deleteOrder(orderId)
        
    #/////////////////////////////枚举函数/////////////////
    def Enum_Buy(self):
        '''
        【说明】
              返回买卖状态的买入枚举值

        【语法】
              char Enum_Buy()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumBuy()

    def Enum_Sell(self):
        '''
        【说明】
              返回买卖状态的卖出枚举值

        【语法】
              char Enum_Sell()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumSell()

    def Enum_Entry(self):
        '''
        【说明】
              返回开平状态的开仓枚举值

        【语法】
              char Enum_Entry()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumEntry()

    def Enum_Exit(self):
        '''
        【说明】
              返回开平状态的平仓枚举值

        【语法】
              char Enum_Exit()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumExit()

    def Enum_ExitToday(self):
        '''
        【说明】
              返回开平状态的平今枚举值

        【语法】
              char Enum_ExitToday()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumExitToday()

    def Enum_EntryExitIgnore(self):
        '''
        【说明】
              返回开平状态不区分开平的枚举值

        【语法】
              char Enum_EntryExitIgnore()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumEntryExitIgnore()

    def Enum_Sended(self):
        '''
        【说明】
              返回委托状态为已发送的枚举值

        【语法】
              char Enum_Sended()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumSended()

    def Enum_Accept(self):
        '''
        【说明】
              返回委托状态为已受理的枚举值

        【语法】
              char Enum_Accept()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumAccept()

    def Enum_Triggering(self):
        '''
        【说明】
              返回委托状态为待触发的枚举值

        【语法】
              char Enum_Triggering()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumTriggering()

    def Enum_Active(self):
        '''
        【说明】
              返回委托状态为已生效的枚举值

        【语法】
              char Enum_Active()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumActive()

    def Enum_Queued(self):
        '''
        【说明】
              返回委托状态为已排队的枚举值

        【语法】
              char Enum_Queued()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumQueued()

    def Enum_FillPart(self):
        '''
        【说明】
              返回委托状态为部分成交的枚举值

        【语法】
              char Enum_FillPart()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumFillPart()

    def Enum_Filled(self):
        '''
        【说明】
              返回委托状态为全部成交的枚举值

        【语法】
              char Enum_Filled()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumFilled()

    def Enum_Canceling(self):
        '''
        【说明】
              返回委托状态为待撤的枚举值

        【语法】
              char Enum_Canceling()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumCanceling()

    def Enum_Modifying(self):
        '''
        【说明】
              返回委托状态为待改的枚举值

        【语法】
              char Enum_Modifying()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumModifying()

    def Enum_Canceled(self):
        '''
        【说明】
              返回委托状态为已撤单的枚举值

        【语法】
              char Enum_Canceled()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumCanceled()

    def Enum_PartCanceled(self):
        '''
        【说明】
              返回委托状态为已撤余单的枚举值

        【语法】
              char Enum_PartCanceled()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPartCanceled()

    def Enum_Fail(self):
        '''
        【说明】
              返回委托状态为指令失败的枚举值

        【语法】
              char Enum_Fail()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumFail()

    def Enum_Suspended(self):
        '''
        【说明】
              返回委托状态为已挂起的枚举值

        【语法】
              char Enum_Suspended()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumSuspended()

    def Enum_Apply(self):
        '''
        【说明】
              返回委托状态为已申请的枚举值

        【语法】
              char Enum_Apply()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumApply()

    def Enum_Period_Tick(self):
        '''
        【说明】
              返回周期类型成交明细的枚举值

        【语法】
              char Enum_Period_Tick()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodTick()
        
    def Enum_Period_Dyna(self):
        '''
        【说明】
              返回周期类型分时图枚举值

        【语法】
              char Enum_Period_Dyna()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodDyna() 
        
    def Enum_Period_Second(self):
        '''
        【说明】
              返回周期类型秒线的枚举值

        【语法】
              char Enum_Period_Second()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodSecond() 
        
    def Enum_Period_Min(self):
        '''
        【说明】
              返回周期类型分钟线的枚举值

        【语法】
              char Enum_Period_Min()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodMin() 
        
    def Enum_Period_Hour(self):
        '''
        【说明】
              返回周期类型小时线的枚举值

        【语法】
              char Enum_Period_Hour()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodHour() 
        
    def Enum_Period_Day(self):
        '''
        【说明】
              返回周期类型日线的枚举值

        【语法】
              char Enum_Period_Day()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodDay() 
        
    def Enum_Period_Week(self):
        '''
        【说明】
              返回周期类型周线的枚举值

        【语法】
              char Enum_Period_Week()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodWeek()

    def Enum_Period_Month(self):
        '''
        【说明】
              返回周期类型月线的枚举值

        【语法】
              char Enum_Period_Month()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodMonth() 
    
    def Enum_Period_Year(self):
        '''
        【说明】
              返回周期类型年线的枚举值

        【语法】
              char Enum_Period_Year()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodYear() 

    def Enum_Period_DayX(self):
        '''
        【说明】
              返回周期类型多日线的枚举值

        【语法】
              char Enum_Period_DayX()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumPeriodDayX()

    def RGB_Red(self):
        '''
        【说明】
             返回颜色类型红色的枚举值

        【语法】
              int RGB_Red()

        【参数】
              无

        【备注】
              返回16进制颜色代码

        【示例】
              无
        '''
        return self._dataModel.getRed()

    def RGB_Green(self):
        '''
        【说明】
              返回颜色类型绿色的枚举值

        【语法】
              int RGB_Green()

        【参数】
              无

        【备注】
              返回16进制颜色代码

        【示例】
              无
        '''
        return self._dataModel.getGreen()

    def RGB_Blue(self):
        '''
        【说明】
              返回颜色类型蓝色的枚举值

        【语法】
              int RGB_Blue()

        【参数】
              无

        【备注】
              返回16进制颜色代码

        【示例】
              无
        '''
        return self._dataModel.getBlue()

    def RGB_Purple(self):
        '''
        【说明】
              返回颜色类型紫色的枚举值

        【语法】
              int RGB_Purple()

        【参数】
              无

        【备注】
              返回16进制颜色代码

        【示例】
              无
        '''
        return self._dataModel.getPurple()

    def RGB_Gray(self):
        '''
        【说明】
              返回颜色类型灰色的枚举值

        【语法】
              int RGB_Gray()

        【参数】
              无

        【备注】
              返回16进制颜色代码

        【示例】
              无
        '''
        return self._dataModel.getGray()

    def RGB_Brown(self):
        '''
        【说明】
              返回颜色类型褐色的枚举值

        【语法】
              int RGB_Brown()

        【参数】
              无

        【备注】
              返回16进制颜色代码

        【示例】
              无
        '''
        return self._dataModel.getBrown()

    def Enum_Order_Market(self):
        '''
        【说明】
              返回订单类型市价单的枚举值

        【语法】
              char Enum_Order_Market()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderMarket()

    def Enum_Order_Limit(self):
        '''
        【说明】
              返回订单类型限价单的枚举值

        【语法】
              char Enum_Order_Limit()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderLimit()

    def Enum_Order_MarketStop(self):
        '''
        【说明】
              返回订单类型市价止损单的枚举值

        【语法】
              char Enum_Order_MarketStop()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderMarketStop()

    def Enum_Order_LimitStop(self):
        '''
        【说明】
              返回订单类型限价止损单的枚举值

        【语法】
              char Enum_Order_LimitStop()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderLimitStop()

    def Enum_Order_Execute(self):
        '''
        【说明】
              返回订单类型行权单的枚举值

        【语法】
              char Enum_Order_Execute()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderExecute()

    def Enum_Order_Abandon(self):
        '''
        【说明】
              返回订单类型弃权单的枚举值

        【语法】
              char Enum_Order_Abandon()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderAbandon()

    def Enum_Order_Enquiry(self):
        '''
        【说明】
              返回订单类型询价单的枚举值

        【语法】
              char Enum_Order_Enquiry()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderEnquiry()

    def Enum_Order_Offer(self):
        '''
        【说明】
              返回订单类型应价单的枚举值

        【语法】
              char Enum_Order_Offer()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderOffer()

    def Enum_Order_Iceberg(self):
        '''
        【说明】
              返回订单类型冰山单的枚举值

        【语法】
              char Enum_Order_Iceberg()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderIceberg()

    def Enum_Order_Ghost(self):
        '''
        【说明】
              返回订单类型影子单的枚举值

        【语法】
              char Enum_Order_Ghost()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderGhost()

    def Enum_Order_Swap(self):
        '''
        【说明】
              返回订单类型互换单的枚举值

        【语法】
              char Enum_Order_Swap()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderSwap()

    def Enum_Order_SpreadApply(self):
        '''
        【说明】
              返回订单类型套利申请的枚举值

        【语法】
              char Enum_Order_SpreadApply()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderSpreadApply()

    def Enum_Order_HedgApply(self):
        '''
        【说明】
              返回订单类型套保申请的枚举值

        【语法】
              char Enum_Order_HedgApply()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderHedgApply()

    def Enum_Order_OptionAutoClose(self):
        '''
        【说明】
              返回订单类型行权前期权自对冲申请的枚举值

        【语法】
              char Enum_Order_OptionAutoClose()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderOptionAutoClose()

    def Enum_Order_FutureAutoClose(self):
        '''
        【说明】
              返回订单类型履约期货自对冲申请的枚举值

        【语法】
              char Enum_Order_FutureAutoClose()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderFutureAutoClose()

    def Enum_Order_MarketOptionKeep(self):
        '''
        【说明】
              返回订单类型做市商留仓的枚举值

        【语法】
              char Enum_Order_MarketOptionKeep()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOrderMarketOptionKeep()

    def Enum_GFD(self):
        '''
        【说明】
              返回订单有效类型当日有效的枚举值

        【语法】
              char Enum_GFD()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumGFD()

    def Enum_GTC(self):
        '''
        【说明】
              返回订单有效类型当日有效的枚举值

        【语法】
              char Enum_GTC()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumGTC()

    def Enum_GTD(self):
        '''
        【说明】
              返回订单有效类型限期有效的枚举值

        【语法】
              char Enum_GTD()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumGTD()

    def Enum_IOC(self):
        '''
        【说明】
              返回订单有效类型即时部分有效的枚举值

        【语法】
              char Enum_IOC()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumIOC()

    def Enum_FOK(self):
        '''
        【说明】
              返回订单有效类型即时全部有效的枚举值

        【语法】
              char Enum_FOK()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumFOK()

    def Enum_Speculate(self):
        '''
        【说明】
              返回订单投保标记投机的枚举值

        【语法】
              char Enum_Speculate()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumSpeculate()

    def Enum_Hedge(self):
        '''
        【说明】
              返回订单投保标记套保的枚举值

        【语法】
              char Enum_Hedge()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumHedge()

    def Enum_Spread(self):
        '''
        【说明】
              返回订单投保标记套利的枚举值

        【语法】
              char Enum_Spread()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumSpread()

    def Enum_Market(self):
        '''
        【说明】
              返回订单投保标记做市的枚举值

        【语法】
              char Enum_Market()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumMarket()

    def Enum_Data_Close(self):
        '''
        【说明】
              返回收盘价的枚举值

        【语法】
              char Enum_Data_Close()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumClose()

    def Enum_Data_Open(self):
        '''
        【说明】
              返回开盘价的枚举值

        【语法】
              char Enum_Data_Open()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOpen()

    def Enum_Data_High(self):
        '''
        【说明】
              返回最高价的枚举值

        【语法】
              char Enum_Data_High()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumHigh()

    def Enum_Data_Low(self):
        '''
        【说明】
              返回最低价的枚举值

        【语法】
              char Enum_Data_Low()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumLow()

    def Enum_Data_Median(self):
        '''
        【说明】
              返回中间价的枚举值，中间价=（最高价+最低价）/ 2

        【语法】
              char Enum_Data_Median()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumMedian()

    def Enum_Data_Typical(self):
        '''
        【说明】
              返回标准价的枚举值，标准价=（最高价+最低价+收盘价）/ 3

        【语法】
              char Enum_Data_Typical()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumTypical()

    def Enum_Data_Weighted(self):
        '''
        【说明】
              返回加权收盘价的枚举值，加权收盘价=（最高价+最低价+开盘价+收盘价）/ 4

        【语法】
              char Enum_Data_Weighted()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumWeighted()

    def Enum_Data_Vol(self):
        '''
        【说明】
              返回成交量的枚举值

        【语法】
              char Enum_Data_Vol()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumVol()

    def Enum_Data_Opi(self):
        '''
        【说明】
              返回持仓量的枚举值

        【语法】
              char Enum_Data_Opi()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumOpi()

    def Enum_Data_Time(self):
        '''
        【说明】
              返回K线时间的枚举值

        【语法】
              char Enum_Data_Time()

        【参数】
              无

        【备注】
              返回字符

        【示例】
              无
        '''
        return self._dataModel.getEnumTime()

    #//////////////////////设置函数////////////////////
    def GetConfig(self):
        return self._dataModel.getConfig()

    def SetBenchmark(self, contractNo):
        '''
        【说明】
              设置基准合约及触发策略的合约列表，参数不能为空

        【语法】
              int SetBenchmark(string contractNo1, string contractNo2, string contractNo3, ...)

        【参数】
              contractNo 合约编号，第一个合约编号为基准合约
              合约编号组成规则详见Symbol方法说明

        【备注】
              返回整型, 0成功，-1失败
              如果使用合约的即时行情、K线、交易数据触发策略，则必须在策略代码中使用该函数设置合约
              如果使用K线触发，则需要使用SetBarInterval函数设置类型和周期，否则设置界面选中的K线类型和周期

        【示例】
              SetBenchmark('ZCE|F|SR|905')
              SetBenchmark('ZCE|F|SR|905', 'ZCE|F|SR|912', 'ZCE|F|SR|001')
        '''
        return self._dataModel.setSetBenchmark(contractNo)

    def AddUserNo(self, userNo):
        '''
        【说明】
              添加实盘交易账户

        【语法】
              int SetUserNo(string userNo)

        【参数】
              userNo 实盘交易账户，不能为空字符串

        【备注】
              返回整型, 0成功，-1失败
              若需要添加多个不同的交易账号，则可多次调用该账户

        【示例】
              SetUserNo('ET001')
        '''
        return self._dataModel.addUserNo(userNo)

    def SetBarInterval(self, contractNo, barType, barInterval, sampleConfig):
        '''
        【说明】
              设置指定合约的K线类型和K线周期，以及策略历史回测的起始点信息

        【语法】
              int SetBarInterval(string contractNo, char barType, int barInterval, int|string|char sampleConfig)

        【参数】
              contractNo 合约编号，默认为基础合约
              barType K线类型 t分时，T分笔，S秒线，M分钟，H小时，D日线，W周线，m月线，Y年线
              barInterval K线周期
              sampleConfig 策略历史回测的起始点信息，可选的值为：
                字符A : 使用所有K线
                字符N : 不执行历史K线
                整数 : 历史回测使用的K线根数
                字符串 : 用于历史回测样本的起始日期，格式为YYYYMMDD，精确到日，例如2019-04-30的日期格式为'20190430'
                默认为使用2000根K线进行回测

        【备注】
              返回整型, 0成功，-1失败
              通过该方法系统会订阅指定合约的K线数据，
              对于相同的合约，如果使用该函数设置不同的K线类型(barType)和周期(barInterval)，则系统会同时订阅指定的K线类型和周期的行情数据
              对于相同的合约，如果使用该函数设置不同的起始点信息(sampleConfig)，则以最后一个起始点信息为准

        【示例】
              SetBarInterval('ZCE|F|SR|906', 'M', 3, 'A') 订阅合约ZCE|F|SR|906的3分钟K线数据，并使用所有K线样本进行历史回测
              SetBarInterval('ZCE|F|SR|906', 'M', 3, 'N') 订阅合约ZCE|F|SR|906的3分钟K线数据，并使用所有K线样本进行历史回测
              SetBarInterval('ZCE|F|SR|906', 'M', 3, 2000) 订阅合约ZCE|F|SR|906的3分钟K线数据，并使用2000根K线样本进行历史回测
              SetBarInterval('ZCE|F|SR|906', 'M', 3) 订阅合约ZCE|F|SR|906的3分钟K线数据，由于sampleConfig的默认值为2000，所以使用2000根K线样本进行历史回测
              SetBarInterval('ZCE|F|SR|906', 'M', 3, '20190430') 订阅合约ZCE|F|SR|906的3分钟K线数据，并使用2019-04-30起的K线进行历史回测
        '''
        return self._dataModel.setBarInterval(contractNo, barType, barInterval, sampleConfig)

    def SetSample(self, sampleType, sampleValue):
        '''
        【说明】
              设置策略历史回测的样本数量，默认为使用2000根K线进行回测。

        【语法】
              int SetSample(char sampleType, int|string sampleValue)

        【参数】
              sampleType 历史回测起始点类型
                A : 使用所有K线
                D : 指定日期开始触发
                C : 使用固定根数
                N : 不执行历史K线
              sampleValue 可选，设置历史回测起始点使用的数值
                当sampleType为A或N时，sampleValue的值不设置；
                当sampleType为D时，sampleValue为形如'20190430'的string型触发指定日期；
                当sampleType为C时，sampleValue为int型历史回测使用的K线根数。

        【备注】
              返回整型，0成功，-1失败

        【示例】
              无
        '''
        return self._dataModel.setSample(sampleType, sampleValue)
        
    def SetInitCapital(self, capital, userNo):
        '''
        【说明】
              设置初始资金，不设置默认100万

        【语法】
              int SetInitCapital(float capital, string usrNo)

        【参数】
              capital 初始资金
              usrNo 账号名称

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetInitCapital(200*10000, 'ET001'), 设置账户ET001的初始资金为200万
        '''
        return self._dataModel.setInitCapital(capital, userNo)
        
    def SetMargin(self, type, value, contractNo):
        '''
        【说明】
              设置保证金参数，不设置取交易所公布参数

        【语法】
              int SetMargin(float type, float value, string contractNo)

        【参数】
              type 0：按比例收取保证金， 1：按定额收取保证金，
              value 按比例收取保证金时的比例， 或者按定额收取保证金时的额度，
              contractNo 合约编号，默认为基础合约。

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetMargin(0, 0.08) 设置基础合约的保证金按比例收取8%
              SetMargin(1, 80000, 'ZCE|F|SR|906') 设置合约ZCE|F|SR|906的保证金按额度收取80000
        '''
        return self._dataModel.setMargin(type, value, contractNo)
        
    def SetTradeFee(self, type, feeType, feeValue, contractNo):
        '''
        【说明】
              设置手续费收取方式，不设置取交易所公布参数

        【语法】
              int SetTradeFee(string type, int feeType, float feeValue, string contractNo)

        【参数】
              type 手续费类型，A-全部，O-开仓，C-平仓，T-平今
              feeType 手续费收取方式，1-按比例收取，2-按定额收取
              feeValue 按比例收取手续费时，feeValue为收取比例；按定额收取手续费时，feeValue为收取额度
              contractNo 合约编号，默认为基础合约
        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetTradeFee('O', 2， 5) 设置基础合约的开仓手续费为5元/手
              SetTradeFee('O', 1， 0.02) 设置基础合约的开仓手续费为每笔2%
              SetTradeFee('T', 2， 5, "ZCE|F|SR|906") 设置合约ZCE|F|SR|906的平今手续费为5元/手
        '''
        return self._dataModel.setTradeFee(type, feeType, feeValue, contractNo)

    def SetTriggerCont(self, contractNo):
        '''
        【说明】
              设置触发合约

        【语法】
              int SetTriggerCont(contractNo1, contractNo2, contractNo3, ...)

        【参数】
              contractNo 合约编号，最多设置4个

        【备注】
              返回整型, 0成功，-1失败
              不调用此函数，默认以基准合约触发


        【示例】
              SetTriggerCont('ZCE|F|SR|905')
              SetTriggerCont('ZCE|F|SR|905', 'ZCE|F|SR|912', 'ZCE|F|SR|001')
        '''
        return self._dataModel.setTriggerCont(contractNo)

    # def SetTradeMode(self, inActual, useSample, useReal):
    #     '''
    #     【说明】
    #          设置运行方式
    #
    #     【语法】
    #           int SetTradeMode(bool inActual, bool useSample, bool useReal)
    #
    #     【参数】
    #           inActual      True 表示在实盘上运行，False 表示在模拟盘上运行
    #           useSample     在模拟盘上是否使用历史数据进行回测
    #           useReal       在模拟盘上是否使用实时数据运行策略
    #
    #     【备注】
    #           返回整型，0成功，-1失败
    #
    #     【示例】
    #           SetTradeMode(False, True, True)    # 在模拟盘上使用历史数据回测，并使用实时数据继续运行策略
    #           SetTradeMode(True, True, True)     # 在模拟盘上使用历史数据回测，并使用实时数据继续运行策略；在实盘上使用实时数据运行策略
    #     '''
    #     return self._dataModel.setTradeMode(inActual, useSample, useReal)

    def SetActual(self):
        '''
        【说明】
             设置策略在实盘上运行

        【语法】
              int SetActual()

        【参数】
              无

        【备注】
              返回整型，0成功，-1失败

        【示例】
              无
        '''
        return self._dataModel.setActual()

    def SetOrderWay(self, type):
        '''
        【说明】
             设置发单方式

        【语法】
              int SetOrderWay(int type)

        【参数】
              type 在实盘上的发单方式，1 表示实时发单,2 表示K线完成后发单

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetOrderWay(1)    # 在实盘上使用实时数据运行策略，实时发单
              SetOrderWay(2)     # 在实盘上使用实时数据运行策略，在K线稳定后发单
        '''
        return self._dataModel.setOrderWay(type)

    def SetTradeDirection(self, tradeDirection):
        '''
        【说明】
             设置交易方向

        【语法】
              int SetTradeDirection(int tradeDirection)

        【参数】
              tradeDirection 设置交易方向
              0 : 双向交易
              1 : 仅多头
              2 : 仅空头

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetTradeDirection(0)    # 双向交易
        '''
        return self._dataModel.setTradeDirection(tradeDirection)

    def SetMinTradeQuantity(self, tradeQty):
        '''
        【说明】
             设置最小下单量，单位为手，默认值为1手。

        【语法】
              int SetMinTradeQuantity(int tradeQty)

        【参数】
              tradeQty 最小下单量，不超过1000

        【备注】
              返回整型，0成功，-1失败

        【示例】
              无
        '''
        return self._dataModel.setMinTradeQuantity(tradeQty)

    def SetHedge(self, hedge, contractNo):
        '''
        【说明】
             设置投保标志

        【语法】
              int SetHedge(char hedge, string contractNo)

        【参数】
              hedge 投保标志
              T : 投机
              B : 套保
              S : 套利
              M : 做市
              contractNo 合约编号，默认为基础合约

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetHedge('T') # 设置基础合约的投保标志为投机
              SetHedge('T', 'ZCE|F|SR|906') # 设置合约ZCE|F|SR|906的投保标志为投机
        '''
        return self._dataModel.setHedge(hedge, contractNo)

    def SetSlippage(self, slippage):
        '''
        【说明】
             设置滑点损耗

        【语法】
              int SetSlippage(float slippage)

        【参数】
              slippage 滑点损耗

        【备注】
              返回整型，0成功，-1失败

        【示例】
              无
        '''
        return self._dataModel.setSlippage(slippage)

    # def SetTriggerType(self, contractNo, type, value):
    #     '''
    #     【说明】
    #          设置触发方式
    #
    #     【语法】
    #           int SetTriggerType(string contractNo, int type, int|list value)
    #
    #     【参数】
    #           contractNo 合约编号，不能为空
    #           type 触发方式，可使用的值为：
    #             1 : 即时行情触发
    #             2 : 交易数据触发
    #             3 : 每隔固定时间触发
    #             4 : 指定时刻触发
    #           value 当触发方式是为每隔固定时间触发(type=3)时，value为触发间隔，单位为毫秒，必须为100的整数倍，
    #           当触发方式为指定时刻触发(type=4)时，value为触发时刻列表，时间的格式为'20190511121314'
    #           当type为其他值时，该值无效，可以不填
    #
    #     【备注】
    #           返回整型，0成功，-1失败
    #
    #     【示例】
    #           SetTriggerType("ZCE|F|SR|910", 3, 1000) # 每隔1000毫秒触发一次
    #           SetTriggerType("ZCE|F|SR|910", 4, ['20190511121314', '20190511121315', '20190511121316']) # 指定时刻触发
    #     '''
    #     return self._dataModel.setTriggerMode(contractNo, type, value)

    def SetTriggerType(self, type, value):
        '''
        【说明】
             设置触发方式

        【语法】
              int SetTriggerType(int type, int|list value)

        【参数】
              type 触发方式，可使用的值为：
                1 : 即时行情触发
                2 : 交易数据触发
                3 : 每隔固定时间触发
                4 : 指定时刻触发
              value 当触发方式是为每隔固定时间触发(type=3)时，value为触发间隔，单位为毫秒，必须为100的整数倍，
              当触发方式为指定时刻触发(type=4)时，value为触发时刻列表，时间的格式为'20190511121314'
              当type为其他值时，该值无效，可以不填

        【备注】
              返回整型，0成功，-1失败

        【示例】
              SetTriggerType(3, 1000) # 每隔1000毫秒触发一次
              SetTriggerType(4, ['20190511121314', '20190511121315', '20190511121316']) # 指定时刻触发
        '''
        return self._dataModel.setTriggerMode('', type, value)

    # //////////////////////其他函数////////////////////

    def PlotNumeric(self, name, value, color, main, axis, type, barsback):
        '''
        【说明】
            在当前Bar输出一个数值

        【语法】
            float PlotNumeric(string name,float value,int color,bool main, char axis, int type, int barsback=0)

        【参数】
            name  输出值的名称，不区分大小写；
            value 输出的数值；
            color 输出值的显示颜色，默认表示使用属性设置框中的颜色；
            main  指标是否加载到主图，True-主图，False-幅图，默认主图
            axis  指标是否使用独立坐标，True-独立坐标，False-非独立坐标，默认非独立坐标
            type  指标线性，0-竖直直线，1-指标线，2-柱子，3-竖线段，4-变色K线，5-线段，6-图标，7-点，8-位置格式
            barsback 从当前Bar向前回溯的Bar数，默认值为当前Bar。

        【备注】
            在当前Bar输出一个数值，输出的值用于在上层调用模块显示。返回数值型，即输入的Number。

        【示例】
            例1：PlotNumeric ("MA1",Ma1Value);
            输出MA1的值。
        '''
        return self._dataModel.setPlotNumeric(name, value, color, main, axis, type, barsback)
        
    def PlotIcon(self, value, icon, color, main, barsback):
        '''
        【说明】
            在当前Bar输出一个图标

        【语法】
            float PlotIcon(float Value,int Icon, int color, bool main, int barsback=0)

        【参数】
            value 输出的值
            icon 图标类型，0-默认图标，1-笑脸，2-哭脸，3-上箭头，4-下箭头，5-上箭头2, 6-下箭头2
                           7-喇叭，8-加锁，9-解锁，10-货币+，11-货币-，12-加号，13-减号，14-叹号，15-叉号
            color 输出值的显示颜色，默认表示使用属性设置框中的颜色；
            main  指标是否加载到主图，True-主图，False-幅图，默认主图
            barsback 从当前Bar向前回溯的Bar数，默认值为当前Bar。

        【备注】
            在当前Bar输出一个数值，输出的值用于在上层调用模块显示。返回数值型，即输入的Number。

        【示例】
            例1：PlotIcon(10,14);
            输出MA1的值。
        '''
        return self._dataModel.setPlotIcon(value, icon, color, main, barsback)
        
    def PlotText(self, value, text, color, main, barsback):
        '''
        【说明】
            在当前Bar输出字符串

        【语法】
            void PlotText(stirng value, text, int color, bool main, int barsback=0)

        【参数】
            value 输出的价格
            text 输出的字符串，最多支持19个英文字符
            color 输出值的显示颜色，默认表示使用属性设置框中的颜色；
            main  指标是否加载到主图，True-主图，False-幅图，默认主图
            barsback 从当前Bar向前回溯的Bar数，默认值为当前Bar。

        【备注】
            在当前Bar输出字符串，输出的值用于在上层调用模块显示。返回数值型，即输入的Number。

        【示例】
            例1：PlotText("ORDER");
        '''
        return self._dataModel.setPlotText(value, text, color, main, barsback)
        
    def PlotVertLine(self, color, main, axis, barsback):
        '''
        【说明】
            在当前Bar输出一个图标

        【语法】
            float PlotVertLine(color, bool main, bool axis, int barsback=0)

        【参数】
            color 输出值的显示颜色，默认表示使用属性设置框中的颜色；
            main  指标是否加载到主图，True-主图，False-幅图，默认主图
            axis  指标是否使用独立坐标，True-独立坐标，False-非独立坐标，默认非独立坐标
            barsback 从当前Bar向前回溯的Bar数，默认值为当前Bar。

        【备注】
            在当前Bar输出一个数值，输出的值用于在上层调用模块显示。返回数值型，即输入的Number。

        【示例】
            例1：PlotIcon(10,14);
            输出MA1的值。
        '''
        return self._dataModel.setPlotVertLine(color, main, axis, barsback)
        
    def UnPlotText(self, main, barsback):
        '''
        【说明】
            在当前Bar取消输出的字符串

        【语法】
            void PlotUnText(bool main, int barsback=0)

        【参数】
            main  指标是否加载到主图，True-主图，False-幅图，默认主图
            barsback 从当前Bar向前回溯的Bar数，默认值为当前Bar。

        【备注】
            在当前Bar取消字符串输出，输出的值用于在上层调用模块显示。返回数值型，即输入的Number。

        【示例】
            UnPlotText();
        '''
        return self._dataModel.setUnPlotText(main, barsback)
        
    
    def LogDebug(self, args):
        '''
        【说明】
             在运行日志窗口中打印用户指定的调试信息。

        【语法】
              LogDebug(args)

        【参数】
              args 用户需要打印的内容，如需要在运行日志窗口中输出多个内容，内容之间用英文逗号分隔。

        【备注】
              无

        【示例】
              accountId = A_AccountID()
              LogDebug("当前使用的用户账户ID为 : ", accountId)
              freeMargin = A_FreeMargin()
              LogDebug("当前使用的用户账户ID为 : %s，可用资金为 : %10.2f" % (accountId, freeMargin))
        '''
        return self._dataModel.LogDebug(args)

    def LogInfo(self, args):
        '''
        【说明】
             在运行日志窗口中打印用户指定的普通信息。

        【语法】
              LogInfo(args)

        【参数】
              args 用户需要打印的内容，如需要在运行日志窗口中输出多个内容，内容之间用英文逗号分隔。

        【备注】
              无

        【示例】
              accountId = A_AccountID()
              LogInfo("当前使用的用户账户ID为 : ", accountId)
              freeMargin = A_FreeMargin()
              LogInfo("当前使用的用户账户ID为 : %s，可用资金为 : %10.2f" % (accountId, freeMargin))
        '''
        return self._dataModel.LogInfo(args)

    def LogWarn(self, args):
        '''
        【说明】
             在运行日志窗口中打印用户指定的警告信息。

        【语法】
              LogWarn(args)

        【参数】
              args 用户需要打印的内容，如需要在运行日志窗口中输出多个内容，内容之间用英文逗号分隔。

        【备注】
              无

        【示例】
              accountId = A_AccountID()
              LogWarn("当前使用的用户账户ID为 : ", accountId)
              freeMargin = A_FreeMargin()
              LogWarn("当前使用的用户账户ID为 : %s，可用资金为 : %10.2f" % (accountId, freeMargin))
        '''
        return self._dataModel.LogWarn(args)

    def LogError(self, args):
        '''
        【说明】
             在运行日志窗口中打印用户指定的错误信息。

        【语法】
              LogError(args)

        【参数】
              args 用户需要打印的内容，如需要在运行日志窗口中输出多个内容，内容之间用英文逗号分隔。

        【备注】
              无

        【示例】
              accountId = A_AccountID()
              LogError("当前使用的用户账户ID为 : ", accountId)
              freeMargin = A_FreeMargin()
              LogError("当前使用的用户账户ID为 : %s，可用资金为 : %10.2f" % (accountId, freeMargin))
        '''
        return self._dataModel.LogError(args)
        
    def strategyStatus(self):
        '''
        【说明】
             获取当前策略状态

        【语法】
              context.strategyStatus()

        【参数】
              无

        【备注】
              返回字符, 'H' 表示回测阶段; 'C' 表示实时数据阶段

        【示例】
              无
        '''
        pass
        
    def triggerType(self):
        '''
        【说明】
             获取当前触发类型 

        【语法】
              context.triggerType()

        【参数】
              无

        【备注】
              返回字符, 'T' 定时触发; 'C' 周期性触发; 'K' 实时阶段K线触发; 'H' 回测阶段K线触发; 'S' 即时行情触发; 'O' 委托状态变化触发 ; 'M' 成交回报触发  

        【示例】
              无
        '''
        pass
        
    def contractNo(self):
        '''
        【说明】
             获取当前触发合约

        【语法】
              context.contractNo()

        【参数】
              无

        【备注】
              返回字符串,例如: 'SHFE|F|CU|1907'

        【示例】
              无
        '''
        pass
        
    def kLineType(self):
        '''
        【说明】
             获取当前触发的K线类型

        【语法】
              context.kLineType()

        【参数】
              无

        【备注】
              返回字符, 't' 分时; 'T' 分笔; 'S' 秒线; 'M' 分钟; 'H' 小时; 'D' 日线; 'W' 周线; 'm' 月线; 'Y'年线

        【示例】
              无
        '''
        pass
        
    def kLineSlice(self):
        '''
        【说明】
             获取当前触发的K线周期

        【语法】
              context.kLineSlice()

        【参数】
              无

        【备注】
              返回整型，例如1

        【示例】
              无
        '''
        pass
        
    def tradeDate(self):
        '''
        【说明】
             获取当前触发的交易日

        【语法】
              context.tradeDate()

        【参数】
              无

        【备注】
              返回字符串, YYYYMMDD格式, '20190524'

        【示例】
              无
        '''
        pass
        
    def dateTimeStamp(self):
        '''
        【说明】
             获取当前触发的时间戳

        【语法】
              context.dateTimeStamp()

        【参数】
              无

        【备注】
              返回字符串, YYYYMMDD格式, '20190524'

        【示例】
              无
        '''
        pass
        
    def triggerData(self):
        '''
        【说明】
             获取当前触发类型对应的数据

        【语法】
              context.triggerData()

        【参数】
              无

        【备注】
              K线触发返回的是K线数据
              交易触发返回的是交易数据
              即时行情触发返回的是即时行情数据

        【示例】
              无
        '''
        pass

baseApi = BaseApi()

#////////////////////全局函数定义//////////////
#K线函数
def Date(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Date(contractNo, kLineType, kLineValue)

def D(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Date(contractNo, kLineType, kLineValue)

def Time(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Time(contractNo, kLineType, kLineValue)

def T(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Time(contractNo, kLineType, kLineValue)

def Open(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Open(contractNo, kLineType, kLineValue)

def O(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Open(contractNo, kLineType, kLineValue)

def High(contractNo='', kLineType='', kLineValue=0):
    return baseApi.High(contractNo, kLineType, kLineValue)

def H(contractNo='', kLineType='', kLineValue=0):
    return baseApi.High(contractNo, kLineType, kLineValue)

def Low(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Low(contractNo, kLineType, kLineValue)

def L(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Low(contractNo, kLineType, kLineValue)

def Close(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Close(contractNo, kLineType, kLineValue)

def C(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Close(contractNo, kLineType, kLineValue)

def Vol(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Vol(contractNo, kLineType, kLineValue)

def V(contractNo='', kLineType='', kLineValue=0):
    return baseApi.Vol(contractNo, kLineType, kLineValue)

def OpenInt(contractNo='', kLineType='', kLineValue=0):
    return baseApi.OpenInt(contractNo, kLineType, kLineValue)

def TradeDate(contractNo='', kLineType='', kLineValue=0):
    return baseApi.TradeDate(contractNo, kLineType, kLineValue)

def BarCount(contractNo='', kLineType='', kLineValue=0):
    return baseApi.BarCount(contractNo, kLineType, kLineValue)

def CurrentBar(contractNo='', kLineType='', kLineValue=0):
    return baseApi.CurrentBar(contractNo, kLineType, kLineValue)

def BarStatus(contractNo='', kLineType='', kLineValue=0):
    return baseApi.BarStatus(contractNo, kLineType, kLineValue)

def HistoryDataExist(contractNo='', kLineType='', kLineValue=0):
    return baseApi.HistoryDataExist(contractNo, kLineType, kLineValue)

def HisData(type, period, interval, contractNo='', maxLength=100):
    return baseApi.HisData(type, period, interval, contractNo, maxLength)
#即时行情
def Q_UpdateTime(contractNo=''):
    return baseApi.Q_UpdateTime(contractNo)

def Q_AskPrice(contractNo='', level=1):
    return baseApi.Q_AskPrice(contractNo, level)

def Q_AskPriceFlag(contractNo=''):
    return baseApi.Q_AskPriceFlag(contractNo)

def Q_AskVol(contractNo='', level=1):
    return baseApi.Q_AskVol(contractNo, level)

def Q_AvgPrice(contractNo=''):
    return baseApi.Q_AvgPrice(contractNo)

def Q_BidPrice(contractNo='', level=1):
    return baseApi.Q_BidPrice(contractNo, level)

def Q_BidPriceFlag(contractNo=''):
    return baseApi.Q_BidPriceFlag(contractNo)

def Q_BidVol(contractNo='', level=1):
    return baseApi.Q_BidVol(contractNo, level)

def Q_Close(contractNo=''):
    return baseApi.Q_Close(contractNo)

def Q_High(contractNo=''):
    return baseApi.Q_High(contractNo)

def Q_HisHigh(contractNo=''):
    return baseApi.Q_HisHigh(contractNo)

def Q_HisLow(contractNo=''):
    return baseApi.Q_HisLow(contractNo)

def Q_InsideVol(contractNo=''):
    return baseApi.Q_InsideVol(contractNo)

def Q_Last(contractNo=''):
    return baseApi.Q_Last(contractNo)

def Q_LastDate(contractNo=''):
    return baseApi.Q_LastDate(contractNo)

def Q_LastFlag(contractNo=''):
    return baseApi.Q_LastFlag(contractNo)

def Q_LastTime(contractNo=''):
    return baseApi.Q_LastTime(contractNo)

def Q_LastVol(contractNo=''):
    return baseApi.Q_LastVol(contractNo)

def Q_Low(contractNo=''):
    return baseApi.Q_Low(contractNo)

def Q_LowLimit(contractNo=''):
    return baseApi.Q_LowLimit(contractNo)

def Q_Open(contractNo=''):
    return baseApi.Q_Open(contractNo)

def Q_OpenInt(contractNo=''):
    return baseApi.Q_OpenInt(contractNo)

def Q_OpenIntFlag(contractNo=''):
    return baseApi.Q_OpenIntFlag(contractNo)

def Q_OutsideVol(contractNo=''):
    return baseApi.Q_OutsideVol(contractNo)

def Q_PreOpenInt(contractNo=''):
    return baseApi.Q_PreOpenInt(contractNo)

def Q_PreSettlePrice(contractNo=''):
    return baseApi.Q_PreSettlePrice(contractNo)

def Q_PriceChg(contractNo=''):
    return baseApi.Q_PriceChg(contractNo)

def Q_PriceChgRadio(contractNo=''):
    return baseApi.Q_PriceChgRadio(contractNo)

def Q_TodayEntryVol(contractNo=''):
    return baseApi.Q_TodayEntryVol(contractNo)

def Q_TodayExitVol(contractNo=''):
    return baseApi.Q_TodayExitVol(contractNo)

def Q_TotalVol(contractNo=''):
    return baseApi.Q_TotalVol(contractNo)

def Q_TurnOver(contractNo=''):
    return baseApi.Q_TurnOver(contractNo)

def Q_UpperLimit(contractNo=''):
    return baseApi.Q_UpperLimit(contractNo)

def QuoteDataExist(contractNo=''):
    return baseApi.QuoteDataExist(contractNo)

#策略状态
def AvgEntryPrice(contractNo=''):
    return baseApi.AvgEntryPrice(contractNo)

def BarsSinceEntry(contractNo=''):
    return baseApi.BarsSinceEntry(contractNo)

def MarketPosition(contractNo=''):
    return baseApi.MarketPosition(contractNo)
# 策略性能
def Available():
    return baseApi.Available()

def FloatProfit(contractNo=''):
    return baseApi.FloatProfit(contractNo)

def GrossLoss():
    return baseApi.GrossLoss()

def GrossProfit():
    return baseApi.GrossProfit()

def Margin(contractNo=''):
    return baseApi.Margin(contractNo)

def NetProfit():
    return baseApi.NetProfit()

def NumEvenTrades():
    return baseApi.NumEvenTrades()

def NumLosTrades():
    return baseApi.NumLosTrades()

def NumWinTrades():
    return baseApi.NumWinTrades()

def NumAllTimes():
    return baseApi.NumAllTimes()

def NumWinTimes():
    return baseApi.NumWinTimes()

def NumLoseTimes():
    return baseApi.NumLoseTimes()

def NumEventTimes():
    return baseApi.NumEventTimes()

def PercentProfit():
    return baseApi.PercentProfit()

def TradeCost():
    return baseApi.TradeCost()

def TotalTrades():
    return baseApi.TotalTrades()

# 账户函数
def A_AccountID():
    return baseApi.A_AccountID()

def A_Cost():
    return baseApi.A_Cost()

def A_CurrentEquity():
    return baseApi.A_CurrentEquity()

def A_FreeMargin():
    return baseApi.A_FreeMargin()

def A_ProfitLoss():
    return baseApi.A_ProfitLoss()

def A_TotalFreeze():
    return baseApi.A_TotalFreeze()

def A_BuyAvgPrice(contractNo=''):
    return baseApi.A_BuyAvgPrice(contractNo)

def A_BuyPosition(contractNo=''):
    return baseApi.A_BuyPosition(contractNo)

def A_BuyProfitLoss(contractNo=''):
    return baseApi.A_BuyProfitLoss(contractNo)

def A_SellAvgPrice(contractNo=''):
    return baseApi.A_SellAvgPrice(contractNo)

def A_SellPosition(contractNo=''):
    return baseApi.A_SellPosition(contractNo)

def A_SellProfitLoss(contractNo=''):
    return baseApi.A_SellProfitLoss(contractNo)

def A_TotalAvgPrice(contractNo=''):
    return baseApi.A_TotalAvgPrice(contractNo)

def A_TotalPosition(contractNo=''):
    return baseApi.A_TotalPosition(contractNo)

def A_TotalProfitLoss(contractNo=''):
    return baseApi.A_TotalProfitLoss(contractNo)

def A_TodayBuyPosition(contractNo=''):
    return baseApi.A_TodayBuyPosition(contractNo)

def A_TodaySellPosition(contractNo=''):
    return baseApi.A_TodaySellPosition(contractNo)

def A_OrderBuyOrSell(orderId=''):
    return baseApi.A_OrderBuyOrSell(orderId)

def A_OrderEntryOrExit(orderId=''):
    return baseApi.A_OrderEntryOrExit(orderId)

def A_OrderFilledLot(orderId=''):
    return baseApi.A_OrderFilledLot(orderId)

def A_OrderFilledPrice(orderId=''):
    return baseApi.A_OrderFilledPrice(orderId)

def A_OrderLot(orderId=''):
    return baseApi.A_OrderLot(orderId)

def A_OrderPrice(orderId=''):
    return baseApi.A_OrderPrice(orderId)

def A_OrderStatus(orderId=''):
    return baseApi.A_OrderStatus(orderId)

def A_OrderTime(orderId=''):
    return baseApi.A_OrderTime(orderId)

def A_SendOrder(userNo, contractNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty):
    return baseApi.A_SendOrder(userNo, contractNo, orderType, validType, orderDirct, entryOrExit, hedge, orderPrice, orderQty)

def A_DeleteOrder(orderId):
    return baseApi.A_DeleteOrder(orderId)

#策略交易
def Buy(share=0, price=0, contractNo=None):
    return baseApi.Buy(contractNo, share, price)

def BuyToCover(share=0, price=0, contractNo=None):
    return baseApi.BuyToCover(contractNo, share, price)

def Sell(share=0, price=0, contractNo=None):
    return baseApi.Sell(contractNo, share, price)

def SellShort(share=0, price=0, contractNo=None):
    return baseApi.SellShort(contractNo, share, price)
    
# 枚举函数
def Enum_Buy():
    return baseApi.Enum_Buy()

def Enum_Sell():
    return baseApi.Enum_Sell()

def Enum_Entry():
    return baseApi.Enum_Entry()

def Enum_Exit():
    return baseApi.Enum_Exit()

def Enum_ExitToday():
    return baseApi.Enum_ExitToday()

def Enum_EntryExitIgnore():
    return baseApi.Enum_EntryExitIgnore()

def Enum_Sended():
    return baseApi.Enum_Sended()

def Enum_Accept():
    return baseApi.Enum_Accept()

def Enum_Triggering():
    return baseApi.Enum_Triggering()

def Enum_Active():
    return baseApi.Enum_Active()

def Enum_Queued():
    return baseApi.Enum_Queued()

def Enum_FillPart():
    return baseApi.Enum_FillPart()

def Enum_Filled():
    return baseApi.Enum_Filled()

def Enum_Canceling():
    return baseApi.Enum_Canceling()

def Enum_Modifying():
    return baseApi.Enum_Modifying()

def Enum_Canceled():
    return baseApi.Enum_Canceled()

def Enum_PartCanceled():
    return baseApi.Enum_PartCanceled()

def Enum_Fail():
    return baseApi.Enum_Fail()

def Enum_Suspended():
    return baseApi.Enum_Suspended()

def Enum_Apply():
    return baseApi.Enum_Apply()

def Enum_Period_Tick():
    return baseApi.Enum_Period_Tick()
    
def Enum_Period_Dyna(): 
    return baseApi.Enum_Period_Dyna()
    
def Enum_Period_Second():
    return baseApi.Enum_Period_Second()
    
def Enum_Period_Min():
    return baseApi.Enum_Period_Min()
    
def Enum_Period_Hour():
    return baseApi.Enum_Period_Hour()
    
def Enum_Period_Day():
    return baseApi.Enum_Period_Day()
    
def Enum_Period_Week():
    return baseApi.Enum_Period_Week()
    
def Enum_Period_Month():
    return baseApi.Enum_Period_Month()
    
def Enum_Period_Year():
    return baseApi.Enum_Period_Year()
    
def Enum_Period_DayX():
    return baseApi.Enum_Period_DayX()

def RGB_Red():
    return baseApi.RGB_Red()

def RGB_Green():
    return baseApi.RGB_Green()

def RGB_Blue():
    return baseApi.RGB_Blue()

def RGB_Purple():
    return baseApi.RGB_Purple()

def RGB_Gray():
    return baseApi.RGB_Gray()

def RGB_Brown():
    return baseApi.RGB_Brown()

def Enum_Order_Market():
    return baseApi.Enum_Order_Market()

def Enum_Order_Limit():
    return baseApi.Enum_Order_Limit()

def Enum_Order_MarketStop():
    return baseApi.Enum_Order_MarketStop()

def Enum_Order_LimitStop():
    return baseApi.Enum_Order_LimitStop()

def Enum_Order_Execute():
    return baseApi.Enum_Order_Execute()

def Enum_Order_Abandon():
    return baseApi.Enum_Order_Abandon()

def Enum_Order_Enquiry():
    return baseApi.Enum_Order_Enquiry()

def Enum_Order_Offer():
    return baseApi.Enum_Order_Offer()

def Enum_Order_Iceberg():
    return baseApi.Enum_Order_Iceberg()

def Enum_Order_Ghost():
    return baseApi.Enum_Order_Ghost()

def Enum_Order_Swap():
    return baseApi.Enum_Order_Swap()

def Enum_Order_SpreadApply():
    return baseApi.Enum_Order_SpreadApply()

def Enum_Order_HedgApply():
    return baseApi.Enum_Order_HedgApply()

def Enum_Order_OptionAutoClose():
    return baseApi.Enum_Order_OptionAutoClose()

def Enum_Order_FutureAutoClose():
    return baseApi.Enum_Order_FutureAutoClose()

def Enum_Order_MarketOptionKeep():
    return baseApi.Enum_Order_MarketOptionKeep()

def Enum_GFD():
    return baseApi.Enum_GFD()

def Enum_GTC():
    return baseApi.Enum_GTC()

def Enum_GTD():
    return baseApi.Enum_GTD()

def Enum_IOC():
    return baseApi.Enum_IOC()

def Enum_FOK():
    return baseApi.Enum_FOK()

def Enum_Speculate():
    return baseApi.Enum_Speculate()

def Enum_Hedge():
    return baseApi.Enum_Hedge()

def Enum_Spread():
    return baseApi.Enum_Spread()

def Enum_Market():
    return baseApi.Enum_Market()

def Enum_Data_Close():
    return baseApi.Enum_Data_Close()

def Enum_Data_Open():
    return baseApi.Enum_Data_Open()

def Enum_Data_High():
    return baseApi.Enum_Data_High()

def Enum_Data_Low():
    return baseApi.Enum_Data_Low()

def Enum_Data_Median():
    return baseApi.Enum_Data_Median()

def Enum_Data_Typical():
    return baseApi.Enum_Data_Typical()

def Enum_Data_Weighted():
    return baseApi.Enum_Data_Weighted()

def Enum_Data_Vol():
    return baseApi.Enum_Data_Vol()

def Enum_Data_Opi():
    return baseApi.Enum_Data_Opi()

def Enum_Data_Time():
    return baseApi.Enum_Data_Time()

# 设置函数
def GetConfig():
    return baseApi.GetConfig()

# def SetBenchmark(*contractNo):
#     return baseApi.SetBenchmark(contractNo)

# def AddUserNo(userNo):
#     return baseApi.AddUserNo(userNo)

def SetBarInterval(contractNo, barType, barInterval, barCount=2000):
    return baseApi.SetBarInterval(contractNo, barType, barInterval, barCount)

# def SetSample(sampleType='C', sampleValue=2000):
#     return baseApi.SetSample(sampleType, sampleValue)

def SetInitCapital(capital='', userNo=''):
    return baseApi.SetInitCapital(capital, userNo)

def SetMargin(type, value=0, contractNo=''):
    return baseApi.SetMargin(type, value, contractNo)

def SetTradeFee(type, feeType, feeValue, contractNo=''):
    return baseApi.SetTradeFee(type, feeType, feeValue, contractNo)

# def SetTradeMode(inActual, useSample, useReal):
# #     return baseApi.SetTradeMode(inActual, useSample, useReal)

def SetActual():
    return baseApi.SetActual()

def SetOrderWay(type):
    return baseApi.SetOrderWay(type)

def SetTradeDirection(tradeDirection):
    return baseApi.SetTradeDirection(tradeDirection)

def SetMinTradeQuantity(tradeQty=1):
    return baseApi.SetMinTradeQuantity(tradeQty)

def SetHedge(hedge, contractNo=''):
    return baseApi.SetHedge(hedge, contractNo)

def SetSlippage(slippage):
    return baseApi.SetSlippage(slippage)

def SetTriggerCont(*contractNo):
    return baseApi.SetTriggerCont(contractNo)

# def SetTriggerType(contNo, type, value=None):
#     return baseApi.SetTriggerType(contNo, type, value)

def SetTriggerType(type, value=None):
    return baseApi.SetTriggerType(type, value)

# 属性函数
def BarInterval(contractNo=''):
    return baseApi.BarInterval(contractNo)

def BarType(contractNo=''):
    return baseApi.BarType(contractNo)

def BidAskSize(contractNo=''):
    return baseApi.BidAskSize(contractNo)

def CanTrade(contractNo=''):
    return baseApi.CanTrade(contractNo)

def ContractUnit(contractNo=''):
    return baseApi.ContractUnit(contractNo)

def ExchangeName(contractNo=''):
    return baseApi.ExchangeName(contractNo)

def ExpiredDate(contractNo=''):
    return baseApi.ExpiredDate(contractNo)

def GetSessionCount(contractNo=''):
    return baseApi.GetSessionCount(contractNo)

def GetSessionEndTime(contractNo='', index=0):
    return baseApi.GetSessionEndTime(contractNo, index)

def GetSessionStartTime(contractNo='', index=0):
    return baseApi.GetSessionStartTime(contractNo, index)

def GetNextTimeInfo(contractNo, timeStr):
    return baseApi.GetNextTimeInfo(contractNo, timeStr)

def MarginRatio(contractNo=''):
    return baseApi.MarginRatio(contractNo)

def MaxBarsBack():
    return baseApi.MaxBarsBack()

def MaxSingleTradeSize():
    return baseApi.MaxSingleTradeSize()

def PriceTick(contractNo=''):
    return baseApi.PriceTick(contractNo)

def OptionStyle(contractNo=''):
    return baseApi.OptionStyle(contractNo)

def OptionType(contractNo=''):
    return baseApi.OptionType(contractNo)

def PriceScale(contractNo=''):
    return baseApi.PriceScale(contractNo)

def RelativeSymbol():
    return baseApi.RelativeSymbol()

def StrikePrice():
    return baseApi.StrikePrice()

def Symbol():
    return baseApi.Symbol()

def SymbolName(contractNo=''):
    return baseApi.SymbolName(contractNo)

def SymbolType(contractNo=''):
    return baseApi.SymbolType(contractNo)

#其他函数
def PlotNumeric(name, value, color=0xdd0000, main=True, axis=False, type=1, barsback=0):
    return baseApi.PlotNumeric(name, value, color, main, axis, type, barsback)
    
def PlotIcon(value, icon=0, color=0xdd0000, main=False, barsback=0):
    return baseApi.PlotIcon(value, icon, color, main, barsback) 
    
def PlotText(value, text, color=0x999999, main=False, barsback=0):
    return baseApi.PlotText(value, text, color, main, barsback) 
    
def PlotVertLine(color=0xdd0000, main=False, axis=False, barsback=0):
    return baseApi.PlotVertLine(color, main, axis, barsback) 
    
def UnPlotText(main=False, barsback=0):
    return baseApi.UnPlotText(main, barsback) 

def LogDebug(*args):
    return baseApi.LogDebug(args)

def LogInfo(*args):
    return baseApi.LogInfo(args)

def LogWarn(*args):
    return baseApi.LogWarn(args)

def LogError(*args):
    return baseApi.LogError(args)

