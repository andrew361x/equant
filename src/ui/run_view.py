import os
import sys
sys.path.append("..")

import re
import json
import pandas as pd
import traceback

import tkinter as tk
import tkinter.ttk as ttk

from dateutil.parser import parse
from datetime import datetime
from tkinter import messagebox
from utils.utils import *
from utils.language import Language
from .language import Language
from .editor import ContractText
from capi.com_types import *

from .com_view import QuantToplevel, QuantFrame
from engine.strategy_cfg_model_new import StrategyConfig_new


class RunWin(QuantToplevel, QuantFrame):
    """运行按钮点击弹出窗口"""
    # 背景色
    bgColor = rgb_to_hex(245, 245, 245)
    bgColorW = "white"

    def __init__(self, control, path, flag=False, master=None, param={}):
        # flag: 是否是从策略右键弹出的标志位
        super().__init__(master)
        self._control = control
        self._exchange = self._control.model.getExchange()
        self._commodity = self._control.model.getCommodity()
        self._contract = self._control.model.getContract()
        self._userNo = self._control.model.getUserNo()

        # 参数设置
        self._strConfig = StrategyConfig_new()

        # 用户设置信息
        self.config = {}

        # 获取用户参数
        self._userParam = param
        # 策略路径
        self._strategyPath = path
        # 是否时属性设置运行窗口标志位
        self._paramFlag = flag

        # 用户设置的多合约信息
        self._contsInfo = []

        self.title("策略属性设置")
        self.attributes("-toolwindow", 1)
        self._master = master
        self.topFrame = tk.Frame(self, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        self.topFrame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)
        self.setPos()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # 将函数包装一下(初始资金只能输入数字、浮点数)
        self.testContent = self.register(self.testDigit)
        self.testFlt     = self.register(self.testFloat)
        # 新建属性设置变量
        self.initVariable()

        self.fColor = self.bgColor
        self.sColor = self.bgColor
        self.rColor = self.bgColor
        self.pColor = self.bgColor
        self.cColor = self.bgColorW

        self.createNotebook(self.topFrame)

        self.fundFrame   = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))
        self.sampleFrame = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))
        self.runFrame    = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))
        self.paramFrame  = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))
        self.contFrame   = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))

        # self.contFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.createCont(self.contFrame)
        self.createRun(self.runFrame)
        self.createFund(self.fundFrame)
        self.createSample(self.sampleFrame)
        self.createParma(self.paramFrame)
        self.addButton(self.topFrame)

        self.contFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        # TODO： 如果将配置文件内容删除会报错
        self.setDefaultConfigure()
        # 根据用户设置内容初始化控件
        self.initWidget()

    def initVariable(self):
        # 变量
        self.user             =    tk.StringVar()  # 用户
        self.initFund         =    tk.StringVar()  # 初始资金
        self.defaultType      =    tk.StringVar()  # 默认下单方式
        self.defaultQty       =    tk.StringVar()  # 默认下单量（或资金、或比例）
        self.minQty           =    tk.StringVar()  # 最小下单量
        # self.hedge            =    tk.StringVar()  # 投保标志
        self.margin           =    tk.StringVar()  # 保证金

        self.openType         =    tk.StringVar()  # 开仓收费方式
        self.closeType        =    tk.StringVar()  # 平仓收费方式
        self.openFee          =    tk.StringVar()  # 开仓手续费（率）
        self.closeFee         =    tk.StringVar()  # 平仓手续费（率）
        self.dir              =    tk.StringVar()  # 交易方向
        self.slippage         =    tk.StringVar()  # 滑点损耗

        self.isCycle          =    tk.IntVar()     # 是否按周期触发
        self.cycle            =    tk.StringVar()  # 周期
        # TODO：定时触发(text控件不能设置变量)
        self.isKLine          =    tk.IntVar()     # K线触发
        self.isSnapShot       =    tk.IntVar()     # 行情触发
        self.isTrade          =    tk.IntVar()     # 交易数据触发

        # 样本类型： 0. 所有K线  1. 起始日期  2. 固定根数  3. 不执行历史K线
        # self.sampleVar        =   tk.IntVar()
        # self.beginDate        =   tk.StringVar()  # 起始日期
        # self.fixQty           =   tk.StringVar()  # 固定根数

        self.sendOrderMode    =   tk.IntVar()     # 发单时机： 0. 实时发单 1. K线稳定后发单
        self.isActual         =   tk.IntVar()     # 实时发单
        self.isAlarm          =   tk.IntVar()     # 发单报警

        self.isOpenTimes      =   tk.IntVar()     # 每根K线同向开仓次数标志
        self.openTimes        =   tk.StringVar()  # 每根K线同向开仓次数
        self.isConOpenTimes   =   tk.IntVar()     # 最大连续同向开仓次数标志
        self.conOpenTimes     =   tk.StringVar()  # 最大连续同向开仓次数
        self.canClose         =   tk.IntVar()     # 开仓的当前K线不允许平仓
        self.canOpen          =   tk.IntVar()     # 平仓的当前K线不允许开仓

        # 根据选择内容设置标签内容变量
        self.unitVar          =   tk.StringVar()
        self.openTypeUnitVar  =   tk.StringVar()
        self.closeTypeUnitVar =   tk.StringVar()

    def getTextConfigure(self):
        """从配置文件中得到配置信息"""
        try:
            configure = self.readConfig()
        except EOFError:
            configure = None

        # key = self._control.getEditorText()["path"]
        key = self._strategyPath
        if configure:
            if key in configure:
                return configure[key]
        return None

    def setDefaultConfigure(self):
        conf = self.getTextConfigure()
        if conf:
        # if None:
            # self.user.set(conf[VUser]),
            self.initFund.set(conf[VInitFund]),
            self.defaultType.set(conf[VDefaultType]),
            self.defaultQty.set(conf[VDefaultQty]),
            self.minQty.set(conf[VMinQty]),
            # self.hedge.set(conf[VHedge]),
            self.margin.set(conf[VMinQty]),

            self.openType.set(conf[VOpenType]),
            self.closeType.set(conf[VCloseType]),
            self.openFee.set(conf[VOpenFee]),
            self.closeFee.set(conf[VCloseFee]),
            self.dir.set(conf[VDirection]),
            self.slippage.set(conf[VSlippage]),

            self.isCycle.set(conf[VIsCycle]),
            self.cycle.set(conf[VCycle]),

            # 定时触发通过函数设置
            self.timerText.delete(0.0, tk.END)
            self.setText(self.timerText, conf[VTimer])

            self.isKLine.set(conf[VIsKLine]),
            self.isSnapShot.set(conf[VIsMarket]),
            self.isTrade.set(conf[VIsTrade]),

            # self.sampleVar.set(conf[VSampleVar]),
            # self.beginDate.set(conf[VBeginDate]),
            # self.fixQty.set(conf[VFixQty]),

            self.sendOrderMode.set(conf[VSendOrderMode]),
            self.isActual.set(conf[VIsActual]),
            try:
                self.isAlarm.set(conf[VIsAlarm])
            except KeyError as e:
                self.isAlarm.set(0)

            self.isOpenTimes.set(conf[VIsOpenTimes]),
            self.openTimes.set(conf[VOpenTimes]),
            self.isConOpenTimes.set(conf[VIsConOpenTimes]),
            self.conOpenTimes.set(conf[VConOpenTimes]),
            self.canClose.set(conf[VCanClose]),
            self.canOpen.set(conf[VCanOpen]),

            # 用户配置参数信息
            # 若保存的设置中用户参数为空，则不对self._userParam赋值
            # try:
            #     if conf[VParams]:
            #         self._userParam = conf[VParams]
            # except KeyError as e:
            #     traceback.print_exc()

            #TODO: DefaultSample
            try:
                if conf[VContSettings]:
                    self._contsInfo = conf[VContSettings]
            except KeyError as e:
                traceback.print_exc()

        # if True:
        else:
            # 设置默认值
            self.isCycle.set(0),
            self.cycle.set(200),
            self.isKLine.set(1),
            self.isSnapShot.set(0),
            self.isTrade.set(0),
            # 指定时刻不好存

            # 发单时机
            self.sendOrderMode.set(0)
            # 运行模式
            self.isActual.set(0)
            # 发单报警
            self.isAlarm.set(0)

            # 初始资金
            self.initFund.set(10000000)
            # 交易方向
            self.dir.set("双向交易")
            # 默认下单量
            self.defaultType.set("按固定合约数")
            self.defaultQty.set(1)
            # 最小下单量
            self.minQty.set(1)

            # 投保标志
            # self.hedge.set("投机")
            # 保证金率
            self.margin.set(8)
            #TODO:直接设置界面怎么更改（有没有百分号）
            # 开仓收费方式
            self.openType.set("固定值")
            # 平仓收费方式
            self.closeType.set("固定值")
            # 开仓手续费（率）
            self.openFee.set("1")
            # 平仓手续费（率）
            self.closeFee.set("1")
            # 滑点损耗
            self.slippage.set("0")

            # 样本设置
            # self.sampleVar.set(2)
            # self.fixQty.set(2000)

            # 发单设置
            # 每根K线同向开仓次数标志
            self.isOpenTimes.set(0)
            # 每根K线同向开仓次数
            self.openTimes.set("1")
            # 最大连续同向开仓次数标志
            self.isConOpenTimes.set(0)
            # 最大连续同向开仓次数
            self.conOpenTimes.set("1")
            # 开仓的当前K线不允许平仓
            self.canClose.set(0)
            # 平仓的当前K线不允许开仓
            self.canOpen.set(0)

    def initWidget(self):
        """根据用户的配置文件决定控件的状态和内容"""
        self.openTypeUnitSet()
        self.closeTypeUnitSet()
        self.defaultUnitSetting()
        self.setCycleEntryState()

        # 设置用户参数
        self.insertParams()
        # 恢复用户最新保存的多合约信息
        self.insertContInfo()

    def getConfig(self):
        """获取用户配置的config"""
        return self.config

    def setPos(self):
        # 获取主窗口大小和位置，根据主窗口调整输入框位置
        ws = self._master.winfo_width()
        hs = self._master.winfo_height()
        wx = self._master.winfo_x()
        wy = self._master.winfo_y()

        #计算窗口位置
        w, h = 620, 570
        x = (wx + ws/2) - w/2
        y = (wy + hs/2) - h/2

        #弹出输入窗口，输入文件名称
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.minsize(620, 570)
        self.resizable(0, 0)

    def createNotebook(self, frame):
        nbFrame = tk.Frame(frame, height=30, bg=self.bgColor)
        nbFrame.pack_propagate(0)
        nbFrame.pack(side=tk.TOP, fill=tk.X)

        self.contBtn = tk.Button(nbFrame, text="合约设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.cColor,
                                 bd=0, highlightthickness=1, command=self.toContFrame)
        self.fundBtn = tk.Button(nbFrame, text="资金设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.fColor,
                                 bd=0, highlightthickness=1, command=self.toFundFrame)
        self.runBtn = tk.Button(nbFrame, text="运行设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.rColor,
                                bd=0, highlightthickness=1, command=self.toRunFrame)
        self.sampleBtn = tk.Button(nbFrame, text="样本设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.sColor,
                                   bd=0, highlightthickness=1, command=self.toSampFrame)
        self.paramBtn = tk.Button(nbFrame, text="参数设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.pColor,
                                  bd=0, highlightthickness=1, command=self.toParamFrame)

        self.contBtn.pack(side=tk.LEFT, expand=tk.NO)
        self.runBtn.pack(side=tk.LEFT, expand=tk.NO)
        self.fundBtn.pack(side=tk.LEFT, expand=tk.NO)
        self.sampleBtn.pack(side=tk.LEFT, expand=tk.NO)
        self.paramBtn.pack(side=tk.LEFT, expand=tk.NO)

        for btn in (self.contBtn, self.fundBtn, self.sampleBtn, self.runBtn, self.paramBtn):
            btn.bind("<Enter>", self.handlerAdaptor(self.onEnter, button=btn))
            btn.bind("<Leave>", self.handlerAdaptor(self.onLeave, button=btn))

    def toFundFrame(self):
        self.fundBtn.config(bg="white")
        self.fColor = self.fundBtn['bg']
        self.rColor = self.bgColor
        self.sColor = self.bgColor
        self.pColor = self.bgColor
        self.cColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.sampleBtn.config(bg=self.sColor)
        self.paramBtn.config(bg=self.pColor)
        self.contBtn.config(bg=self.cColor)

        self.runFrame.pack_forget()
        self.sampleFrame.pack_forget()
        self.paramFrame.pack_forget()
        self.contFrame.pack_forget()
        self.fundFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def toSampFrame(self):
        self.sampleBtn.config(bg="white")
        self.sColor = self.sampleBtn['bg']
        self.rColor = self.bgColor
        self.fColor = self.bgColor
        self.pColor = self.bgColor
        self.cColor = self.bgColor
        self.fundBtn.config(bg=self.fColor)
        self.runBtn.config(bg=self.rColor)
        self.paramBtn.config(bg=self.pColor)
        self.contBtn.config(bg=self.cColor)

        self.fundFrame.pack_forget()
        self.runFrame.pack_forget()
        self.paramFrame.pack_forget()
        self.contFrame.pack_forget()
        self.sampleFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def toRunFrame(self):
        self.runBtn.config(bg="white")
        self.rColor = self.runBtn['bg']
        self.fColor = self.bgColor
        self.sColor = self.bgColor
        self.pColor = self.bgColor
        self.cColor = self.bgColor
        self.fundBtn.config(bg=self.fColor)
        self.sampleBtn.config(bg=self.sColor)
        self.paramBtn.config(bg=self.pColor)
        self.contBtn.config(bg=self.cColor)

        self.fundFrame.pack_forget()
        self.sampleFrame.pack_forget()
        self.paramFrame.pack_forget()
        self.contFrame.pack_forget()
        self.runFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def toParamFrame(self):
        self.paramBtn.config(bg="white")
        self.pColor = self.paramBtn['bg']
        self.sColor = self.bgColor
        self.rColor = self.bgColor
        self.fColor = self.bgColor
        self.cColor = self.bgColor
        self.fundBtn.config(bg=self.fColor)
        self.runBtn.config(bg=self.rColor)
        self.sampleBtn.config(bg=self.sColor)
        self.contBtn.config(bg=self.cColor)

        self.fundFrame.pack_forget()
        self.runFrame.pack_forget()
        self.sampleFrame.pack_forget()
        self.contFrame.pack_forget()
        self.paramFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def toContFrame(self):
        self.contBtn.config(bg="white")
        self.cColor = self.contBtn['bg']
        self.sColor = self.bgColor
        self.rColor = self.bgColor
        self.fColor = self.bgColor
        self.pColor = self.bgColor
        self.fundBtn.config(bg=self.fColor)
        self.runBtn.config(bg=self.rColor)
        self.sampleBtn.config(bg=self.sColor)
        self.paramBtn.config(bg=self.pColor)

        self.fundFrame.pack_forget()
        self.runFrame.pack_forget()
        self.sampleFrame.pack_forget()
        self.paramFrame.pack_forget()
        self.contFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def onEnter(self, event, button):
        if button == self.fundBtn:
            button.config(bg='white')
            self.sampleBtn.config(bg=self.bgColor)
            self.runBtn.config(bg=self.bgColor)
            self.paramBtn.config(bg=self.bgColor)
            self.contBtn.config(bg=self.bgColor)
        elif button == self.sampleBtn:
            button.config(bg='white')
            self.fundBtn.config(bg=self.bgColor)
            self.runBtn.config(bg=self.bgColor)
            self.paramBtn.config(bg=self.bgColor)
            self.contBtn.config(bg=self.bgColor)
        elif button == self.runBtn:
            button.config(bg='white')
            self.fundBtn.config(bg=self.bgColor)
            self.sampleBtn.config(bg=self.bgColor)
            self.paramBtn.config(bg=self.bgColor)
            self.contBtn.config(bg=self.bgColor)
        elif button == self.paramBtn:
            button.config(bg='white')
            self.fundBtn.config(bg=self.bgColor)
            self.sampleBtn.config(bg=self.bgColor)
            self.runBtn.config(bg=self.bgColor)
            self.contBtn.config(bg=self.bgColor)
        else:
            button.config(bg='white')
            self.fundBtn.config(bg=self.bgColor)
            self.sampleBtn.config(bg=self.bgColor)
            self.runBtn.config(bg=self.bgColor)
            self.paramBtn.config(bg=self.bgColor)

    def onLeave(self, event, button):
        button.config(bg=rgb_to_hex(227, 230, 233))
        if button == self.fundBtn:
            button['bg'] = self.fColor
            self.runBtn['bg'] = self.rColor
            self.sampleBtn['bg'] = self.sColor
            self.paramBtn['bg'] = self.pColor
            self.contBtn['bg'] = self.cColor
        elif button == self.runBtn:
            button['bg'] = self.rColor
            self.fundBtn['bg'] = self.fColor
            self.sampleBtn['bg'] = self.sColor
            self.paramBtn['bg'] = self.pColor
            self.contBtn['bg'] = self.cColor
        elif button == self.sampleBtn:
            button['bg'] = self.sColor
            self.fundBtn['bg'] = self.fColor
            self.runBtn['bg'] = self.rColor
            self.paramBtn['bg'] = self.pColor
            self.contBtn['bg'] = self.cColor
        elif button == self.paramBtn:
            button['bg'] = self.pColor
            self.fundBtn['bg'] = self.fColor
            self.runBtn['bg'] = self.rColor
            self.sampleBtn['bg'] = self.sColor
            self.contBtn['bg'] = self.cColor
        elif button == self.contBtn:
            button['bg'] = self.cColor
            self.fundBtn['bg'] = self.fColor
            self.runBtn['bg'] = self.rColor
            self.sampleBtn['bg'] = self.sColor
            self.paramBtn['bg'] = self.pColor
        else:
            pass

    def createFund(self, frame):
        self.setInitFunds(frame)
        self.setTradeDir(frame)
        self.setDefaultOrder(frame)
        # self.setOrderSym(frame)
        self.setMargin(frame)
        self.setCommision(frame)
        self.setSlippage(frame)

    def createSample(self, frame):
        # self.setSample(frame)
        self.setSendOrderLimit(frame)

    def createRun(self, frame):
        self.setTrigger(frame)
        baseFrame = tk.LabelFrame(frame, text="基础设置", bg=rgb_to_hex(255, 255, 255), padx=5)
        baseFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, padx=15, pady=5)

        self.SendOrderMode(baseFrame)
        self.setRunMode(baseFrame)
        # self.setContract(baseFrame)
        self.setUser(baseFrame)
        # self.setKLineType(baseFrame)
        # self.setKLineSlice(baseFrame)

    def createParma(self, frame):
        self.setParamLabel(frame)
        self.addParam(frame)

    def createCont(self, frame):
        self.setContList(frame)
        self.addContBtn(frame)

    def setParamLabel(self, frame):
        tk.Label(frame, text='鼠标单击"当前值"进行参数修改:', bg=rgb_to_hex(255, 255, 255),
                 justif=tk.LEFT,  anchor=tk.W, width=40).pack(side=tk.TOP, anchor=tk.W, padx=15, pady=5)

    # 生成参数设置的目录树
    def addParam(self, frame):
        headList = ["参数", "当前值", "类型", "描述"]
        widthList = [5, 20, 20, 200]

        self.paramBar = ttk.Scrollbar(frame, orient="horizontal")
        self.paramBar.pack(side=tk.BOTTOM, fill=tk.X)

        self.paramTree = ttk.Treeview(frame, show="headings", height=28, columns=tuple(headList),
                                      yscrollcommand=self.paramBar.set)
        self.paramBar.config(command=self.paramTree.xview)
        self.paramTree.pack(fill=tk.BOTH, expand=tk.YES, padx=15)

        for key, w in zip(headList, widthList):
            self.paramTree.column(key, width=w, anchor=tk.W)
            self.paramTree.heading(key, text=key, anchor=tk.W)

        # for key in self._userParam:
        #     self.paramTree.insert("", tk.END, values=tuple([key, self._userParam[key]]), tags=key)

        #TODO: tag怎么实现颜色配置
        # self._paramId += 1
        # self.paramTree.insert("", tk.END, values=tuple(["N", 20,  "整形", ""]), tag="tag0")

        self.paramTree.bind("<Button-1>", self.onClick)

    def insertParams(self):
        """恢复用户选择的参数信息"""
        for key in self._userParam:
            self.paramTree.insert("", tk.END, values=tuple(
                [key, self._userParam[key][0], type(self._userParam[key][0]), self._userParam[key][1]]), tags=key)
            # self.paramTree.insert("", tk.END, values=tuple(
            #     [key, self._userParam[key][0], type(self._userParam[key]), self._userParam[key][1]]), tags=key)

    def insertContInfo(self):
        """恢复配置文件中用户选择的多合约信息"""
        for key in self._contsInfo:
            self.contTree.insert("", tk.END, values=key)

    def onClick(self, event):
        """单击更改策略值"""
        x, y, widget = event.x, event.y, event.widget

        select = widget.identify_row(event.y)
        widget.selection_set(select)
        widget.focus(select)

        item = widget.item(widget.focus())
        itemValues = item['values']
        iid = widget.identify_row(y)
        column = event.widget.identify_column(x)

        if column != "#2":
            return

        if not column or not iid:
            return

        if not len(itemValues):
            return

        self.cell_value = itemValues[int(column[1]) - 1]

        # if not self.cell_value:
        #     return

        bbox = widget.bbox(iid, column)
        if not bbox:
            return

        x, y, width, height = bbox

        self.entryedit = EntryPopup(self.paramTree, self.cell_value)
        self.entryedit.place(x=x, y=y, width=width, height=height)

    def setContList(self, frame):
        """合约列表"""
        treeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        treeFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, padx=2, pady=5)
        # headList = ["合约", "K线类型", "K线根数", "保证金(%)", "开仓手续费", "平仓手续费", ""]
        # widthList = [30, 5, 5, 5, 10, 10, 30]

        headList = ["合约", "K线类型", "K线周期", "运算起始点"]
        widthList= [30, 5, 5, 10]

        self.contTree = ttk.Treeview(treeFrame, show="headings", height=28, columns=tuple(headList))
        self.contTree.pack(fill=tk.BOTH, expand=tk.YES, padx=5)

        for key, w in zip(headList, widthList):
            self.contTree.column(key, width=w, anchor=tk.W)
            self.contTree.heading(key, text=key, anchor=tk.W)

    def addContBtn(self, frame):
        # TODO: 和加载的addButton代码相同
        # TODO: 这种button可以写一个复用

        # TODO：关闭增加窗口之后会有问题
        btnFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        btnFrame.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
        modifyButton = tk.Button(btnFrame, text="修改", relief=tk.FLAT, bg=rgb_to_hex(230, 230, 230),
                                 activebackground="lightblue", highlightbackground="red",
                                 overrelief="groove",
                                 command=self.contModify)
        modifyButton.pack(side=tk.BOTTOM, ipadx=20, padx=5)

        delButton = tk.Button(btnFrame, text="删除", relief=tk.FLAT,
                                activebackground="lightblue",
                                overrelief="groove",
                                command=self.contDel, bg=rgb_to_hex(230, 230, 230))
        delButton.pack(side=tk.BOTTOM, ipadx=20, padx=5, pady=5)

        addButton = tk.Button(btnFrame, text="增加", relief=tk.FLAT,
                                activebackground="lightblue",
                                overrelief="groove",
                                command=self.contAdd, bg=rgb_to_hex(230, 230, 230))
        addButton.pack(side=tk.BOTTOM, ipadx=20, padx=5)

    def contAdd(self):
        """合约增加事件"""
        addWin = AddContWin(self, self._exchange, self._commodity, self._contract)
        addWin.display()

    def contDel(self):
        """合约删除事件"""
        item = self.contTree.selection()
        for id in item:
            self.contTree.delete(id)

    def contModify(self):
        """合约修改事件"""
        #TODO：没有选择的情况下怎么办？？？？？？？？？？？？？
        item = self.contTree.item(self.contTree.focus())
        itemValues = item['values']
        if not len(itemValues):
            return

        modWin = AddContWin(self, self._exchange, self._commodity, self._contract)
        modWin.contractButton.config(state="disabled")
        modWin.codeEntry.config(state="disabled")
        modWin.setWinValue(self.contTree.focus(), itemValues)
        modWin.display()


    # 资金设置
    def setUser(self, frame):
        """设置账户"""
        self.userFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.userFrame.pack(fill=tk.NONE, anchor=tk.W, padx=5, pady=5)
        userLabel = tk.Label(self.userFrame, text="账户:", bg=rgb_to_hex(255, 255, 255),
                             justif=tk.LEFT, anchor=tk.W, width=10)
        userLabel.pack(side=tk.LEFT, padx=5)

        self.userChosen = ttk.Combobox(self.userFrame, state="readonly", textvariable=self.user)
        # TODO：账户信息重复
        userList = []   # 从交易引擎获取
        [userList.append(user["UserNo"]) for user in self._userNo if not user["UserNo"] in userList]

        self.userChosen["values"] = userList
        if userList:
            self.userChosen.current(0)
        self.userChosen.pack(side=tk.LEFT, padx=10)

    def setInitFunds(self, frame):
        """设置初始资金"""
        initFundFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        initFundFrame.pack(fill=tk.X, padx=15, pady=5)

        iniFundLabel = tk.Label(initFundFrame, text='初始资金:', bg=rgb_to_hex(255, 255, 255),
                                justif=tk.LEFT, anchor=tk.W, width=15)
        iniFundLabel.pack(side=tk.LEFT)
        self.initFundEntry = tk.Entry(initFundFrame, relief=tk.GROOVE, bd=2, textvariable=self.initFund, validate="key",
                                      validatecommand=(self.testContent, "%P"))
        self.initFundEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        tk.Label(initFundFrame, text='元', bg=rgb_to_hex(255, 255, 255), justif=tk.LEFT, anchor=tk.W, width=2) \
            .pack(side=tk.LEFT, padx=1)

    def setDefaultOrder(self, frame):
        defaultFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        defaultFrame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)

        defaultLabel = tk.Label(defaultFrame, text='默认下单量:', bg=rgb_to_hex(255, 255, 255),
                                justif=tk.LEFT, anchor=tk.W, width=15)
        defaultLabel.pack(side=tk.LEFT)

        typeChosen = ttk.Combobox(defaultFrame, width=11, textvariable=self.defaultType, state="readonly")
        typeList = ['按固定合约数', '按资金比例', '按固定资金']
        typeChosen["values"] = typeList
        # typeChosen.current(0)
        typeChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)
        typeChosen.bind('<<ComboboxSelected>>', self.defaultUnitSetting)

        qtyEntry = tk.Entry(defaultFrame, relief=tk.GROOVE, width=7, textvariable=self.defaultQty, bd=2,
                            validate="key", validatecommand=(self.testContent, "%P"))
        # qtyEntry.insert(tk.END, 1)
        qtyEntry.pack(side=tk.LEFT, expand=tk.NO)

        defaultUnit = tk.Label(defaultFrame, text='手', bg=rgb_to_hex(255, 255, 255),
                               textvariable=self.unitVar, justif=tk.LEFT, anchor=tk.W, width=2)
        defaultUnit.pack(side=tk.LEFT, expand=tk.NO, padx=1)

        # 最小下单量
        minQtyFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        minQtyFrame.pack(side=tk.TOP, fill=tk.X, padx=15, pady=5)
        tk.Label(minQtyFrame, text='最小下单量: ', bg=rgb_to_hex(255, 255, 255), justif=tk.LEFT, anchor=tk.W, width=15) \
                 .pack(side=tk.LEFT)
        self.minQtyEntry = tk.Entry(minQtyFrame, relief=tk.GROOVE, bd=2, width=10, textvariable=self.minQty,
                               validate="key", validatecommand=(self.testContent, "%P"))
        # minQtyEntry.insert(tk.END, 1)
        self.minQtyEntry.pack(side=tk.LEFT, expand=tk.NO, padx=4)
        tk.Label(minQtyFrame, text='手(1-{})'.format(MAXSINGLETRADESIZE), bg=rgb_to_hex(255, 255, 255),
                 justif=tk.LEFT, anchor=tk.W, width=10).pack(side=tk.LEFT, expand=tk.NO, padx=4)

    def defaultUnitSetting(self, event=None):
        """默认下单量checkbutton选中事件"""
        # TODO：把字符串定义为事件
        type = self.defaultType.get()
        if type == "按固定合约数":
            self.defaultQty.set(1)
            self.unitVar.set("手")
        elif type == "按资金比例":
            self.defaultQty.set(5)
            self.unitVar.set("%")
        elif type == "按固定资金":
            self.defaultQty.set(1000000)
            self.unitVar.set("元")
        else:
            pass

    # TODO: 删除
    # def setOrderSym(self, frame):
    #     """投保标志"""
    #     symFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
    #     symFrame.pack(fill=tk.X, padx=15, pady=5)
    #     symLabel = tk.Label(symFrame, text="投保标志:", bg=rgb_to_hex(255, 255, 255),
    #                         justif=tk.LEFT, anchor=tk.W, width=15)
    #     symLabel.pack(side=tk.LEFT)
    #
    #     symChosen = ttk.Combobox(symFrame, state="readonly", textvariable=self.hedge)
    #     symList = ['投机', '套利', '保值', '做市']
    #     symChosen["values"] = symList
    #     symChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)

    def setMargin(self, frame):
        """设置保证金比率"""
        marginFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        marginFrame.pack(fill=tk.X, padx=15, pady=5)

        marginLabel = tk.Label(marginFrame, text='保证金率:', bg=rgb_to_hex(255, 255, 255),
                               justif=tk.LEFT, anchor=tk.W, width=15)
        marginLabel.pack(side=tk.LEFT)
        marginEntry = tk.Entry(marginFrame, relief=tk.GROOVE, bd=2, textvariable=self.margin,
                               validate="key", validatecommand=(self.testContent, "%P"))
        marginEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        tk.Label(marginFrame, text='%', bg=rgb_to_hex(255, 255, 255), justif=tk.LEFT, anchor=tk.W, width=2) \
            .pack(side=tk.LEFT, expand=tk.NO, padx=1)

    def setCommision(self, frame):
        """手续费"""
        openTypeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        openTypeFrame.pack(fill=tk.X, padx=15, pady=5)
        openTypeLabel = tk.Label(openTypeFrame, text='开仓收费方式:', bg=rgb_to_hex(255, 255, 255),
                                 justify=tk.LEFT, anchor=tk.W, width=15)
        openTypeLabel.pack(side=tk.LEFT)
        openTypeChosen = ttk.Combobox(openTypeFrame, state="readonly", textvariable=self.openType)
        openTypeChosen['values'] = ['固定值', '比例']
        # openTypeChosen.current(0)
        openTypeChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)
        openTypeChosen.bind('<<ComboboxSelected>>', self.openTypeUnitSet)

        openFeeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        openFeeFrame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(openFeeFrame, text='开仓手续费(率):', bg=rgb_to_hex(255, 255, 255),
                 justify=tk.LEFT, anchor=tk.W, width=15).pack(side=tk.LEFT)
        openFeeEntry = tk.Entry(openFeeFrame, relief=tk.GROOVE, bd=2, textvariable=self.openFee,
                                validate="key", validatecommand=(self.testFlt, "%P"))
        openFeeEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)

        openFeeUnit = tk.Label(openFeeFrame, text=' ', bg=rgb_to_hex(255, 255, 255),
                               textvariable=self.openTypeUnitVar, justify=tk.LEFT, anchor=tk.W, width=2)
        openFeeUnit.pack(side=tk.LEFT, padx=5)

        closeTypeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        closeTypeFrame.pack(fill=tk.X, padx=15, pady=5)
        closeTypeLabel = tk.Label(closeTypeFrame, text='平仓收费方式:',
                                  bg=rgb_to_hex(255, 255, 255), justify=tk.LEFT, anchor=tk.W, width=15)
        closeTypeLabel.pack(side=tk.LEFT)
        closeTypeChosen = ttk.Combobox(closeTypeFrame, state="readonly", textvariable=self.closeType)
        closeTypeChosen['values'] = ['固定值', '比例']
        closeTypeChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)
        closeTypeChosen.bind('<<ComboboxSelected>>', self.closeTypeUnitSet)

        closeFeeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        closeFeeFrame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(closeFeeFrame, text='平仓手续费(率):', bg=rgb_to_hex(255, 255, 255),
                 justify=tk.LEFT, anchor=tk.W, width=15).pack(side=tk.LEFT)
        closeFeeEntry = tk.Entry(closeFeeFrame, relief=tk.GROOVE, bd=2, textvariable=self.closeFee,
                                 validate="key", validatecommand=(self.testFlt, "%P"))

        closeFeeEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        closeFeeUnit = tk.Label(closeFeeFrame, text=' ', bg=rgb_to_hex(255, 255, 255),
                                     textvariable=self.closeTypeUnitVar, justify=tk.LEFT, anchor=tk.W, width=2)
        closeFeeUnit.pack(side=tk.LEFT, padx=5)

    def openTypeUnitSet(self, event=None):
        """开仓手续费类型选择事件"""
        openType = self.openType.get()
        if openType == "固定值":
            self.openTypeUnitVar.set(" ")
        if openType == "比例":
            self.openTypeUnitVar.set("%")

    def closeTypeUnitSet(self, event=None):
        closeType = self.closeType.get()
        if closeType == "固定值":
            self.closeTypeUnitVar.set(" ")
        if closeType == "比例":
            self.closeTypeUnitVar.set("%")

    def setTradeDir(self, frame):
        """设置交易方向"""
        dirFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        dirFrame.pack(fill=tk.X, padx=15, pady=5)
        dirLabel = tk.Label(dirFrame, text="交易方向:", bg=rgb_to_hex(255, 255, 255),
                            justif=tk.LEFT, anchor=tk.W, width=15)
        dirLabel.pack(side=tk.LEFT)

        dirChosen = ttk.Combobox(dirFrame, state="readonly", textvariable=self.dir)
        dirList = ['双向交易', '仅多头', '仅空头']
        dirChosen["values"] = dirList
        dirChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)

    def setSlippage(self, frame):
        """设置滑点损耗"""

        slipFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        slipFrame.pack(fill=tk.X, padx=15, pady=5)
        slipLabel = tk.Label(slipFrame, text='滑点损耗:', bg=rgb_to_hex(255, 255, 255),
                             justif=tk.LEFT, anchor=tk.W, width=15)
        slipLabel.pack(side=tk.LEFT)
        slipEntry = tk.Entry(slipFrame, relief=tk.GROOVE, bd=2, width=23, textvariable=self.slippage,
                             validate="key", validatecommand=(self.testContent, "%P"))
        slipEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)

    def setTrigger(self, frame):
        """触发方式"""
        triggerFrame = tk.LabelFrame(frame, text="触发方式", bg=rgb_to_hex(255, 255, 255), padx=5)
        triggerFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, padx=15, pady=5)

        tLeftFrame = tk.Frame(triggerFrame, bg=rgb_to_hex(255, 255, 255), padx=5)
        tRightFrame = tk.Frame(triggerFrame, bg=rgb_to_hex(255, 255, 255), padx=5)
        tLeftFrame.pack(fill=tk.Y, side=tk.LEFT, pady=2)
        tRightFrame.pack(fill=tk.Y, side=tk.RIGHT, pady=2)

        kLineFrame = tk.Frame(tLeftFrame, bg=rgb_to_hex(255, 255, 255), padx=5, pady=5)
        marketFrame = tk.Frame(tLeftFrame, bg=rgb_to_hex(255, 255, 255), padx=5, pady=5)
        tradeFrame = tk.Frame(tLeftFrame, bg=rgb_to_hex(255, 255, 255), padx=5, pady=5)
        cycleFrame = tk.Frame(tLeftFrame, bg=rgb_to_hex(255, 255, 255), padx=5, pady=5)

        for f in [kLineFrame, marketFrame, tradeFrame, cycleFrame]:
            f.pack(fill=tk.X, pady=2)
        # 周期
        cycleCheck = tk.Checkbutton(cycleFrame, text="每间隔", bg=rgb_to_hex(255, 255, 255), bd=2,
                                    anchor=tk.W, variable=self.isCycle, command=self.cycleCheckEvent)
        cycleCheck.pack(side=tk.LEFT, padx=5)

        self.cycleEntry = tk.Entry(cycleFrame, relief=tk.GROOVE, width=8, bd=2,
                                   textvariable=self.cycle, validate="key", validatecommand=(self.testContent, "%P"))
        # self.cycleEntry.config(state="disabled")
        self.cycleEntry.pack(side=tk.LEFT, fill=tk.X, padx=1)
        tk.Label(cycleFrame, text="毫秒执行代码（100的整数倍）", bg=rgb_to_hex(255, 255, 255),
                 anchor=tk.W, width=25).pack(side=tk.LEFT, expand=tk.NO, padx=1)

        # 定时
        tk.Label(tRightFrame, text="指定时刻", bg=rgb_to_hex(255, 255, 255),
                 anchor=tk.W, width=10).pack(side=tk.TOP, anchor=tk.W, expand=tk.NO, padx=5)
        timerFrame = tk.Frame(tRightFrame, bg=rgb_to_hex(255, 255, 255), padx=5, pady=5)
        timerFrame.pack(fill=tk.X, expand=tk.YES)
        self.timerText = tk.Text(timerFrame, bg=rgb_to_hex(255, 255, 255), bd=2, relief=tk.GROOVE,
                                 height=8, state="disabled")
        self.addScroll(timerFrame, self.timerText, xscroll=False)
        # self.timerText.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT, anchor=tk.W, padx=5)
        self.timerText.pack(fill=tk.BOTH, expand=tk.YES)


        self.timerText.bind("<Button-1>", self.timerTextEvent)

        tFrame = tk.Frame(tRightFrame, bg=rgb_to_hex(255, 255, 255), padx=5)
        tFrame.pack(fill=tk.X, pady=2)
        #TODO: DateEntry 控件创建很耗时
        # timer = DateEntry(tFrame, width=15, anchor=tk.W, background='darkblue', foreground="white", borderwidth=2,
        #         #                   year=2019)
        #         # timer.pack(side=tk.LEFT, pady=5)
        self.t = tk.StringVar()
        timer = tk.Entry(tFrame, relief=tk.GROOVE, width=12, bd=2, textvariable=self.t)
        timer.pack(side=tk.LEFT, fill=tk.X, padx=1)
        addBtn = tk.Button(tFrame, text="增加", relief=tk.FLAT, padx=2, bd=0, highlightthickness=1,
                           activebackground="lightblue", overrelief="groove", bg=rgb_to_hex(230, 230, 230),
                           command=self.addBtnEvent)
        addBtn.pack(side=tk.LEFT, expand=tk.NO, ipadx=10, padx=5)
        delBtn = tk.Button(tFrame, text="删除", relief=tk.FLAT, padx=2, bd=0, highlightthickness=1,
                           activebackground="lightblue", overrelief="groove", bg=rgb_to_hex(230, 230, 230),
                           command=self.delBtnEvent)
        delBtn.pack(side=tk.LEFT, expand=tk.NO, ipadx=10, padx=5)

        # K线触发
        self.kLineCheck = tk.Checkbutton(kLineFrame, text="K线触发", bg=rgb_to_hex(255, 255, 255),
                                         anchor=tk.W, variable=self.isKLine)
        self.kLineCheck.pack(side=tk.LEFT, padx=5)
        # self.kLineCheck.config(state="disabled")

        # 即时行情触发
        self.marketCheck = tk.Checkbutton(marketFrame, text="即时行情触发", bg=rgb_to_hex(255, 255, 255),
                                          anchor=tk.W, variable=self.isSnapShot)
        self.marketCheck.pack(side=tk.LEFT, padx=5)

        # 交易数据触发
        self.tradeCheck = tk.Checkbutton(tradeFrame, text="交易数据触发", bg=rgb_to_hex(255, 255, 255),
                                         anchor=tk.W, variable=self.isTrade)
        self.tradeCheck.pack(side=tk.LEFT, padx=5)

    def setCycleEntryState(self):
        if self.isCycle.get() == 0:
            self.cycleEntry.config(state="disabled", bg=rgb_to_hex(245, 245, 245))
        else:
            self.cycleEntry.config(state="normal", bg=rgb_to_hex(255, 255, 255))

    def addBtnEvent(self):
        """增加按钮回调事件"""
        timer = self.t.get()
        timers = (self.timerText.get('1.0', "end")).strip("\n")

        # pattern = re.compile(r'^(0?[0-9]|1[0-9]|2[0-3]):(0?[0-9]|[1-5][0-9]):(0?[0-9]|[1-5][0-9])$')
        pattern = re.compile(r'^([0-1][0-9]|2[0-3])([0-5][0-9])([0-5][0-9])$')
        if pattern.search(timer):
            if timer in timers:
                messagebox.showinfo("极星量化", "该时间点已经存在", parent=self)
                return
            self.setText(self.timerText, timer+'\n')
        else:
            messagebox.showinfo("极星量化", "时间格式为hhmmss", parent=self)

    def setText(self, widget, text):
        # TODO: Text控件中本身就含有"\n"字符
        widget.config(state="normal")
        widget.insert("end", text)
        widget.config(state="disabled")
        widget.see("end")
        widget.update()

    def delBtnEvent(self):
        """删除按钮回调事件"""
        line = self.timerText.index('insert').split(".")[0]
        tex = self.timerText.get(str(line)+'.0', str(line)+'.end')
        if not tex:
            if messagebox.showinfo(title="极星量化", message="请选择一个时间点", parent=self):
                return
        self.timerText.config(state="normal")
        self.timerText.delete(str(line)+'.0', str(line)+'.end+1c')
        self.timerText.config(state="disabled")

    def timerTextEvent(self, event):
        """timerText回调事件"""
        self.timerText.tag_configure("current_line", background=rgb_to_hex(0, 120, 215), foreground="white")
        self.timerText.tag_remove("current_line", 1.0, "end")
        self.timerText.tag_add("current_line", "current linestart", "current lineend")

    def cycleCheckEvent(self):
        isCycle = self.isCycle.get()
        if isCycle:
            self.cycleEntry.config(state="normal", bg=self.bgColorW)
            self.cycleEntry.focus_set()
            return
        self.cycleEntry.config(state="disabled", bg=self.bgColor)

    def SendOrderMode(self, frame):
        modeFrame = tk.Frame(frame, bg=rgb_to_hex(255, 255, 255))
        modeFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(modeFrame, text="发单时机: ", bg=rgb_to_hex(255, 255, 255),
                 anchor=tk.W, width=10).pack(side=tk.LEFT, expand=tk.NO, padx=5)
        # 实时发单
        self.RealTimeRadio = tk.Radiobutton(modeFrame, text="实时发单", bg=rgb_to_hex(255, 255, 255),
                                            anchor=tk.W, value=0, variable=self.sendOrderMode)
        self.RealTimeRadio.pack(side=tk.LEFT, padx=10)
        # K线稳定后发单
        self.steadyRadio = tk.Radiobutton(modeFrame, text="K线稳定后发单", bg=rgb_to_hex(255, 255, 255),
                                          anchor=tk.W, value=1, variable=self.sendOrderMode)
        self.steadyRadio.pack(side=tk.LEFT, padx=50)

    def setRunMode(self, frame):
        """是否实盘运行"""
        runModeFrame = tk.Frame(frame, bg=rgb_to_hex(255, 255, 255))
        runModeFrame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        tk.Label(runModeFrame, text="运行模式: ", bg=rgb_to_hex(255, 255, 255),
                 anchor=tk.W, width=10).pack(side=tk.LEFT, expand=tk.NO, padx=5)

        # 实盘运行
        self.modeCheck = tk.Checkbutton(runModeFrame, text="实盘运行", bg=rgb_to_hex(255, 255, 255),
                                        anchor=tk.W, variable=self.isActual)
        self.modeCheck.pack(side=tk.LEFT, padx=10)
        # 是否连续运行
        # self.continueCheck = tk.Checkbutton(runModeFrame, text="连续运行", bg=rgb_to_hex(255, 255, 255),
        #                                     anchor=tk.W, variable=self.isContinue)
        # self.continueCheck.pack(side=tk.LEFT, padx=5)

        # 发单报警
        self.alarmCheck = tk.Checkbutton(runModeFrame, text="发单报警", bg=rgb_to_hex(255, 255, 255),
                                         anchor=tk.W, variable=self.isAlarm)
        self.alarmCheck.pack(side=tk.LEFT, padx=50)

    def setSendOrderLimit(self, frame):
        sendModeFrame = tk.LabelFrame(frame, text="发单设置", bg=rgb_to_hex(255, 255, 255), padx=5)
        sendModeFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, padx=15, pady=15)

        self.setContinueOpenTimes(sendModeFrame)
        self.setOpenTimes(sendModeFrame)
        self.setCanClose(sendModeFrame)
        self.setCanOpen(sendModeFrame)
        # self.setHelp(setFrame)
        # self.bindEvent()

    # 运行设置
    def setOpenTimes(self, frame):
        """每根K线同向开仓次数"""
        self.openTimesFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.openTimesFrame.pack(fill=tk.X, pady=6)

        self.otCheck = tk.Checkbutton(self.openTimesFrame, text="每根K线同向开仓次数:", bg=rgb_to_hex(255, 255, 255),
                                      anchor=tk.W, variable=self.isOpenTimes)
        self.otCheck.pack(side=tk.LEFT, padx=10)

        self.timesEntry = tk.Entry(self.openTimesFrame, relief=tk.GROOVE, bd=2, width=8, textvariable=self.openTimes,
                                   validate="key", validatecommand=(self.testContent, "%P"))
        # self.timesEntry.insert(tk.END, 1)
        self.timesEntry.pack(side=tk.LEFT, fill=tk.X, padx=1)
        timesLabel = tk.Label(self.openTimesFrame, text='次(1-100)', bg=rgb_to_hex(255, 255, 255),
                 justif=tk.LEFT, anchor=tk.W, width=10)
        timesLabel.pack(side=tk.LEFT, expand=tk.NO, padx=1)

    def setContinueOpenTimes(self, frame):
        """最大连续同向开仓次数"""

        self.conTimesFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.conTimesFrame.pack(fill=tk.X, pady=6)

        self.conCheck = tk.Checkbutton(self.conTimesFrame, text="最大连续同向开仓次数:", bg=rgb_to_hex(255, 255, 255),
                                       anchor=tk.W, onvalue=1, offvalue=0, variable=self.isConOpenTimes)
        self.conCheck.pack(side=tk.LEFT, padx=10)

        self.conTimesEntry = tk.Entry(self.conTimesFrame, relief=tk.GROOVE, bd=2, width=8, textvariable=self.conOpenTimes,
                                      validate="key", validatecommand=(self.testContent, "%P"))
        self.conTimesEntry.pack(side=tk.LEFT, fill=tk.X, padx=1)
        conTimesLabel = tk.Label(self.conTimesFrame, text='次(1-100)', bg=rgb_to_hex(255, 255, 255),
                 justif=tk.LEFT, anchor=tk.W, width=10)
        conTimesLabel.pack(side=tk.LEFT, expand=tk.NO, padx=1)

    def setCanClose(self, frame):
        """开仓的当前K线不允许平仓"""
        self.canCloseFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.canCloseFrame.pack(fill=tk.X, pady=6)

        self.canCloseCheck = tk.Checkbutton(self.canCloseFrame, text="开仓的当前K线不允许反向下单",
                                            bg=rgb_to_hex(255, 255, 255), anchor=tk.W, variable=self.canClose)
        self.canCloseCheck.pack(side=tk.LEFT, padx=10)

    def setCanOpen(self, frame):
        """平仓的当前K线不允许开仓"""
        self.canOpenFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.canOpenFrame.pack(fill=tk.X, pady=6)

        self.canOpenCheck = tk.Checkbutton(self.canOpenFrame, text="平仓的当前K线不允许开仓",
                                           bg=rgb_to_hex(255, 255, 255), anchor=tk.W, variable=self.canOpen)
        self.canOpenCheck.pack(side=tk.LEFT, padx=10)

    # TODO:删掉
    def setHelp(self, frame):
        """选项说明"""
        self.helpText = tk.StringVar()  # TODO:把所有变量都放到init初始化中

        self.helpFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.helpFrame.pack(fill=tk.X, padx=5, pady=20)

        self.helpT = tk.Text(self.helpFrame, state="disabled", width=50, height=5)
        self.helpT.pack(side=tk.LEFT, fill=tk.X, padx=98)

    # TODO: 删除
    def onCheckBtnEnterEvent(self, event, checkBtn):
        if checkBtn == self.otCheck:
            self.setHelpText(OpenTimesHelp)
        elif checkBtn == self.conCheck:
            self.setHelpText(ContinueOpenTimesHelp)
        elif checkBtn == self.canOpenCheck:
            self.setHelpText(CanClose)
        else:
            self.setHelpText(CanOpen)

    # TODO: 删除
    def onCheckBtnLeaveEvent(self, event, checkBtn):
        self.helpT.config(state="normal")
        self.helpT.delete('1.0', 'end')
        self.helpT.config(state="disabled")
        self.helpT.update()

    # TODO: 删除
    def bindEvent(self):
        """运行设置的checkbutton绑定事件"""
        for cb in [self.otCheck, self.conCheck, self.canCloseCheck, self.canOpenCheck]:
            cb.bind("<Enter>", self.handlerAdaptor(self.onCheckBtnEnterEvent, checkBtn=cb))
            cb.bind("<Leave>", self.handlerAdaptor(self.onCheckBtnLeaveEvent, checkBtn=cb))

    # TODO: 删除
    def setHelpText(self, text=""):
        self.helpT.config(state="normal")
        self.helpT.delete('1.0', 'end')
        self.helpT.insert("end", text + "\n")
        self.helpT.config(state="disabled")
        self.helpT.update()

    def addButton(self, frame):
        enterFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        enterFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=5)
        cancelButton = tk.Button(enterFrame, text="取消", relief=tk.FLAT, bg=rgb_to_hex(230, 230, 230),
                                 activebackground="lightblue", highlightbackground="red",
                                 overrelief="groove",
                                 command=self.cancel)
        cancelButton.pack(side=tk.RIGHT, ipadx=20, padx=5, pady=5)

        enterButton = tk.Button(enterFrame, text="确定", relief=tk.FLAT,
                                activebackground="lightblue",
                                overrelief="groove",
                                command=self.enter, bg=rgb_to_hex(230, 230, 230))
        enterButton.pack(side=tk.RIGHT, ipadx=20, padx=5, pady=5)

    def enter(self):
        # TODO: IntVar()显示时会补充一个0？？？
        user = self.user.get()
        initFund = self.initFund.get()
        defaultType = self.defaultType.get()
        defaultQty = self.defaultQty.get()
        minQty = self.minQty.get()
        # hedge = self.hedge.get()
        margin = self.margin.get()

        openType = self.openType.get()
        closeType = self.closeType.get()
        openFee = self.openFee.get()
        closeFee = self.closeFee.get()

        tradeDirection = self.dir.get()
        slippage = self.slippage.get()
        #TODO: contract另外保存了一个变量，不再分解了
        # contractInfo = self.contract.get()

        # contract = (contractInfo.rstrip("\n")).split("\n")

        # if len(contract) == 0:
        #     messagebox.showinfo("提示", "未选择合约")
        #     return
        # else:
        #     contractInfo = (contract.rstrip(", ")).split(", ")

        timer = self.timerText.get('1.0', "end-1c")   # 时间

        isCycle = self.isCycle.get()
        cycle = self.cycle.get()
        isKLine = self.isKLine.get()
        isSnapShot = self.isSnapShot.get()
        isTrade = self.isTrade.get()

        # beginDate = self.beginDate.get()
        # # beginDateFormatter = parseYMD(beginDate)
        # fixQty = self.fixQty.get()
        # sampleVar = self.sampleVar.get()

        sendOrderMode = self.sendOrderMode.get()  # 发单时机： 0. 实时发单 1. K线稳定后发单

        isActual = self.isActual.get()
        isAlarm  = self.isAlarm.get()
        # isContinue = self.isContinue.get()
        isOpenTimes = self.isOpenTimes.get()
        openTimes = self.openTimes.get()

        isConOpenTimes = self.isConOpenTimes.get()

        conOpenTimes = self.conOpenTimes.get()
        canClose = self.canClose.get()
        canOpen = self.canOpen.get()

        # -------------转换定时触发的时间形式--------------------------
        time = timer.split("\n")
        timerFormatter = []
        for t in time:
            if t:
                timerFormatter.append(t)

        if float(initFund) < 1000:
            messagebox.showinfo("极星量化", "初始资金不能小于1000元", parent=self)
            self.initFundEntry.focus_set()
            self.toFundFrame()
            return

        if cycle == "":
            messagebox.showinfo("极星量化", "定时触发周期不能为空", parent=self)
            self.cycleEntry.focus_set()
            self.toRunFrame()
            return
        elif int(cycle) % 100 != 0:
            messagebox.showinfo("极星量化", "定时触发周期为100的整数倍", parent=self)
            self.cycleEntry.focus_set()
            self.toRunFrame()
            return
        else:
            pass

        if minQty == "":
            messagebox.showinfo("极星量化", "最小下单量不能为空", parent=self)
            return
        elif int(minQty) > MAXSINGLETRADESIZE:
            messagebox.showinfo("极星量化", "最小下单量不能大于1000", parent=self)
            self.minQtyEntry.focus_set()
            self.toFundFrame()
            return
        else:
            pass

        if isConOpenTimes:
            if conOpenTimes == '' or int(conOpenTimes) < 1 or int(conOpenTimes) > 100:
                messagebox.showinfo("极星量化", "最大连续同向开仓次数必须介于1-100之间", parent=self)
                self.conTimesEntry.focus_set()
                self.toSampFrame()
                return

        if isOpenTimes:
            if openTimes == '' or int(openTimes) < 1 or int(openTimes) > 100:
                messagebox.showinfo("极星量化", "每根K线同向开仓次数必须介于1-100之间", parent=self)
                self.timesEntry.focus_set()
                self.toSampFrame()
                return

        # 用户是否确定用新参数重新运行
        if self._paramFlag:
            userSlt = messagebox.askokcancel("提示", "点确定后会重新运行策略", parent=self)
            if not userSlt:
                return

        # TODO: 合约设置，K线类型， K线周期、运算起始点设置
        # 多合约信息：
        contsInfo = []
        for item in self.contTree.get_children():
            contValues = self.contTree.item(item)['values']
            contsInfo.append(contValues)

            # kLineTypeDict = {
            #     "分时": 't',
            #     "分笔": 'T',
            #     "秒线": 'S',
            #     "分钟": 'M',
            #     "小时": 'H',
            #     "日线": 'D',
            #     "周线": 'W',
            #     "月线": 'm',
            #     "年线": 'Y'
            # }

            kLineTypeDict = {
                "分笔": 'T',
                "秒"  : 'T',
                "分钟": 'M',
                "日线": 'D',
            }

            contCode     = contValues[0]
            kTypeValue   = kLineTypeDict[contValues[1]]
            kSliceValue  = int(contValues[2])

            samValue = ''
            if contValues[3] == "所有K线":
                samValue = 'A'
            elif contValues[3] == "不执行历史K线":
                samValue = 'N'
            elif isinstance(contValues[3], str):
                if not contValues[3].find("-") == -1:  # 日期
                    temp = "".join(contValues[3].split("-"))
                    samValue = temp
            elif isinstance(contValues[3], int):
                samValue = contValues[3]

            self._strConfig.setBarInfoInSample(contCode, kTypeValue, kSliceValue, samValue)

        # K线触发
        if isKLine:
            self._strConfig.setTrigger(5)
        # 即时行情触发
        if isSnapShot:
            self._strConfig.setTrigger(1)
        # 交易数据触发
        if isTrade:
            self._strConfig.setTrigger(2)
        # 周期触发
        if isCycle:
            self._strConfig.setTrigger(3, int(cycle))
        # 指定时刻
        if timer:
            self._strConfig.setTrigger(4, timerFormatter)

        # 发单设置
        if sendOrderMode == 0:
            self._strConfig.setOrderWay('1')
        else:
            self._strConfig.setOrderWay('2')

        # 连续运行
        # self.config["RunMode"]["Simulate"]["Continues"] = True
        # 运行模式
        if isActual:
            self._strConfig.setActual()
        # 发单报警
        self._strConfig.setAlarm(True) if int(isAlarm) else self._strConfig.setAlarm(False)
        # 账户
        #TODO: user类型对不对呢？
        self._strConfig.setUserNo(user)
        # 初始资金
        self._strConfig.setInitCapital(int(initFund))
        # 交易方向
        if tradeDirection == "双向交易":
            self._strConfig.setTradeDirection(0)
        elif tradeDirection == "仅多头":
            self._strConfig.setTradeDirection(1)
        else:
            self._strConfig.setTradeDirection(2)

        # 默认下单量
        if defaultType == "按固定合约数":
            self._strConfig.setOrderQty("1", int(defaultQty))
        elif defaultType == "按固定资金":
            self._strConfig.setOrderQty("2", float(defaultQty))
        elif defaultType == "按资金比例":
            self._strConfig.setOrderQty("3", float(defaultQty) / 100)
        else:
            raise Exception("默认下单量类型异常")

        # 最小下单量
        self._strConfig.setMinQty(int(minQty))
        # 投保标志
        # if hedge == "投机":
        #     self._strConfig.setHedge("T")
        # elif hedge == "套利":
        #     self._strConfig.setHedge("B")
        # elif hedge == "保值":
        #     self._strConfig.setHedge("S")
        # elif hedge == "做市":
        #     self._strConfig.setHedge("M")
        # else:
        #     raise Exception("投保标志异常")

        # # 保证金率
        # TODO: margin类型没有设置！！！！！
        # 比例
        self._strConfig.setMargin('R', float(margin)/100)

        # 开仓按比例收费
        if openType == "比例":
            self._strConfig.setTradeFee('O', 'R', float(openFee) / 100)
        else:
            self._strConfig.setTradeFee('O', 'F', float(openFee))
        # 平仓按比例收费
        if closeType == "比例":
            self._strConfig.setTradeFee('C', 'R', float(closeFee)/100)
        else:
            self._strConfig.setTradeFee('C', 'F', float(closeFee))
        # 平今手续费
        # TODO：平今手续费没有设置
        # self.config["Money"]["CloseTodayFee"]["Type"] = "F"
        # self.config["Money"]["CloseTodayFee"]["Type"] = 0
        self._strConfig.setTradeFee('T', "F", 0)

        # 滑点损耗
        self._strConfig.setSlippage(float(slippage))

        # 发单设置
        openT = int(openTimes) if isOpenTimes else -1           # 每根K线同向开仓次数
        cOpenT = int(conOpenTimes) if isConOpenTimes else -1    # 最大连续同向开仓次数
        self._strConfig.setLimit(openT, cOpenT, canClose, canOpen)

        # 用户参数
        params = {}
        for item in self.paramTree.get_children():
            paramValues = self.paramTree.item(item)['values']
            params[paramValues[0]] = (paramValues[1], paramValues[3])

        self._strConfig.setParams(params)

        self.config = self._strConfig.getConfig()
        #print("-----------: ", self.config)


        # -------------保存用户配置--------------------------
        # strategyPath = self._control.getEditorText()["path"]
        strategyPath = self._strategyPath
        userConfig = {
            strategyPath: {
                VUser: user,
                VInitFund: initFund,
                VDefaultType: defaultType,
                VDefaultQty: defaultQty,
                VMinQty: minQty,
                # VHedge: hedge,
                VMargin: margin,
                VOpenType: openType,
                VCloseType: closeType,
                VOpenFee: openFee,
                VCloseFee: closeFee,
                VDirection: tradeDirection,
                VSlippage: slippage,
                VTimer: timer,
                VIsCycle: isCycle,
                VCycle: cycle,
                VIsKLine: isKLine,
                VIsMarket: isSnapShot,
                VIsTrade: isTrade,

                # VSampleVar: sampleVar,
                # VBeginDate: beginDate,
                # VFixQty: fixQty,

                VSendOrderMode: sendOrderMode,
                VIsActual: isActual,
                VIsAlarm: isAlarm,
                VIsOpenTimes: isOpenTimes,
                VOpenTimes: openTimes,
                VIsConOpenTimes: isConOpenTimes,
                VConOpenTimes: conOpenTimes,
                VCanClose: canClose,
                VCanOpen: canOpen,

                #VParams: params,
                VContSettings: contsInfo
            }
        }

        # 将配置信息保存到本地文件
        self.writeConfig(userConfig)

        self.destroy()

    def cancel(self):
        self.config = {}
        self.destroy()

    def readConfig(self):
        """读取配置文件"""
        if os.path.exists(r"./config/loadconfigure.json"):
            with open(r"./config/loadconfigure.json", "r", encoding="utf-8") as f:
                try:
                    result = json.loads(f.read())
                except json.decoder.JSONDecodeError:
                    return None
                else:
                    return result
        else:
            filePath = os.path.abspath(r"./config/loadconfigure.json")
            f = open(filePath, 'w')
            f.close()

    def writeConfig(self, configure):
        """写入配置文件"""
        # 将文件内容追加到配置文件中
        try:
            config = self.readConfig()
        except:
            config = None
        if config:
            for key in configure:
                config[key] = configure[key]
                break
        else:
            config = configure

        with open(r"./config/loadconfigure.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(config, indent=4))


class SelectContractWin(QuantToplevel, QuantFrame):

    # exchangeList = ["CFFEX", "CME", "DCE", "SGE", "SHFE", "ZCE", "SPD", "INE", "NYMEX", "SSE", "SZSE"]
    exchangeList = ["SPD", "ZCE", "DCE", "SHFE", "INE", "CFFEX", "SSE", "SZSE", "SGE", "CME", "COMEX", "NYMEX", "HKEX"]
    commodityType = {"P": "现货", "Y": "现货", "F": "期货", "O": "期权",
                     "S": "跨期套利", "M": "品种套利", "s": "", "m": "",
                     "y": "", "T": "股票", "X": "外汇",
                     "I": "外汇", "C": "外汇"}
    # 外盘保留品种
    FCommodity = {"NYMEX": ["美原油"], "COMEX": ["美黄金"], "HKEX": ["恒指", "小恒指", "H股指"], "CME": ["小标普"]}

    def __init__(self, master, exchange, commodity, contract):
        super().__init__(master)
        self._master = master
        self._selectCon = []   # 所选合约列表

        self._exchange = exchange
        self._commodity = commodity
        self._contract = contract

        # print(datetime.now().strftime('%H:%M:%S.%f'))

        self.title("选择合约")
        self.attributes("-toolwindow", 1)

        self.topFrame = tk.Frame(self, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        self.topFrame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)

        self.setPos()
        self.createWidgets(self.topFrame)

    def getSelectCon(self):
        return self._selectCon

    def setPos(self):
        # TODO: setPos需要重新设计下么？
        # 获取主窗口大小和位置，根据主窗口调整输入框位置
        ws = self._master.winfo_width()
        hs = self._master.winfo_height()
        wx = self._master.winfo_x()
        wy = self._master.winfo_y()

        #计算窗口位置
        w, h = 870, 560
        x = (wx + ws/2) - w/2
        y = (wy + hs/2) - h/2

        #弹出输入窗口，输入文件名称
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.minsize(870, 560)
        self.resizable(0, 0)

    def createWidgets(self, frame):
        topFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        topFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES, anchor=tk.N)
        self.addExchange(topFrame)
        self.addContract(topFrame)
        self.addText(topFrame)
        self.addButton(frame)

    def addExchange(self, frame):
        exchangeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        exchangeFrame.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.W)

        self.exchangeTree = ttk.Treeview(exchangeFrame, show="tree")
        self.contractScroll = self.addScroll(exchangeFrame, self.exchangeTree, xscroll=False)
        # for exch in self._exchange:
        #     if exch["ExchangeNo"] in self.exchangeList:
        #         exchangeId = self.exchangeTree.insert("", tk.END,
        #                                               text=exch["ExchangeNo"] + "【" + exch["ExchangeName"] + "】",
        #                                               values=exch["ExchangeNo"])

        # for exchangeNo in self.exchangeList:
        #     for exch in self._exchange:
        #         if exch["ExchangeNo"] == exchangeNo:
        #             exchangeId = self.exchangeTree.insert("", tk.END,
        #                                                  text=exch["ExchangeNo"] + "【" + exch["ExchangeName"] + "】",
        #                                                  values=exch["ExchangeNo"])
        #
        #             for commodity in self._commodity:
        #                 if commodity["ExchangeNo"] == exch["ExchangeNo"] and commodity["CommodityType"] in self.commodityType.keys():
        #                     if commodity["ExchangeNo"] == "SPD":
        #                         text = commodity["CommodityName"]
        #                     else:
        #                         text = commodity["CommodityName"] + " [" + self.commodityType[commodity["CommodityType"]] + "]"
        #                     commId = self.exchangeTree.insert(exchangeId, tk.END,
        #                                                       text=text,
        #                                                       values=commodity["CommodityNo"])

        for exchangeNo in self.exchangeList:
            exchange = self._exchange.loc[self._exchange.ExchangeNo == exchangeNo]
            for _, exch in exchange.iterrows():
                exchangeId = self.exchangeTree.insert("", tk.END,
                                                      text=exch.ExchangeNo + "【" + exch.ExchangeName + "】",
                                                      values=exch.ExchangeNo)

            commodity = self._commodity.loc[self._commodity.ExchangeNo == exchangeNo]
            for _, comm in commodity.iterrows():
                # 仅保留外盘支持的品种
                if exchangeNo in self.FCommodity:
                    if comm.CommodityName not in self.FCommodity[exchangeNo]:
                        continue

                if comm.CommodityType in self.commodityType.keys():
                    if comm.ExchangeNo == "SPD":
                        text = comm.CommodityName
                    else:
                        text = comm.CommodityName + " [" + self.commodityType[comm.CommodityType] + "]"
                    commId = self.exchangeTree.insert(exchangeId, tk.END,
                                                      text=text,
                                                      values=comm.CommodityNo)

        self.exchangeTree.pack(fill=tk.BOTH, expand=tk.YES)
        self.exchangeTree.bind("<ButtonRelease-1>", self.updateContractFrame)

    def addContract(self, frame):
        contractFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        contractFrame.pack(side=tk.LEFT, fill=tk.Y, anchor=tk.W)

        self.contractTree = ttk.Treeview(contractFrame, show='tree')
        self.contractScroll = self.addScroll(contractFrame, self.contractTree, xscroll=False)
        self.contractTree.pack(side=tk.LEFT, fill=tk.Y)
        self.contractTree.bind("<Double-Button-1>", self.addSelectedContract)

    def addText(self, frame):
        textFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        textFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES, anchor=tk.W)
        self.contractText = ContractText(textFrame)
        self.contractText.pack(side=tk.LEFT, fill=tk.Y)

        self.contractText.bind("<Double-Button-1>", self.deleteSelectedContract)

    def addButton(self, frame):
        #TODO: 和加载的addButton代码相同
        enterFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        enterFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=5)
        cancelButton = tk.Button(enterFrame, text="取消", relief=tk.FLAT, bg=rgb_to_hex(230, 230, 230),
                                 activebackground="lightblue", highlightbackground="red",
                                 overrelief="groove",
                                 command=self.cancel)
        cancelButton.pack(side=tk.RIGHT, ipadx=20, padx=5, pady=5)

        enterButton = tk.Button(enterFrame, text="确定", relief=tk.FLAT,
                                activebackground="lightblue",
                                overrelief="groove",
                                command=self.enter, bg=rgb_to_hex(230, 230, 230))
        enterButton.pack(side=tk.RIGHT, ipadx=20, padx=5, pady=5)

    def enter(self):
        self._master.codeEntry.config(state="normal")
        self._master.codeEntry.delete(0, tk.END)

        # 多合约
        # for con in self._selectCon:
        #     self._master.contractEntry.insert(tk.END, con)
        if len(self._selectCon) > 1:
            self._master.codeEntry.insert(tk.END, self._selectCon[0] + ", ...")
        else:
            # self._master.contractEntry.insert(tk.END, self._selectCon[0])
            self._master.codeEntry.insert(tk.END, self._selectCon)
        self._master.setUserContract(self._selectCon)

        self._master.codeEntry.config(state="disabled")

        # 不加self._master.display()会出现选择合约确定后设置窗口后移
        # self._master.focus()
        self.destroy()
        self._master.display()

    def cancel(self):
        self.destroy()
        self._master.display()

    def updateContractFrame(self, event):
        contractItems = self.contractTree.get_children()
        for item in contractItems:
            self.contractTree.delete(item)

        select = event.widget.selection()

        for idx in select:
            if self.exchangeTree.parent(idx):
                commodityNo = self.exchangeTree.item(idx)['values']
                directory_id = self.exchangeTree.parent(idx)
                exchangeNo = self.exchangeTree.item(directory_id)['values']

                # 将F和Z合并到一个节点下
                commodityNoZ = commodityNo[0]
                temp = commodityNo[0].split("|")
                if temp[1] == "F":
                    temp[1] = "Z"
                    commodityNoZ = "|".join(temp)

                contract = self._contract.loc[
                    (self._contract.ExchangeNo == exchangeNo[0])
                    & (
                        (self._contract.CommodityNo == commodityNo[0])
                        |
                        (self._contract.CommodityNo == commodityNoZ)
                    )
                        ]
                for index, row in contract.iterrows():
                    self.contractTree.insert("", tk.END, text=row["ContractNo"], values=row["CommodityNo"])

    def addSelectedContract(self, event):
        select = event.widget.selection()
        # cont = self.contractText.get_text()
        # contList = (self.contractText.get_text()).strip("\n")
        # contList = ((self.contractText.get_text()).strip("\n")).split("\n")
        contList = ((self.contractText.get_text()).strip("\n")).split()


        if len(contList) > 0:
            messagebox.showinfo("提示", "选择合约数量不能超过1个", parent=self)
            return

        for idx in select:
            contractNo = self.contractTree.item(idx)["text"]
            if contractNo in contList:
                return
            else:
                self.contractText.setText(contractNo)
                self._selectCon.append(contractNo)

    def deleteSelectedContract(self, event):
        line = self.contractText.index('insert').split(".")[0]
        tex = self.contractText.get(str(line)+'.0', str(line)+'.end')
        if not tex:
            return
        # 将合约从self._selectCon中删除
        self._selectCon.remove(tex)
        self.contractText.config(state="normal")
        self.contractText.delete(str(line)+'.0', str(line)+'.end+1c')
        self.contractText.config(state="disabled")


