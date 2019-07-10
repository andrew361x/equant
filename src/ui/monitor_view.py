import os
import traceback

from tkinter import *
from tkinter import ttk, messagebox, Frame
from utils.utils import *
from .language import Language
from .com_view import QuantFrame, QuantToplevel
from .editor import MonitorText, SignalText, ErrorText
from .menu import RunMenu
from capi.com_types import *
from report.fieldConfigure import StrategyStatus, FrequencyDict


class QuantMonitor(object):

    # 背景色
    bgColor = rgb_to_hex(245, 245, 245)
    bgColorW = "white"

    def __init__(self, frame, control, language):
        self.parentFrame = frame
        self._controller = control
        self._logger = self._controller.get_logger()
        self.language = language

        # Monitor不同标签的背景色
        self.rColor = self.bgColorW
        self.lColor = self.bgColor
        self.sColor = self.bgColor
        self.eColor = self.bgColor
        self.pColor = self.bgColor

        self.createButtonFrame()

        # 执行列表、监控日志、信号记录、错误
        self.executeList  = Frame(self.parentFrame)
        self.monitorLog   = Frame(self.parentFrame)
        self.sigRecord    = Frame(self.parentFrame)
        self.errRecord    = Frame(self.parentFrame)
        self.posMonitor   = Frame(self.parentFrame)

        self.executeList.pack(side=TOP, fill=BOTH, expand=YES)

        self.monText = None
        self.sigText = None
        self.errText = None

    def createButtonFrame(self):
        btnFrame = Frame(self.parentFrame, height=30, bg=self.bgColor)
        btnFrame.pack_propagate(0)
        btnFrame.pack(side=TOP, fill=X)
        # 利用frame做出button的黑色边框
        # f1 = Frame(btnFrame, highlightbackground="black", highlightthickness=1, bd=0)
        # f1.pack(side=LEFT)

        self.runBtn = Button(btnFrame, text="策略运行", relief=FLAT, padx=14, pady=1.5, bg=self.rColor,
                             bd=0, highlightthickness=1, command=self.toMonFrame)
        self.logBtn = Button(btnFrame, text="运行日志", relief=FLAT, padx=14, pady=1.5, bg=self.lColor,
                             bd=0, highlightthickness=1,
                             command=self.toLogFrame)
        self.sigBtn = Button(btnFrame, text="信号记录", relief=FLAT, padx=14, pady=1.5, bg=self.sColor,
                             bd=0, highlightthickness=1,  command=self.toSigFrame)
        self.errBtn = Button(btnFrame, text="错误信息", relief=FLAT, padx=14, pady=1.5, bg=self.eColor,
                             bd=0, highlightthickness=1, command=self.toErrFrame)

        self.posBtn = Button(btnFrame, text="组合监控", relief=FLAT, padx=14, pady=1.5, bg=self.pColor,
                             bd=0, highlightthickness=1, command=self.toPosFrame)
        self.runBtn.pack(side=LEFT, expand=NO)
        self.logBtn.pack(side=LEFT, expand=NO)
        self.sigBtn.pack(side=LEFT, expand=NO)
        self.errBtn.pack(side=LEFT, expand=NO)
        self.posBtn.pack(side=LEFT, expand=NO)

        for btn in (self.runBtn, self.logBtn, self.sigBtn, self.errBtn, self.posBtn):
            btn.bind("<Enter>", self.handlerAdaptor(self.onEnter, button=btn))
            btn.bind("<Leave>", self.handlerAdaptor(self.onLeave, button=btn))

    def createMonitor(self):
        # monitorRightBar = Scrollbar(self.monitorLog)
        # monitorRightBar.pack(side=RIGHT, fill=Y), yscrollcommand=monitorRightBar.set

        self.monText = MonitorText(self.monitorLog, height=20, bd=0)
        self.monText.createScrollbar()
        self.monText.pack(fill=BOTH, expand=YES)

    def createSignal(self):
        self.sigText = SignalText(self.sigRecord, height=20, bd=0)
        self.sigText.createScrollbar()
        self.sigText.pack(fill=BOTH, expand=YES)

    def createPos(self):
        headList = ["账号", "合约", "账户仓", "策略仓", "仓差", "策略多", "策略空", "账户多", "账户空"]
        widthList = [10, 10, 10, 10, 10, 10, 10, 10, 10]

        funcFrame = Frame(self.posMonitor, relief=RAISED, bg=rgb_to_hex(245, 245, 245), height=25)
        funcFrame.pack(side=TOP, fill=X, expand=YES, padx=1, pady=2)
        treeFrame = Frame(self.posMonitor, relief=RAISED, bg=rgb_to_hex(245, 245, 245))
        treeFrame.pack(side=TOP, fill=X, expand=YES, padx=1, pady=2)
        self.posTree = ttk.Treeview(treeFrame, show="headings", height=28, columns=headList)
        self.posTree.pack(fill=BOTH, expand=YES, padx=5)

        for key, w in zip(headList, widthList):
            self.posTree.column(key, width=w, anchor=W)
            self.posTree.heading(key, text=key, anchor=W)

        self.createPosFunc(funcFrame)

    def createPosFunc(self, frame):
        cbV    = StringVar()
        sbV    = IntVar()
        timeV  = IntVar()

        cbV.set("对盘价")
        sbV.set(0)
        timeV.set(5000)

        # buttonborder = Frame(frame, highlightbackground="lightblue", highlightthickness=2, bd=0)
        # buttonborder.pack(side=LEFT, padx=2)

        synBtn = Button(frame, text="持仓一键同步", relief=FLAT, activebackground="lightblue",
                        overrelief="groove",
                        bg=rgb_to_hex(230, 230, 230))
        synBtn.pack(side=LEFT, padx=2)

        Label(frame, text="同步设置：", bg=rgb_to_hex(245, 245, 245), justify=LEFT, anchor=W, width=8).pack(side=LEFT)

        cbValues = ["对盘价", "最新价", "市价"]

        cb = ttk.Combobox(frame, values=cbValues, width=11, textvariable=cbV, state="readonly")
        cb.pack(side=LEFT, padx=2)

        Label(frame, text="+", bg=rgb_to_hex(245, 245, 245), justify=LEFT, anchor=W, width=1).pack(side=LEFT)

        sb = ttk.Spinbox(frame, values=list(range(0, 101, 1)), width=4, textvariable=sbV)
        sb.pack(side=LEFT, padx=2)

        Label(frame, text="跳", bg=rgb_to_hex(245, 245, 245), justify=LEFT, anchor=W, width=2).pack(side=LEFT)

        disCheck = Checkbutton(frame, text="间隔", bg=rgb_to_hex(245, 245, 245), width=10, bd=1, anchor=E)
        disCheck.pack(side=LEFT, padx=2)

        timeEntry = Entry(frame, relief=GROOVE, bd=2, width=5, textvariable=timeV)
        timeEntry.pack(side=LEFT)

        Label(frame, text="毫秒自动同步", bg=rgb_to_hex(245, 245, 245), justify=LEFT, anchor=W, width=12)\
            .pack(side=LEFT, padx=2)

        subCheck = Checkbutton(frame, text="仅自动减仓", bg=rgb_to_hex(245, 245, 245), bd=1, anchor=W)
        subCheck.pack(side=LEFT, padx=5)

        pass

    def createExecute(self):
        headList  = ["编号", "账号", "策略名称", "基准合约", "频率", "运行状态", "实盘运行",
                    "初始资金", "可用资金", "最大回撤", "累计收益", "胜率"]
        widthList = [5, 50, 50, 50, 5, 10, 5, 20, 10, 20, 20, 5]

        self.executeBar = ttk.Scrollbar(self.executeList, orient="vertical")
        self.executeBar.pack(side=RIGHT, fill=Y)

        self.executeListTree = ttk.Treeview(self.executeList, show="headings", height=28, columns=tuple(headList),
                                            yscrollcommand=self.executeBar.set, style="Filter.Treeview")
        self.executeBar.config(command=self.executeListTree.yview)
        self.executeListTree.pack(fill=BOTH, expand=YES)

        self.executeListTree.bind("<Button-3>", self.createMenu)

        for key, w in zip(headList, widthList):
            self.executeListTree.column(key, width=w, anchor=CENTER)
            self.executeListTree.heading(key, text=key)

    def createMenu(self, event):
        """创建运行策略右键菜单"""
        RunMenu(self._controller, self.executeListTree).popupmenu(event)

    def _formatMonitorInfo(self, dataDict):
        """
        格式化监控需要的信息
        :param dataDict: 策略的所有信息
        :return: 需要展示的信息
        """
        try:
            Id = dataDict['StrategyId']
            UserNo = dataDict["Config"]["Money"]["UserNo"]
            StName = dataDict['StrategyName']
            BenchCon = dataDict['ContractNo']
            kLineType = dataDict['KLineType']
            kLineSlice = dataDict['KLinceSlice']

            Frequency = str(kLineSlice) + kLineType

            RunType = "是" if dataDict['IsActualRun'] else "否"
            Status = StrategyStatus[dataDict["StrategyState"]]
            InitFund = dataDict['InitialFund']

            if 'RunningData' in dataDict:
                # Available =  "{:.2f}".format(dataDict['RunningData']['Fund'][-1]['Available'])
                Available = "{:.2f}".format(dataDict['RunningData']['Available'])
                # 年化单利收益率
                # AnnualizedReturns = "{:.2f}".format(dataDict['RunningData']['Detail']['AnnualizedSimple'])
                MaxRetrace = "{:.2f}".format((dataDict['RunningData']['MaxRetrace']))
                TotalProfit = "{:.2f}".format(dataDict['RunningData']['NetProfit'])
                WinRate = "{:.2f}".format(dataDict['RunningData']['WinRate'])
            else:
                Available = InitFund
                MaxRetrace = 0
                TotalProfit = 0
                WinRate = 0

        except KeyError:
            traceback.print_exc()
            return {}

        values = [
            Id,
            UserNo,
            StName,
            BenchCon,
            Frequency,
            Status,
            RunType,
            InitFund,
            Available,
            MaxRetrace,
            TotalProfit,
            WinRate
        ]

        return values

    def updateSingleExecute(self, dataDict):
        values = self._formatMonitorInfo(dataDict)

        if not values:
            return

        strategyId = dataDict["StrategyId"]
        try:
            if self.executeListTree.exists(strategyId):
                self.updateStatus(strategyId, dataDict)
                return
        except Exception as e:
            self._logger.warn("updateSingleExecute exception")
        self.executeListTree.insert("", END, iid=strategyId, values=tuple(values), tag=0)

    def createErr(self):
        # 错误信息展示
        self.errText = ErrorText(self.errRecord, height=20, bd=0)
        self.errText.createScrollbar()
        self.errText.pack(fill=BOTH, expand=YES)

    def updateLogText(self):
        guiQueue = self._controller.get_logger().getGuiQ()
        data = ""
        flag = True
        try:
            # data = guiQueue.get_nowait()
            while flag:
                data += guiQueue.get_nowait()+"\n"
                if guiQueue.empty():
                    flag = False
        except:
            return
        else:
            self.monText.setText(data)

    def updateSigText(self):
        sigQueue = self._controller.get_logger().getSigQ()
        sigData = ''
        flag = True
        try:
            # sigData = sigQueue.get_nowait()
            while flag:
                sigData += sigQueue.get_nowait()+"\n"
                if sigQueue.empty():
                    flag = False

        except Exception as e:
            return
        else:
            # self.toSigFrame()
            self.sigText.setText(sigData)

    def updateErrText(self):
        errQueue = self._controller.get_logger().getErrQ()
        try:
            errData = errQueue.get_nowait()
        except:
            return
        else:
            self.toErrFrame()
            self.errText.setText(errData)

    def clearErrorText(self):
        self.errText.setText("")

    def toMonFrame(self):
        self.runBtn.config(bg="white")
        self.rColor = self.runBtn['bg']
        self.lColor = self.bgColor
        self.sColor = self.bgColor
        self.eColor = self.bgColor
        self.pColor = self.bgColor
        self.errBtn.config(bg=self.rColor)
        self.sigBtn.config(bg=self.sColor)
        self.logBtn.config(bg=self.lColor)
        self.posBtn.config(bg=self.pColor)
        self.monitorLog.pack_forget()
        self.sigRecord.pack_forget()
        self.errRecord.pack_forget()
        self.posMonitor.pack_forget()
        self.executeList.pack(side=TOP, fill=BOTH, expand=YES)

    def toLogFrame(self):
        self.logBtn.config(bg="white")
        self.lColor = self.logBtn['bg']
        self.rColor = self.bgColor
        self.sColor = self.bgColor
        self.eColor = self.bgColor
        self.pColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.sigBtn.config(bg=self.sColor)
        self.errBtn.config(bg=self.eColor)
        self.posBtn.config(bg=self.pColor)
        self.sigRecord.pack_forget()
        self.executeList.pack_forget()
        self.errRecord.pack_forget()
        self.posMonitor.pack_forget()
        self.monitorLog.pack(side=TOP, fill=BOTH, expand=YES)

    def toSigFrame(self):
        self.sigBtn.config(bg="white")
        self.sColor = self.sigBtn['bg']
        self.lColor = self.bgColor
        self.rColor = self.bgColor
        self.eColor = self.bgColor
        self.pColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.logBtn.config(bg=self.lColor)
        self.errBtn.config(bg=self.eColor)
        self.posBtn.config(bg=self.pColor)
        self.monitorLog.pack_forget()
        self.executeList.pack_forget()
        self.errRecord.pack_forget()
        self.posMonitor.pack_forget()
        self.sigRecord.pack(side=TOP, fill=BOTH, expand=YES)

    def toErrFrame(self):
        self.errBtn.config(bg="white")
        self.eColor = self.errBtn['bg']
        self.lColor = self.bgColor
        self.rColor = self.bgColor
        self.sColor = self.bgColor
        self.pColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.sigBtn.config(bg=self.sColor)
        self.logBtn.config(bg=self.lColor)
        self.posBtn.config(bg=self.pColor)
        self.parentFrame.update()
        self.monitorLog.pack_forget()
        self.executeList.pack_forget()
        self.sigRecord.pack_forget()
        self.posMonitor.pack_forget()
        self.errRecord.pack(side=TOP, fill=BOTH, expand=YES)

    def toPosFrame(self):
        self.posBtn.config(bg="white")
        self.pColor = self.posBtn['bg']
        self.lColor = self.bgColor
        self.rColor = self.bgColor
        self.sColor = self.bgColor
        self.eColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.sigBtn.config(bg=self.sColor)
        self.logBtn.config(bg=self.lColor)
        self.errBtn.config(bg=self.eColor)
        self.parentFrame.update()
        self.monitorLog.pack_forget()
        self.executeList.pack_forget()
        self.sigRecord.pack_forget()
        self.errRecord.pack_forget()
        self.posMonitor.pack(side=TOP, fill=BOTH, expand=YES)

    def handlerAdaptor(self, fun, **kwargs):
        return lambda event, fun=fun, kwargs=kwargs: fun(event, **kwargs)

    def onEnter(self, event, button):
        if button == self.runBtn:
            button.config(bg='white')
            self.logBtn.config(bg=self.bgColor)
            self.sigBtn.config(bg=self.bgColor)
            self.errBtn.config(bg=self.bgColor)
            self.posBtn.config(bg=self.bgColor)
        elif button == self.logBtn:
            button.config(bg='white')
            self.runBtn.config(bg=self.bgColor)
            self.sigBtn.config(bg=self.bgColor)
            self.errBtn.config(bg=self.bgColor)
            self.posBtn.config(bg=self.bgColor)
        elif button == self.sigBtn:
            button.config(bg='white')
            self.runBtn.config(bg=self.bgColor)
            self.logBtn.config(bg=self.bgColor)
            self.errBtn.config(bg=self.bgColor)
            self.posBtn.config(bg=self.bgColor)
        elif button == self.errBtn:
            button.config(bg='white')
            self.runBtn.config(bg=self.bgColor)
            self.logBtn.config(bg=self.bgColor)
            self.sigBtn.config(bg=self.bgColor)
            self.posBtn.config(bg=self.bgColor)
        else:
            button.config(bg='white')
            self.runBtn.config(bg=self.bgColor)
            self.logBtn.config(bg=self.bgColor)
            self.sigBtn.config(bg=self.bgColor)
            self.errBtn.config(bg=self.bgColor)

    def onLeave(self, event, button):
        button.config(bg=rgb_to_hex(227, 230, 233))
        if button == self.runBtn:
            button['bg'] = self.rColor
            self.logBtn['bg'] = self.lColor
            self.sigBtn['bg'] = self.sColor
            self.errBtn['bg'] = self.eColor
            self.posBtn['bg'] = self.pColor
        elif button == self.logBtn:
            button['bg'] = self.lColor
            self.runBtn['bg'] = self.rColor
            self.sigBtn['bg'] = self.sColor
            self.errBtn['bg'] = self.eColor
            self.posBtn['bg'] = self.pColor
        elif button == self.sigBtn:
            button['bg'] = self.sColor
            self.runBtn['bg'] = self.rColor
            self.logBtn['bg'] = self.lColor
            self.errBtn['bg'] = self.eColor
            self.posBtn['bg'] = self.pColor
        elif button == self.errBtn:
            button['bg'] = self.eColor
            self.runBtn['bg'] = self.rColor
            self.logBtn['bg'] = self.lColor
            self.sigBtn['bg'] = self.sColor
            self.posBtn['bg'] = self.pColor
        else:
            button['bg'] = self.pColor
            self.runBtn['bg'] = self.rColor
            self.logBtn['bg'] = self.lColor
            self.sigBtn['bg'] = self.sColor
            self.errBtn['bg'] = self.eColor

    def deleteStrategy(self, strategyId):
        """删除策略"""
        self.executeListTree.delete(strategyId)

    def updateStatus(self, strategyId, dataDict):
        """更新策略ID对应的策略状态"""
        if len(dataDict) < 4:
            return

        values = self._formatMonitorInfo(dataDict)
        if not values:
            return
        self.executeListTree.item(strategyId, values=values)
