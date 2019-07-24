import talib
import numpy as np

class ATR:
    def __init__(self):
        self.value = []
        self.atrv = []

    def mean(self, v, n):
        self.value.append(v)
        length = len(self.value)
        if length < n:
            self.atrv.append(np.nan)
        else:
            nav = np.array(self.value[length-n:])
            mean = nav.sum()/n
            self.atrv.append(mean)
        return self.atrv
            
atr = ATR()

def initialize(context): 
    SetBarInterval("DCE|F|I|1909", 'M', 1, 2000)


def handle_data(context):
    mean = atr.mean(Vol()[-1], 100)
    LogInfo("VVVV", Date(), Time(), Vol()[-1], mean[-1])
    PlotNumeric("ATR", mean[-1], main=False)