class AddContWin(QuantToplevel, QuantFrame):

    """增加合约窗口"""
    def __init__(self, master, exchange, commodity, contract):
        super().__init__(master)
        self._master = master
        self.title("商品属性")
        self.attributes("-toolwindow", 1)

        self._exchange = pd.DataFrame(exchange).drop_duplicates()
        self._commodity = pd.DataFrame(commodity).drop_duplicates()
        self._contract = pd.DataFrame(contract).drop_duplicates()

        # 用于保存用户所选的用户合约
        self.userContList = []

        # 用于记录需要修改的合约对应的树控件的item
        self.selectedItem = ''

        self.setPos()

        self.contCode    = tk.StringVar()  # 合约
        self.kLineType   = tk.StringVar()  # K线类型
        self.kLineSlice  = tk.StringVar()  # K线周期
        self.sampleVar   = tk.IntVar()     # 样本设置
        self.beginDate   = tk.StringVar()  # 起始日期
        self.fixQty      = tk.StringVar()  # 固定根数

        self.margin      = tk.StringVar()  # 保证金
        self.openType    = tk.IntVar()     # 开仓收费方式
        self.closeType   = tk.IntVar()     # 平仓收费方式
        self.openFee     = tk.StringVar()  # 开仓手续费
        self.closeFee    = tk.StringVar()  # 平仓手续费

        # 根据选择内容设置标签内容变量
        self.unitVar = tk.StringVar()
        self.openTypeUnitVar = tk.StringVar()
        self.closeTypeUnitVar = tk.StringVar()

        self.testFlt = self.register(self.testFloat)
        self.testContent = self.register(self.testDigit)

        self.topFrame = tk.Frame(self, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        self.topFrame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)
        self.createWidgets(self.topFrame)

        self._initArgs()

    def dropDuplicate(self, data):
        """去重"""
        pass

    def _initArgs(self):
        self.margin.set("5")
        # K线类型
        self.kLineType.set("分钟")
        # K线周期
        self.kLineSlice.set("1")
        # 样本设置
        self.sampleVar.set(2)
        self.fixQty.set(2000)

        self.openFee.set("1")
        self.closeFee.set("1")
        self.openType.set(0)
        self.closeType.set(0)

    def setPos(self):
        # TODO: setPos需要重新设计下么？
        # 获取主窗口大小和位置，根据主窗口调整输入框位置
        ws = self._master.winfo_width()
        hs = self._master.winfo_height()
        wx = self._master.winfo_x()
        wy = self._master.winfo_y()

        #计算窗口位置
        w, h = 400, 360
        x = (wx + ws/2) - w/2
        y = (wy + hs/2) - h/2

        #弹出输入窗口，输入文件名称
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.minsize(400, 260)
        self.resizable(0, 0)

    def setWinValue(self, item, value):
        """设置增加多合约信息时界面的参数值"""
        self.selectedItem = item
        self.contCode.set(value[0])
        self.kLineType.set(value[1])
        # 防止用户设置中分笔的周期设置为不为零的值
        self.kLineSlice.set("0") if value[1] == "分笔" else self.kLineSlice.set(value[2])
        # 设置运算起始点状态（转换）
        samV = {
            "所有K线"       : 0,
            "不执行历史K线" : 3
        }

        if value[3] in samV.keys():
            self.sampleVar.set(samV[value[3]])
        elif isinstance(value[3], str):
            if not value[3].find("-") == -1:   # 日期
                self.sampleVar.set(1)
                beginDate = "".join(value[3].split("-"))
                self.beginDate.set(beginDate)
        elif isinstance(value[3], int):
            self.fixQty.set(str(value[3]))
            self.sampleVar.set(2)
        else:
            pass

    def createWidgets(self, frame):
        self.setContCode(frame)
        self.setKLineType(frame)
        self.setKLineSlice(frame)
        self.setSample(frame)
        # self.setMargin(frame)
        # self.setCommision(frame)
        # self.setSeperator(frame)
        self.addButton(frame)

    def setContCode(self, frame):
        """设置商品代码"""
        contCodeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        contCodeFrame.pack(fill=tk.X, padx=15, pady=2)

        codeLabel = tk.Label(contCodeFrame, text='商品代码:', bg=rgb_to_hex(245, 245, 245),
                                justif=tk.LEFT, anchor=tk.W, width=15)
        codeLabel.pack(side=tk.LEFT)
        self.codeEntry = tk.Entry(contCodeFrame, relief=tk.GROOVE, bd=2, textvariable=self.contCode)
        self.codeEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)

        self.contractButton = tk.Button(contCodeFrame, text="选择", relief=tk.FLAT,
                                   activebackground="lightblue",
                                   overrelief="groove",
                                   bg=rgb_to_hex(230, 230, 230),
                                   command=self.selectContract)
        self.contractButton.pack(side=tk.LEFT, ipadx=5, padx=5)

    def setKLineType(self, frame):
        kLineTypeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        kLineTypeFrame.pack(fill=tk.NONE, anchor=tk.W, padx=15, pady=2)
        kLineTypeLabel = tk.Label(kLineTypeFrame, text='K线类型:', bg=rgb_to_hex(245, 245, 245),
                                  justify=tk.LEFT, anchor=tk.W, width=15)
        kLineTypeLabel.pack(side=tk.LEFT)

        self.kLineTypeChosen = ttk.Combobox(kLineTypeFrame, state="readonly", textvariable=self.kLineType, width=17)
        self.kLineTypeChosen['values'] = ['分笔', '秒', '分钟', '日线']
        self.kLineTypeChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.kLineTypeChosen.bind("<<ComboboxSelected>>", self.kLineChosenCallback)

    def setKLineSlice(self, frame):
        self.klineSliceFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        self.klineSliceFrame.pack(fill=tk.X, padx=15, pady=2)
        klineSliceLabel = tk.Label(self.klineSliceFrame, text="K线周期:", bg=rgb_to_hex(245, 245, 245),
                                   justify=tk.LEFT, anchor=tk.W, width=15)
        klineSliceLabel.pack(side=tk.LEFT)

        self.klineSliceChosen = ttk.Combobox(self.klineSliceFrame, state="readonly",
                                             textvariable=self.kLineSlice, width=17)
        self.klineSliceChosen["values"] = ['1', '2', '3', '5', '10', '15', '30', '60', '120']
        self.klineSliceChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)
        self.klineSliceChosen.bind("<<ComboboxSelected>>", self.kLineChosenCallback)

    def kLineChosenCallback(self, event):
        """k线周期和k线类型选择回调函数"""
        type = self.kLineType.get()
        slice = self.kLineSlice.get()
        if slice == "0":
            slice = "1"
        if type == "分笔":
            self.kLineSlice.set("0")
            self.klineSliceChosen.config(state="disabled")
            return
        self.kLineSlice.set(slice)
        self.klineSliceChosen.config(state="normal")

    def setSample(self, frame):
        """设置样本"""
        sampFrame = tk.LabelFrame(frame, text="运算起始点", bg=rgb_to_hex(245, 245, 245), padx=5, width=300)
        # sampFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, padx=15, pady=5)
        # sampFrame.pack_propagate(0)
        sampFrame.pack(side=tk.TOP, fill=tk.NONE, expand=tk.FALSE, padx=15, pady=5)
        allKFrame = tk.Frame(sampFrame, bg=rgb_to_hex(245, 245, 245), padx=5)
        allKFrame.pack(side=tk.TOP, fill=tk.X, pady=5)
        beginFrame = tk.Frame(sampFrame, bg=rgb_to_hex(245, 245, 245), padx=5)
        beginFrame.pack(side=tk.TOP, fill=tk.X, pady=5)
        fixFrame = tk.Frame(sampFrame, bg=rgb_to_hex(245, 245, 245), padx=5)
        fixFrame.pack(side=tk.TOP, fill=tk.X, pady=5)
        hisFrame = tk.Frame(sampFrame, bg=rgb_to_hex(245, 245, 245), padx=5)
        hisFrame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # 所有K线
        allKRadio = tk.Radiobutton(allKFrame, text="所有K线", bg=rgb_to_hex(245, 245, 245),
                                   value=0, anchor=tk.W, variable=self.sampleVar)  # self.isAllK
        allKRadio.pack(side=tk.LEFT, padx=5)

        # 起始日期
        self.dateRatio = tk.Radiobutton(beginFrame, text="起始日期", bg=rgb_to_hex(245, 245, 245),
                                        value=1, anchor=tk.W, variable=self.sampleVar)  # self.isBeginDate
        self.dateRatio.pack(side=tk.LEFT, padx=5)

        date_ = tk.Entry(beginFrame, relief=tk.GROOVE, bd=2, width=10,
                         textvariable=self.beginDate, validate="key", validatecommand=(self.testContent, "%P"))
        date_.pack(side=tk.LEFT, fill=tk.X, padx=1)
        date_.bind("<ButtonRelease-1>", self.dateSelectEvent)
        tk.Label(beginFrame, text="(格式: YYYYMMDD)", bg=rgb_to_hex(245, 245, 245),
                 anchor=tk.W, width=18).pack(side=tk.LEFT, expand=tk.NO, padx=1)

        # 固定根数
        self.qtyRadio = tk.Radiobutton(fixFrame, text="固定根数", bg=rgb_to_hex(245, 245, 245),
                                       value=2, anchor=tk.W, variable=self.sampleVar)  # self.isFixQty
        self.qtyRadio.pack(side=tk.LEFT, padx=5)
        self.qtyEntry = tk.Entry(fixFrame, relief=tk.RIDGE, width=8, textvariable=self.fixQty,
                                 validate="key", validatecommand=(self.testContent, "%P"))
        self.qtyEntry.pack(side=tk.LEFT, fill=tk.X, padx=1)
        self.qtyEntry.bind("<Button-1>", self.qtyEnterEvent)
        tk.Label(fixFrame, text="根", bg=rgb_to_hex(245, 245, 245),
                 anchor=tk.W, width=25).pack(side=tk.LEFT, expand=tk.NO, padx=1)

        # 不执行历史K线
        hisRadio = tk.Radiobutton(hisFrame, text="不执行历史K线", bg=rgb_to_hex(245, 245, 245), anchor=tk.W,
                                  value=3, variable=self.sampleVar)  # self.isHistory
        hisRadio.pack(side=tk.LEFT, padx=5)

        for radio in [allKRadio, self.dateRatio, hisRadio]:
            radio.bind("<Button-1>", self.handlerAdaptor(self.radioBtnEvent, radioBtn=radio))

    def setMargin(self, frame):
        """设置保证金"""
        marginFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        marginFrame.pack(fill=tk.X, padx=15, pady=2)

        marginLabel = tk.Label(marginFrame, text='保证金率:', bg=rgb_to_hex(245, 245, 245),
                               justif=tk.LEFT, anchor=tk.W, width=15)
        marginLabel.pack(side=tk.LEFT)
        marginEntry = tk.Entry(marginFrame, relief=tk.GROOVE, bd=2, width=8, textvariable=self.margin,
                               validate="key", validatecommand=(self.testFlt, "%P"))
        marginEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        tk.Label(marginFrame, text='%', bg=rgb_to_hex(245, 245, 245), justif=tk.LEFT, anchor=tk.W, width=2) \
            .pack(side=tk.LEFT, expand=tk.NO, padx=1)

    def setCommision(self, frame):
        """手续费"""

        openFeeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        openFeeFrame.pack(fill=tk.X, padx=15, pady=2)
        tk.Label(openFeeFrame, text='开仓手续费(率):', bg=rgb_to_hex(245, 245, 245),
                 justify=tk.LEFT, anchor=tk.W, width=15).pack(side=tk.LEFT)
        openFeeEntry = tk.Entry(openFeeFrame, relief=tk.GROOVE, bd=2, width=8, textvariable=self.openFee,
                                validate="key", validatecommand=(self.testFlt, "%P"))
        openFeeEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)

        openFeeUnit = tk.Label(openFeeFrame, text=' ', bg=rgb_to_hex(245, 245, 245),
                               textvariable=self.openTypeUnitVar, justify=tk.LEFT, anchor=tk.W, width=2)
        openFeeUnit.pack(side=tk.LEFT, padx=1)
        # 周期
        openFeeTypeCheck = tk.Checkbutton(openFeeFrame, text="比例", bg=rgb_to_hex(245, 245, 245),
                                          bd=1, anchor=tk.W, variable=self.openType, command=self.openTypeUnitSet)
        openFeeTypeCheck.pack(side=tk.LEFT, padx=5)

        closeFeeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        closeFeeFrame.pack(fill=tk.X, padx=15, pady=2)
        tk.Label(closeFeeFrame, text='平仓手续费(率):', bg=rgb_to_hex(245, 245, 245),
                 justify=tk.LEFT, anchor=tk.W, width=15).pack(side=tk.LEFT)
        closeFeeEntry = tk.Entry(closeFeeFrame, relief=tk.GROOVE, bd=2, width=8, textvariable=self.closeFee,
                                 validate="key", validatecommand=(self.testFlt, "%P"))

        closeFeeEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        closeFeeUnit = tk.Label(closeFeeFrame, text=' ', bg=rgb_to_hex(245, 245, 245),
                                textvariable=self.closeTypeUnitVar, justify=tk.LEFT, anchor=tk.W, width=2)
        closeFeeUnit.pack(side=tk.LEFT, padx=1)

        closeFeeTypeCheck = tk.Checkbutton(closeFeeFrame, text="比例", bg=rgb_to_hex(245, 245, 245),
                                           bd=1, anchor=tk.W, variable=self.closeType, command=self.closeTypeUnitSet)
        closeFeeTypeCheck.pack(side=tk.LEFT, padx=5)

    def openTypeUnitSet(self):
        """开仓手续费类型选择事件"""
        openType = self.openType.get()
        if openType == 0:
            self.openTypeUnitVar.set(" ")
        if openType == 1:
            self.openTypeUnitVar.set("%")

    def closeTypeUnitSet(self):
        closeType = self.closeType.get()
        if closeType == 0:
            self.closeTypeUnitVar.set(" ")
        if closeType == 1:
            self.closeTypeUnitVar.set("%")

    # 弃用
    def setSeperator(self, frame):
        seperatorFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        seperatorFrame.pack(fill=tk.X, padx=15, pady=15)
        cv = tk.Canvas(seperatorFrame, bg=rgb_to_hex(245, 245, 245))
        cv.create_line(0, 0, 360, 0, width=5, fill=rgb_to_hex(25, 25, 25))
        cv.pack(expand=tk.YES, fill=tk.BOTH)

    def addButton(self, frame):
        #TODO: 和加载的addButton代码相同
        enterFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        enterFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=2, pady=5)
        cancelButton = tk.Button(enterFrame, text="取消", relief=tk.FLAT, bg=rgb_to_hex(230, 230, 230),
                                 activebackground="lightblue", highlightbackground="red",
                                 overrelief="groove",
                                 command=self.cancel)
        cancelButton.pack(side=tk.RIGHT, ipadx=20, padx=5, pady=5)

        enterButton = tk.Button(enterFrame, text="确定", relief=tk.FLAT,
                                activebackground="lightblue",
                                overrelief="groove",
                                command=self.enter, bg=rgb_to_hex(230, 230, 230))
        enterButton.pack(side=tk.RIGHT, ipadx=20, padx=5, pady=5)

    def selectContract(self):
        """选择合约"""
        self.selectWin = SelectContractWin(self, self._exchange, self._commodity, self._contract)
        self.selectWin.display()

    def enter(self):
        code = self.contCode.get()
        kLineType = self.kLineType.get()
        kLineSlice = self.kLineSlice.get()
        sampleVar = self.sampleVar.get()

        beginDate = self.beginDate.get()
        fixQty = self.fixQty.get()

        if not code:
            messagebox.showinfo(title="提示", message="商品代码不能为空!", parent=self)
            return

        if sampleVar == 1:
            # 对用户输入的日期进行判断
            dateFormat = self._isDateFormat(beginDate)
            if not dateFormat:  # 没有正确返回日期就退出
                return
        elif sampleVar == 2:
            if not fixQty or int(fixQty) == 0:
                messagebox.showinfo("极星量化", "K线数量大于零且不能为空", parent=self)
                return
        elif sampleVar == 0 or sampleVar == 3:
            pass
        else:
            raise Exception("运算起始点异常")

        sampleDict = {
            0: "所有K线",
            1: beginDate,
            2: int(fixQty),
            3: "不执行历史K线"
        }
        sampleValue = sampleDict[sampleVar]
        if sampleVar == 1:    # 对样本数是日期的进行格式变换
            sampleValue = parse(beginDate).strftime("%Y-%m-%d")

        selectRlt = (code, kLineType, kLineSlice, sampleValue)

        # 当父窗口按钮按下修改按钮时，修改条目值
        if self.selectedItem:
            self._master.contTree.item(self.selectedItem, values=selectRlt)
        else:
            self._master.contTree.insert("", tk.END, values=selectRlt)

        # 不加self._master.display()会出现选择合约确定后设置窗口后移
        # self._master.focus()
        # TODO：点击量化主界面后master窗口会消失
        self.destroy()
        self._master.display()

    def cancel(self):
        """关闭窗口"""
        self.destroy()
        self._master.display()

    def setUserContract(self, contList):
        """设置用户所选数据合约"""
        self.userContList = contList

    def qtyEnterEvent(self, event):
        """点击qtyEntry时qtyRatio选中"""
        self.qtyRadio.select()

    def dateSelectEvent(self, event):
        """点击选择日期时dateRatio选中"""
        self.dateRatio.select()

    def radioBtnEvent(self, event, radioBtn):
        """从qtyEntry获取焦点"""
        radioBtn.focus_set()

    def _isDateFormat(self, date):
        """
        判断用户输入的日期格式是否正确，正确则将该日期返回，错误则给出提示信息
        :param date: 标准格式：'YYYYMMDD'
        :return:
        """
        if len(date) > 8 or len(date) < 8:
            messagebox.showinfo("极星量化", "日期应为8位长度", parent=self)
            return
        else:
            # TODO: 还需要判断日期是否是合法日期
            try:
                time = parse(date)
            except ValueError:
                messagebox.showinfo("极星量化", "日期为非法日期", parent=self)
                return
            else:
                if time > datetime.now():
                    messagebox.showinfo("极星量化", "日期不能大于今天", parent=self)
                    return
                else:
                    return  date


