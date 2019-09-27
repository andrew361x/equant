import talib

userNo = 'Q912526205'
#contNo = 'NYMEX|F|CL|1910'
contNo = 'NYMEX|O|CL|1911C5200'
#contNo = 'ZCE|O|CF|001C16400'
#contNo = 'SHFE|F|CU|1910'
cFlag = 'A'

def initialize(context): 
    #SetUserNo('Q912526205')
    SetBarInterval(contNo , 'M', 1, 200)

def handle_data(context):
    #LogInfo("AAA:%f, %f, %f, %f, %f, %f, %f" %(Q_TheoryPrice(), Q_Sigma(), Q_Delta(), Q_Gamma(), Q_Vega(), Q_Theta(), Q_Rho()))
    LogInfo("AAA: " , Q_TheoryPrice(), Q_Sigma(), Q_Delta(), Q_Gamma(), Q_Vega(), Q_Theta(), Q_Rho())


def exit_callback(context):
    pass
