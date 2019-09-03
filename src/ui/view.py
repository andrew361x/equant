import ctypes

from tkinter import *
from utils.utils import *
from .language import Language
from .editor_view import QuantEditor,QuantEditorHead
from .helper_view import QuantHelper,QuantHelperHead, QuantHelperText
from .monitor_view import QuantMonitor
from .run_view import RunWin

from report.reportview import ReportView
from .com_view import HistoryToplevel

from datetime import datetime


class QuantApplication(object):
    '''主界面'''
    def __init__(self, top, control):
        self.root = top
        self.control = control
        self.language = Language("EquantMainFrame")

        self.root.protocol("WM_DELETE_WINDOW", self.quantExit)

        #monitor_text需要跟日志绑定
        self.monitor_text = None
        self.editor_text_frame = None
        self.top_pane_left_up = None
        self.signal_text = None
        
        #窗口类
        self.quant_editor = None
        self.quant_helper = None
        self.quant_editor_head = None
        self.quant_helper_head = None
        self.quant_monitor = None
        # 运行按钮弹出窗口
        self.runWin = None

        # 历史回测窗口
        self.hisTop = None

    def mainloop(self):
        self.root.mainloop()

    def create_window(self):
        myappid = 'mycompany.myproduct.subproduct.version'  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        #srceen size
        width = self.root.winfo_screenwidth()*0.8
        height = self.root.winfo_screenheight()*0.8
        
        #window location
        self.root.geometry('%dx%d+%d+%d' % (width, height, width*0.1, height*0.1))
        #title
        self.root.title("极星量化")
        icon = r'./icon/epolestar ix2.ico'

        self.root.iconbitmap(bitmap=icon)
        self.root.bitmap = icon
        top_frame = Frame(self.root)
        top_frame.pack(fill=BOTH, expand=YES)

        # 创建主窗口,分为左右两个窗口，大小由子控件决定
        top_pane = PanedWindow(top_frame, orient=HORIZONTAL, sashrelief=GROOVE, sashwidth=1.5,
                               showhandle=False, opaqueresize=True)
        top_pane.pack(fill=BOTH, expand=YES)
        
        # 左窗口分上下窗口
        top_pane_left = PanedWindow(top_pane, orient=VERTICAL, sashrelief=GROOVE,
                                    sashwidth=1.5, opaqueresize=True, showhandle=False)
        # 右窗口，分上下窗口
        top_pane_right = PanedWindow(top_pane, orient=VERTICAL, sashrelief=GROOVE,
                                     sashwidth=1.5, opaqueresize=True, showhandle=False)

        top_pane.add(top_pane_left, stretch='always')
        top_pane.add(top_pane_right)
        

        # 左窗口分为上下两部分，右窗口分为上下两部分
        
        left_up_frame = Frame(top_pane_left, bg=rgb_to_hex(255, 255, 255), height=height*3/4, width=width*4/5)  # 左上
        left_down_frame = Frame(top_pane_left, bg=rgb_to_hex(255, 255, 255), height=height*1/4, width=width*4/5)  # 左下
        right_up_frame = Frame(top_pane_right, bg=rgb_to_hex(255, 255, 255), height=height*3/4, width=width*1/5)  # 右上
        right_down_frame = Frame(top_pane_right, bg=rgb_to_hex(255, 255, 255), height=height*1/4, width=width*1/5)  # 右下

        top_pane_left.add(left_up_frame, stretch='always')
        top_pane_left.add(left_down_frame, stretch='always')
        top_pane_right.add(right_up_frame, stretch='always')
        top_pane_right.add(right_down_frame, stretch='always')
        

        # 策略标题
        self.quant_editor_head = QuantEditorHead(left_up_frame, self.control,self.language)
        #策略树和编辑框
        self.quant_editor = QuantEditor(left_up_frame, self.control, self.language)
        #创建策略树
        self.quant_editor.create_tree()
        #创建策略编辑器
        self.quant_editor.create_editor()
        #api函数标题
        self.quant_helper_head = QuantHelperHead(right_up_frame, self.control, self.language)
        #系统函数列表
        self.quant_helper = QuantHelper(right_up_frame, self.control, self.language)
        self.quant_helper.create_list()
       
        #系统函数说明
        self.quant_helper_text = QuantHelperText(right_down_frame, self.control, self.language)
        self.quant_helper_text.create_text()
        
        # 监控窗口
        self.quant_monitor = QuantMonitor(left_down_frame, self.control, self.language)
        # self.quant_monitor.createSysLog()
        self.quant_monitor.createExecute()
        # self.create_monitor()
        # self.quant_monitor.createSignal()
        self.quant_monitor.createLog()
        self.quant_monitor.createErr()
        self.quant_monitor.createPos()

    def updateLogText(self):
        self.quant_monitor.updateLogText()
        
    def set_help_text(self, funcName, text):
        self.quant_helper_text.insert_text(funcName, text)

    def updateStrategyTree(self, path):
        # self.quant_editor.update_all_tree()
        self.quant_editor.update_tree(path)

    def updateEditorHead(self, text):
        self.quant_editor.updateEditorHead(text)

    def updateEditorText(self, text):
        self.quant_editor.updateEditorText(text)

    def updateEditorModifyTime(self, time):
        self.quant_editor.setModifyTime(time)

    # def updateExecuteList(self, executeList):
    #     self.quant_monitor.updateExecuteList(executeList)
        
    def addExecute(self, dataDict):
        self.quant_monitor.addExecute(dataDict)

    def sortStrategyExecute(self):
        self.quant_monitor.sortStrategyExecute()

    def createRunWin(self, param, path, flag):
        """弹出量化设置界面"""

        self.setLoadState("disabled")
        self.runWin = RunWin(self.control, path, flag, self.root, param)
        self.runWin.display()
        self.setLoadState("normal")

    def setLoadState(self, state):
        self.quant_editor.setLoadBtnState(state)

    def quantExit(self):
        """量化界面关闭处理"""
        # 向引擎发送主进程退出信号
        if messagebox.askokcancel("关闭?", "确定退出么?\n请确认保存当前的内容"):
            self.control.sendExitRequest()

            # 退出子线程和主线程
            self.control.quitThread()

    def autoExit(self):
        """量化终端自动退出"""
        self.control.sendExitRequest()
        self.control.quitThread()

    def reportDisplay(self, data, id):
        """
        显示回测报告
        :param data: 回测报告数据
        :param id:  对应策略Id
        :return:
        """
        stManager = self.control.getStManager()
        strategyPath = self.control.getEditorText()["path"]

        stName = os.path.basename(strategyPath)

        stData = stManager.getSingleStrategy(id)
        # runMode = stData["Config"]["RunMode"]["Actual"]["SendOrder2Actual"]
        runMode = stData["Config"]["RunMode"]["SendOrder2Actual"]
        # 保存报告数据
        save(data, runMode, stName)

        self.hisTop = HistoryToplevel(self, self.root)

        ReportView(data, self.hisTop)

        # def test():
        #     #TODO: 增加matplotlib.pyplot.close()
        #     # a.dire.detail_frame.fund.canvas.destroy()
        #     # a.dire.detail_frame.graph.canvas.destroy()
        #     self.hisTop.destroy()
        #
        # self.hisTop.protocol("WM_DELETE_WINDOW", test)
        self.hisTop.display_()

    def updateRunStage(self, strategyId, status):
        """
        更新策略运行阶段
        :param strategyId: 策略Id
        :param dataDict: strategeId对应的策略状态信息
        :return:
        """
        self.quant_monitor.updateRunStage(strategyId, status)

    def updateRunMode(self, strategyId, status):
        """
        更新策略运行状态
        :param strategy:
        :param status:
        :return:
        """
        self.quant_monitor.updateRunMode(strategyId, status)

    def updateValue(self, strategyId, values):
        """
        更新策略的运行数据
        :param strategyId: 策略id
        :param values: 策略的运行数据
        :return:
        """
        self.quant_monitor.updateValue(strategyId, values)

    def delUIStrategy(self, strategyId):
        """
        删除监控列表中的策略
        :param strategyIdList: 待删除的策略列表
        :return:
        """
        self.quant_monitor.deleteStrategy(strategyId)

    def setConnect(self, src):

        if src == 'Q':
            self.quant_editor_head.stateLabel.config(text="即时行情连接成功", fg="black")
        if src == 'H':
            self.quant_editor_head.stateLabel.config(text="历史行情连接成功", fg="black")

        if src == 'T':
            self.quant_editor_head.stateLabel.config(text="交易服务连接成功", fg="black")

        if src == 'S':
            self.quant_editor_head.stateLabel.config(text="极星9.5连接成功", fg="black")

    def setDisconnect(self, src):
        if src == 'Q':
            self.quant_editor_head.stateLabel.config(text="即时行情断连", fg="red")
        if src == 'H':
            self.quant_editor_head.stateLabel.config(text="历史行情断连", fg="red")

        if src == 'T':
            self.quant_editor_head.stateLabel.config(text="交易服务断连", fg="red")

        if src == 'S':
            self.quant_editor_head.stateLabel.config(text="极星9.5退出", fg="red")
            messagebox.showerror("错误", "极星9.5退出", parent=self.root)

    def clearError(self):
        """清除错误信息"""
        self.quant_monitor.clearErrorText("")

    def updateSyncPosition(self, positions):
        """更新组合监控持仓信息"""
        self.quant_monitor.updatePos(positions)
