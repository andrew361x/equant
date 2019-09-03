import talib
import os
import xlrd,xlwt
from xlutils.copy import copy

class MyExcel:
    def __init__(self, path, name):
        self._fullname = path + os.sep + name
        
        if not os.path.exists(self._fullname):
            wt_work = xlwt.Workbook()
            wt_work.add_sheet("Sheet1")
            wt_work.save(self._fullname)
            
    def Write(self, sheet, row, data):
        '''更新写入'''
        if not isinstance(data, list):
            return
        rdxls = xlrd.open_workbook(self._fullname)
        wtxls = copy(rdxls)
        
        if sheet not in rdxls.sheet_names():
            tables = wtxls.add_sheet(sheet)
        else:
            tables = wtxls.get_sheet(sheet)
            
        for i in range(len(data)):
            tables.write(row, i, data[i])
                
        wtxls.save(self._fullname)
        
        
myExcel  = MyExcel('.', 'test.xls')

contList = {
    'NYMEX|F|CL|1909', 'HKEX|F|HSI|1908', 'COMEX|F|GC|1909'
}

def initialize(context): 
    for cont in contList:
        SetBarInterval(cont, 'M', 1, 'N')
        
    head = ['合约', '时间戳', '最新价', '买价', '卖价', '成交量', '买量', '卖量']
    
    for cont in contList:
        myExcel.Write(cont, 0, head)

def handle_data(context):
    cno = context.contractNo()
    quote = [
        cno, 
        Q_UpdateTime(cno),
        Q_Last(cno),
        Q_BidPrice(cno),
        Q_AskPrice(cno),
        Q_TotalVol(cno),
        Q_BidVol(cno),
        Q_AskVol(cno)
    ]
    
    myExcel.Write(cno, 1, quote)
    
