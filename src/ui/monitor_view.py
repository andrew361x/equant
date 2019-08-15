import os
import traceback

from tkinter import *
from tkinter import ttk, messagebox, Frame
from utils.utils import *

from .editor import MonitorText, LogText, ErrorText
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
        self.eColor = self.bgColor
        self.pColor = self.bgColor
        # 日志不同标签背景色
        self.yColor = self.bgColor   # 系统日志标签颜色
        self.sColor = self.bgColor
        self.uColor = self.bgColorW

        self.createButtonFrame()

        # 执行列表、监控日志、信号记录、错误
        self.executeList  = Frame(self.parentFrame)
        self.errRecord    = Frame(self.parentFrame)
        self.posMonitor   = Frame(self.parentFrame)
        self.logRecord    = Frame(self.parentFrame)

        self.sysLog       = Frame(self.logRecord)
        self.sigRecord    = Frame(self.logRecord)
        self.usrLog       = Frame(self.logRecord)

        self.executeList.pack(side=TOP, fill=BOTH, expand=YES)

        self.sysText = None
        self.sigText = None
        self.usrText = None
        self.errText = None

        # 日志功能区
        self.createLogBtnFrame()
        self.usrLog.pack(side=TOP, fill=BOTH, expand=YES)

    def createButtonFrame(self):
        btnFrame = Frame(self.parentFrame, height=30, bg=self.bgColor)
        btnFrame.pack_propagate(0)
        btnFrame.pack(side=TOP, fill=X)

        self.runBtn = Button(btnFrame, text="策略运行", relief=FLAT, padx=14, pady=1.5, bg=self.rColor,
                             bd=0, highlightthickness=1, command=self.toMonFrame)
        self.logBtn = Button(btnFrame, text="运行日志", relief=FLAT, padx=14, pady=1.5, bg=self.lColor,
                             bd=0, highlightthickness=1, command=self.toLogFrame)
        self.errBtn = Button(btnFrame, text="错误信息", relief=FLAT, padx=14, pady=1.5, bg=self.eColor,
                             bd=0, highlightthickness=1, command=self.toErrFrame)

        self.posBtn = Button(btnFrame, text="组合监控", relief=FLAT, padx=14, pady=1.5, bg=self.pColor,
                             bd=0, highlightthickness=1, command=self.toPosFrame)
        self.runBtn.pack(side=LEFT, expand=NO)
        self.logBtn.pack(side=LEFT, expand=NO)
        self.errBtn.pack(side=LEFT, expand=NO)
        self.posBtn.pack(side=LEFT, expand=NO)

        for btn in (self.runBtn, self.logBtn, self.errBtn, self.posBtn):
            btn.bind("<Enter>", self.handlerAdaptor(self.onEnter, button=btn))
            btn.bind("<Leave>", self.handlerAdaptor(self.onLeave, button=btn))

    def createLogBtnFrame(self):
        """创建日志按钮Frame"""
        lBtnFrame = Frame(self.logRecord, height=30, bg=self.bgColor)
        lBtnFrame.pack_propagate(0)
        lBtnFrame.pack(side=BOTTOM, fill=X)

        self.usrBtn = Button(lBtnFrame, text="用户日志", relief=FLAT, padx=14, pady=1.5, bg=self.rColor,
                             bd=0, highlightthickness=1, command=self.toUsrFrame)
        self.sigBtn = Button(lBtnFrame, text="信号记录", relief=FLAT, padx=14, pady=1.5, bg=self.lColor,
                             bd=0, highlightthickness=1, command=self.toSigFrame)
        self.sysBtn = Button(lBtnFrame, text="系统日志", relief=FLAT, padx=14, pady=1.5, bg=self.sColor,
                             bd=0, highlightthickness=1, command=self.toSysFrame)

        self.usrBtn.pack(side=LEFT, expand=NO)
        self.sigBtn.pack(side=LEFT, expand=NO)
        self.sysBtn.pack(side=LEFT, expand=NO)

        # for btn in (self.usrBtn, self.sigBtn, self.sysBtn):
            # btn.bind("<Enter>", self.handlerAdaptor(self.onEnter, button=btn))
            # btn.bind("<Leave>", self.handlerAdaptor(self.onLeave, button=btn))
            # pass

    def createLog(self):
        self.createSysLog()
        self.createSignal()
        self.createUsrLog()

    def createSysLog(self):
        """系统日志"""
        self.sysText = MonitorText(self.sysLog, height=20, bd=0)
        self.sysText.createScrollbar()
        self.sysText.pack(fill=BOTH, expand=YES)

    def createSignal(self):
        """信号记录"""
        self.sigText = LogText(self.sigRecord, height=20, bd=0)
        self.sigText.createScrollbar()
        self.sigText.pack(fill=BOTH, expand=YES)

    def createUsrLog(self):
        """用户日志"""
        self.usrText = LogText(self.usrLog, height=20, bd=0)
        self.usrText.createScrollbar()
        self.usrText.pack(fill=BOTH, expand=YES)

    def createPos(self):
        headList = ["账号", "合约", "账户仓", "策略仓", "仓差",
                    "策略多", "策略空","策略今多", "策略今空", "账户多", "账户空", "账户今多", "账户今空"]
        widthList = [20, 20, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]

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
            Id          = dataDict['StrategyId']
            UserNo      = dataDict["Config"]["Money"]["UserNo"]
            StName      = dataDict['StrategyName']
            BenchCon    = dataDict['ContractNo']
            kLineType   = dataDict['KLineType']
            kLineSlice  = dataDict['KLinceSlice']

            Frequency   = str(kLineSlice) + kLineType

            RunType     = "是" if dataDict['IsActualRun'] else "否"
            Status      = StrategyStatus[dataDict["StrategyState"]]
            InitFund    = dataDict['InitialFund']

            Available   = "{:.2f}".format(InitFund)
            MaxRetrace  = 0.0
            TotalProfit = 0.0
            WinRate     = 0.0

            return [
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

        except KeyError:
            traceback.print_exc()
            return []

    def addExecute(self, dataDict):
        values = self._formatMonitorInfo(dataDict)

        if not values:
            return

        strategyId = dataDict["StrategyId"]
        try:
            if self.executeListTree.exists(strategyId):
                self.updateStatus(strategyId, dataDict[5])
                return
        except Exception as e:
            self._logger.warn("addExecute exception")
        else:
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
            self.sysText.setText(data)

    def updateSigText(self):
        """更新信号记录"""
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

    def updateUsrText(self):
        """更新用户日志"""
        usrQueue = self._controller.get_logger().getUsrQ()
        usrData = ''
        flag = True
        try:
            while flag:
                usrData += usrQueue.get_nowait()+"\n"
                if usrQueue.empty():
                    flag = False

        except Exception as e:
            return
        else:
            self.usrText.setText(usrData)

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
        self.eColor = self.bgColor
        self.pColor = self.bgColor
        self.errBtn.config(bg=self.rColor)
        self.logBtn.config(bg=self.lColor)
        self.posBtn.config(bg=self.pColor)
        self.logRecord.pack_forget()
        self.errRecord.pack_forget()
        self.posMonitor.pack_forget()
        self.executeList.pack(side=TOP, fill=BOTH, expand=YES)

    # def toLogFrame(self, event, button):
    #     buttons = [self.runBtn, self.logBtn, self.errBtn, self.posBtn]
    #     colors = [self.rColor, self.lColor, self.eColor, self.pColor]
    #     frames = [self.executeList, self.logRecord, self.errRecord, self.posMonitor]
    #
    #     button.config(bg="white")
    #     index = buttons.index(button)
    #     colors[index] = button['bg']
    #     frames[index].pack(side=TOP, fill=BOTH, expand=YES)
    #     buttons.remove(button)
    #     colors.remove(colors[index])
    #     frames.remove(frames[index])
    #     #TODO:怎么pop呢？
    #
    #     for btn in buttons:
    #         i = buttons.index(btn)
    #         colors[i] = self.bgColor
    #         btn.config(bg=self.bgColor)
    #         frames[i].pack_forget()

    def toLogFrame(self):
        self.logBtn.config(bg="white")
        self.lColor = self.logBtn['bg']
        self.rColor = self.bgColor
        self.eColor = self.bgColor
        self.pColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.errBtn.config(bg=self.eColor)
        self.posBtn.config(bg=self.pColor)
        self.executeList.pack_forget()
        self.errRecord.pack_forget()
        self.posMonitor.pack_forget()
        self.logRecord.pack(side=TOP, fill=BOTH, expand=YES)

    def toSysFrame(self):
        self.sysBtn.config(bg="white")
        self.yColor = self.sysBtn['bg']
        self.sColor = self.bgColor
        self.uColor = self.bgColor

        self.sigBtn.config(bg=self.sColor)
        self.usrBtn.config(bg=self.uColor)

        self.sigRecord.pack_forget()
        self.usrLog.pack_forget()

        self.sysLog.pack(side=TOP, fill=BOTH, expand=YES)

    def toSigFrame(self):
        self.sigBtn.config(bg="white")
        self.sColor = self.sigBtn['bg']
        self.uColor = self.bgColor
        self.yColor = self.bgColor

        self.sysBtn.config(bg=self.yColor)
        self.usrBtn.config(bg=self.uColor)

        self.sysLog.pack_forget()
        self.usrLog.pack_forget()

        self.sigRecord.pack(side=TOP, fill=BOTH, expand=YES)

    def toUsrFrame(self):
        self.usrBtn.config(bg="white")
        self.uColor = self.sysBtn['bg']
        self.sColor = self.bgColor
        self.yColor = self.bgColor

        self.sigBtn.config(bg=self.sColor)
        self.sysBtn.config(bg=self.yColor)

        self.sigRecord.pack_forget()
        self.sysLog.pack_forget()

        self.usrLog.pack(side=TOP, fill=BOTH, expand=YES)

    def toErrFrame(self):
        self.errBtn.config(bg="white")
        self.eColor = self.errBtn['bg']
        self.lColor = self.bgColor
        self.rColor = self.bgColor
        self.pColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.logBtn.config(bg=self.lColor)
        self.posBtn.config(bg=self.pColor)
        self.parentFrame.update()
        self.logRecord.pack_forget()
        self.executeList.pack_forget()
        self.posMonitor.pack_forget()
        self.errRecord.pack(side=TOP, fill=BOTH, expand=YES)

    def toPosFrame(self):
        self.posBtn.config(bg="white")
        self.pColor = self.posBtn['bg']
        self.lColor = self.bgColor
        self.rColor = self.bgColor
        self.eColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.logBtn.config(bg=self.lColor)
        self.errBtn.config(bg=self.eColor)
        self.parentFrame.update()
        self.logRecord.pack_forget()
        self.executeList.pack_forget()
        self.errRecord.pack_forget()
        self.posMonitor.pack(side=TOP, fill=BOTH, expand=YES)

    def handlerAdaptor(self, fun, **kwargs):
        return lambda event, fun=fun, kwargs=kwargs: fun(event, **kwargs)

    def onEnter(self, event, button):
        """鼠标进入事件"""
        buttons = [self.runBtn, self.logBtn, self.errBtn, self.posBtn]
        button.config(bg='white')
        buttons.remove(button)
        for btn in buttons:
            btn.config(bg=self.bgColor)

    def onLeave(self, event, button):
        """鼠标离开事件"""
        buttons = [self.runBtn, self.logBtn, self.errBtn, self.posBtn]
        #TODO: 类实例作为字典键值有问题!
        btnColorDict = {
            self.runBtn: self.rColor,
            self.logBtn: self.lColor,
            self.errBtn: self.eColor,
            self.posBtn: self.pColor
        }
        button.config(bg=rgb_to_hex(227, 230, 233))
        button['bg'] = btnColorDict[button]

        buttons.remove(button)
        for btn in buttons:
            btn['bg'] = btnColorDict[btn]

    def deleteStrategy(self, strategyId):
        """删除策略"""
        if str(strategyId) in self.executeListTree.get_children():
            self.executeListTree.delete(strategyId)
            self._logger.info(f"[UI][{strategyId}]: Delete strategy {strategyId} successfully!")

    def updateValue(self, strategyId, dataDict):
        """更新策略ID对应的运行数据"""

        colValues = {
                       "#9": "{:.2f}".format(dataDict["Available"]),
                       "#10": "{:.2f}".format(dataDict["MaxRetrace"]),
                       "#11": "{:.2f}".format(dataDict["NetProfit"]),
                       "#12": "{:.2f}".format(dataDict["WinRate"])
                   }

        if str(strategyId) in self.executeListTree.get_children():
            for k, v in colValues.items():
                self.executeListTree.set(strategyId, column=k, value=v)

    def updateStatus(self, strategyId, status):
        """更新策略状态"""
        if str(strategyId) in self.executeListTree.get_children():
            self.executeListTree.set(strategyId, column="#6", value=StrategyStatus[status])

    def updatePos(self, positions):
        for itemId in self.posTree.get_children():
            self.posTree.delete(itemId)

        strategyPos = {}
        accountPos  = {}
        strategyAccount = set()
        # 重组策略仓
        for sid in positions["Strategy"]:
            for user in positions["Strategy"][sid]:
                strategyAccount.add(user)

                if user not in strategyPos:
                    strategyPos.update(
                        {
                            #TODO：结构和下面的不一致
                            user: positions["Strategy"][sid][user]
                        }
                    )
                else:
                    for pCont, pInfo in positions["Strategy"][sid][user].items():
                        if pCont not in strategyPos[user]:
                            strategyPos[user].update(
                                {
                                    pCont: pInfo
                                }
                            )
                        else:
                            strategyPos[user][pCont]["TotalBuy"] += pInfo["TotalBuy"]
                            strategyPos[user][pCont]["TotalSell"] += pInfo["TotalSell"]
                            strategyPos[user][pCont]["TodayBuy"] += pInfo["TodayBuy"]
                            strategyPos[user][pCont]["TodaySell"] += pInfo["TodaySell"]
        #print("sssssss: ", strategyPos)

        # 重组账户仓
        for user in positions["Account"]:
            if user not in strategyAccount:
                continue

            if user not in accountPos:
                accountPos[user] = {}

            for pCont, pInfo in positions["Account"][user].items():
                if pCont[-1] == "T":    # 只关注账户中的投机单的持仓
                    if pCont[:-2] not in accountPos[user]:
                        if pCont[-2] == "S":
                            accountPos[user][pCont[:-2]] = {
                                "TotalSell": pInfo["PositionQty"],
                                "TodaySell": pInfo["PositionQty"] - pInfo["PrePositionQty"],
                                "TotalBuy" : 0,
                                "TodayBuy" : 0
                            }
                        else:
                            accountPos[user][pCont[:-2]] = {
                                "TotalBuy" : pInfo["PositionQty"],
                                "TodayBuy" : pInfo["PositionQty"] - pInfo["PrePositionQty"],
                                "TotalSell": 0,
                                "TodaySell": 0
                            }

                    else:
                        if pCont[-2] == "S":
                            accountPos[user][pCont[:-2]]["TotalSell"] += pInfo["PositionQty"]
                            accountPos[user][pCont[:-2]]["TodaySell"] += pInfo["PositionQty"] - pInfo["PrePositionQty"]

                        else:
                            accountPos[user][pCont[:-2]]["TotalBuy"] += pInfo["PositionQty"]
                            accountPos[user][pCont[:-2]]["TodayBuy"] += pInfo["PositionQty"] - pInfo["PrePositionQty"]

        #print("tttttttttt: ", accountPos)

        rlt = []

        for user in strategyAccount:
            for c, p in strategyPos[user].items():

                if user in accountPos:
                    if c in accountPos[user]:
                        aTPos = accountPos[user][c]["TotalBuy"] - (-accountPos[user][c]["TotalSell"]) # 账户仓
                        sTPos = p["TotalBuy"] - (-p["TotalSell"])   # 策略仓
                        posDif = sTPos - aTPos                      # 仓差
                        rlt.append([user, c, aTPos, sTPos, posDif,
                                    p["TotalBuy"], p["TotalSell"], p["TodayBuy"], p["TodaySell"],
                                    accountPos[user][c]["TotalBuy"], accountPos[user][c]["TotalSell"],
                                    accountPos[user][c]["TodayBuy"], accountPos[user][c]["TodaySell"]])
                        continue

                rlt.append([user, c, 0, p["TotalBuy"] - (-p["TotalSell"]), p["TotalBuy"] - (-p["TotalSell"]),
                            p["TotalBuy"], p["TotalSell"], p["TodayBuy"], p["TodaySell"], 0, 0, 0, 0])

        # print("BBBBBBBBBBB: ", rlt)
        for v in rlt:
            self.posTree.insert("", 'end', values=v)



