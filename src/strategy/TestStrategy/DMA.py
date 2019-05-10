#-*-coding:utf-8
import talib

def initialize(context):
    SetBenchmark("NYMEX|F|CL|1906","NYMEX|F|CL|1907","NYMEX|F|CL|1908")
    SetBarInterval('M',1)
    #SetSample('D','20190429')
    SetUserNo("ET001")


def handle_data(context):
    ma_1906_5 = talib.MA(Close("NYMEX|F|CL|1906"), timeperiod=5)
    ma_1906_20 = talib.MA(Close("NYMEX|F|CL|1906"), timeperiod=20)
    ma_1907_5 = talib.MA(Close("NYMEX|F|CL|1907"), timeperiod=5)
    ma_1907_20 = talib.MA(Close("NYMEX|F|CL|1907"), timeperiod=20)
    ma_1908_5 = talib.MA(Close("NYMEX|F|CL|1908"), timeperiod=5)
    ma_1908_20 = talib.MA(Close("NYMEX|F|CL|1908"), timeperiod=20)
    
    #记录指标
    PlotNumeric('MA_1906_5', ma_1906_5[-1])
    #if len(ma_1906_5)>=5:
        #print("close('NYMEX|F|CL|1906') = ", Close("NYMEX|F|CL|1906")[-5:])
        #print("ma_1906_5 result = ",ma_1906_5[-5:])
    PlotNumeric('MA_1906_20', ma_1906_20[-1], color=0x00aa00)
    PlotNumeric('MA_1907_5', ma_1907_5[-1])
    PlotNumeric('MA_1907_20', ma_1907_20[-1], color=0x00aa00)
    PlotNumeric('MA_1908_5', ma_1908_5[-1])
    PlotNumeric('MA_1908_20', ma_1908_20[-1], color=0x00aa00)
      
    #if ma_1906_5[-1] < (ma_1907_5[-1]+ma_1908_5[-1])/2:
    Buy("NYMEX|F|CL|1906", 1, Open("NYMEX|F|CL|1906")[-1])               # 买平开
    Buy("NYMEX|F|CL|1907", 1, Open("NYMEX|F|CL|1906")[-1])              # 买平开
    #if ma_1906_20[-1] > (ma_1907_20[-1]+ma_1908_20[-1])/2:
    #SellShort(1, Open("NYMEX|F|CL|1906")[-1],"NYMEX|F|CL|1906")         # 卖平开