class EntryPopup(tk.Entry):
    """单击参数进行修改Entry类"""

    def __init__(self, parent, text, **kw):
        ''' If relwidth is set, then width is ignored '''
        super().__init__(parent, **kw)

        self.parent = parent

        self.insert(0, text)
        # self['state'] = 'readonly'
        self['readonlybackground'] = 'white'
        self['selectbackground'] = '#1BA1E2'
        self['exportselection'] = False
        self['borderwidth'] = 2
        self['relief'] = tk.GROOVE

        self.focus_force()
        self.selection_range(0, 'end')
        self.bind("<Control-a>", self.selectAll)
        self.bind("<Escape>", lambda *ignore: self.destroy())
        self.bind("<Return>", self.saveEdit)
        self.bind("<FocusOut>", self.onFocusOut)
        self.bind("<FocusIn>", self.onFocusIn)
        # 键盘键位释放
        self.bind("<KeyRelease>", self.onKeyRelease)

    def selectAll(self, *ignore):
        ''' Set selection on the whole text '''
        self.selection_range(0, 'end')
        return 'break'

    def saveEdit(self, event):
        item = self.parent.focus()
        self.parent.set(item, column="#2", value=self.get())
        self.destroy()

    def onFocusIn(self, event):
        # 记录获取焦点的item
        # TODO: 多个时是不是会有问题
        self.item = self.parent.focus()

    def onFocusOut(self, event):
        self.parent.set(self.item, column="#2", value=self.get())
        self.destroy()

    def onKeyRelease(self, event):
        self.parent.set(self.item, column="#2", value=self.get())
