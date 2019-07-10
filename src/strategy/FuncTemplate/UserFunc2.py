import talib


class UserModel:
    def __init__(self):
        pass
    
    def getCurTime(self, contNo):
        dateTime = Date(contNo, 'M', 1) + Time(contNo, 'M', 1)
        return dateTime
