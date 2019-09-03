import talib
import xlrd
import xlwt
from xlutils.copy import copy

rd_ex_file = r"D:\main_cont.xlsx"
wt_ex_file = r"D:\cont_sanp.xls"

cont_sheet = 'Sheet1'
snap_sheet = "Sheet1"

#合约列表
g_contList = []

def initialize(context):
    global g_contList
    #设置基准合约
    SetBarInterval("DCE|F|I|1909", 'M', 1, 1)
    #合约表格
    rd_work  = xlrd.open_workbook(rd_ex_file)
    rd_table = rd_work.sheet_by_name(cont_sheet)

    #从合约表格中读取合约进行配置    
    for i in range(rd_table.nrows):
        #跳过表头
        if i == 0:continue
        rows = rd_table.row_values(i)
        #月份如果为浮点数，转换为字符
        rows[3] = str(int(rows[3]))
        #月份保持最少3位，郑商所品种存在001，excel表中是1
        rows[3] = rows[3].zfill(3)
        #拼接为合约格式'ZCE|F|SR|909'
        cont = '|'.join(rows)
        g_contList.append(cont)
        #订阅即时行情
        SubQuote(cont)

    #行情表格
    wt_work  = xlwt.Workbook()
    wt_table = wt_work.add_sheet(snap_sheet)
    table_head = ['合约', '时间戳', '最新价', '买价', '卖价', '成交量', '买量', '卖量']
    for i in range(len(table_head)):
        wt_table.write(0, i, table_head[i])
    
    wt_work.save(wt_ex_file)

def handle_data(context):
    global g_contList

    #跳过回测阶段
    if context.triggerType() == 'H':
        return
    #追加写入excel表
    r_xls = xlrd.open_workbook(wt_ex_file) # 读取excel文件
    row = r_xls.sheets()[0].nrows # 获取已有的行数
    excel = copy(r_xls) # 将xlrd的对象转化为xlwt的对象
    wt_table = excel.get_sheet(0) # 获取要操作的sheet
    
    #保存合约号、最新价、成交量、买卖价、买卖量到excel表格中
    for cont in g_contList:
        LogInfo(cont)
        wt_table.write(row, 0, cont)
        wt_table.write(row, 1, Q_UpdateTime(cont))
        wt_table.write(row, 2, Q_Last(cont))
        wt_table.write(row, 3, Q_BidPrice(cont))
        wt_table.write(row, 4, Q_AskPrice(cont))
        wt_table.write(row, 5, Q_TotalVol(cont))
        wt_table.write(row, 6, Q_BidVol(cont))
        wt_table.write(row, 7, Q_AskVol(cont))
        row += 1
    excel.save(wt_ex_file)
