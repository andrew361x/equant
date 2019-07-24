import talib

g_params['Lots'] = 1 #aaa
g_params['AAAA'] = 2 
g_params['BNBB'] = 'CCC'  #####bbbbbb
g_params['dddddd'] = 8.2  #####bbbbbb

def initialize(context):
    SetBarInterval("DCE|F|I|1909", 'M', 1, 1)


def handle_data(context):
    LogInfo("Lots",  g_params)
