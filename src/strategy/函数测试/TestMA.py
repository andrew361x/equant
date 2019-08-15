import talib

contA = 'NYMEX|F|CL|1909'
contB = 'INE|F|SC|1909'

p1 = 5
p2 = 10

def getVn(nr, n):
    return nr[-1] if len(nr) < n else nr[-n]

def initialize(context): 
    SetBarInterval(contA, 'M', 1, '20190701')
    SetBarInterval(contA, 'M', 3, '20190701')
    SetBarInterval(contB, 'M', 1, '20190701')


def handle_data(context):
    ma11 = talib.MA(Close(contA, 'M', 1), p1, 0)
    ma12 = talib.MA(Close(contA, 'M', 1), p2, 0)

    ma31 = talib.MA(Close(contA, 'M', 3), p1, 0)
    ma32 = talib.MA(Close(contA, 'M', 3), p2, 0)

    diff2 = getVn(ma11, 2) - getVn(ma31, 2)    

    PlotNumeric("ma11", ma11[-1], color=RGB_Red())
    PlotNumeric("ma12", ma12[-1], color=RGB_Green())
    PlotNumeric("diff2", diff2, color=RGB_Blue(), main=False)
    
