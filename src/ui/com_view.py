import os
import sys
sys.path.append("..")

import re
import json
import pandas as pd

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
from report.windowconfig import center_window


class QuantFrame(object):
    '''通用方法类'''
    def __init__(self):
        pass
        
    def addScroll(self, frame, widgets, xscroll=True, yscroll=True):
        xsb,ysb = None, None

        if xscroll:
            xsb = tk.Scrollbar(frame, orient="horizontal")
            widgets.config(xscrollcommand=xsb.set)
            xsb.config(command=widgets.xview, bg=rgb_to_hex(255,0,0))
            xsb.pack(fill=tk.X, side=tk.BOTTOM)

        if yscroll:
            ysb = tk.Scrollbar(frame,bg=rgb_to_hex(255,0,0))
            widgets.config(yscrollcommand=ysb.set)
            ysb.config(command=widgets.yview, bg=rgb_to_hex(255,0,0))
            ysb.pack(fill=tk.Y, side=tk.RIGHT)

        return xsb, ysb


class QuantToplevel(tk.Toplevel):
    def __init__(self, master=None):
        tk.Toplevel.__init__(self, master)
        self._master = master
        self.language = Language("EquantMainFrame")
        self.setPos()
        #图标
        self.iconbitmap(bitmap=r"./icon/epolestar ix2.ico")

    def setPos(self):
        # 获取主窗口大小和位置，根据主窗口调整输入框位置
        ws = self._master.winfo_width()
        hs = self._master.winfo_height()
        wx = self._master.winfo_x()
        wy = self._master.winfo_y()

        #计算窗口位置
        w, h = 400, 120
        x = (wx + ws/2) - w/2
        y = (wy + hs/2) - h/2

        #弹出输入窗口，输入文件名称
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.minsize(200, 120)

    def display(self):
        """显示并设置模态窗口"""
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.wait_window()


class NewFileToplevel(QuantToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.attributes("-toolwindow", 1)
        self.title("新建文件")
        self.createWidgets()

    def createWidgets(self):
        f1, f2, f3 = tk.Frame(self), tk.Frame(self), tk.Frame(self)
        f1.pack(side=tk.TOP, fill=tk.X, pady=5)
        f2.pack(side=tk.TOP, fill=tk.X)
        f3.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        name_label = tk.Label(f1, text=self.language.get_text(14), width=10)
        self.nameEntry = tk.Entry(f1, width=23)
        type_label = tk.Label(f2, text=self.language.get_text(15), width=10)
        self.type_chosen = ttk.Combobox(f2, state="readonly", width=20)
        self.type_chosen["values"] = [".py"]
        self.type_chosen.current(0)

        self.saveBtn = tk.Button(f3, text=self.language.get_text(19), bd=0)
        self.cancelBtn = tk.Button(f3, text=self.language.get_text(20), bd=0)
        name_label.pack(side=tk.LEFT, expand=tk.NO)
        self.nameEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)
        type_label.pack(side=tk.LEFT, expand=tk.NO)
        self.type_chosen.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)
        self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, padx=20)
        self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO)

    def display(self):
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.nameEntry.focus_set()
        self.wait_window()


class NewDirToplevel(QuantToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.attributes("-toolwindow", 1)
        self.title("新建文件夹")
        self.createWidget()

    def createWidget(self):
        f1, f2, f3 = tk.Frame(self), tk.Frame(self), tk.Frame(self)
        f4, f5 = tk.Frame(f3), tk.Frame(f3)

        f1.pack(side=tk.TOP, fill=tk.X, pady=5)
        f2.pack(side=tk.TOP, fill=tk.X)
        f3.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        f4.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)
        f5.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES)

        nameLabel = tk.Label(f1, text="输入分组名称：")
        self.nameEntry = tk.Entry(f2)
        self.saveBtn = tk.Button(f4, text="保存", bd=0)
        self.cancelBtn = tk.Button(f5, text="取消", bd=0)

        nameLabel.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15)
        self.nameEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)
        self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, padx=10)
        self.cancelBtn.pack(side=tk.LEFT, expand=tk.NO, padx=10)

    def display(self):
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.nameEntry.focus_set()
        self.wait_window()


class RenameToplevel(QuantToplevel):
    def __init__(self, path, master=None):
        super().__init__(master)
        self.path = path
        self.attributes("-toolwindow", 1)
        self.title("重命名")
        self.createWidget()

    def createWidget(self):
        f1, f2 = tk.Frame(self), tk.Frame(self)
        f1.pack(side=tk.TOP, fill=tk.X, pady=15)
        f2.pack(side=tk.BOTTOM, fill=tk.X)

        if os.path.isfile(self.path):
            newLabel = tk.Label(f1, text=self.language.get_text(28))
            self.newEntry = tk.Entry(f1, width=15)
            self.newEntry.insert(tk.END, os.path.basename(self.path))

            self.saveBtn = tk.Button(f2, text="确定", bd=0)
            self.cancelBtn = tk.Button(f2, text="取消", bd=0)

            newLabel.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15)
            self.newEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)

            self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)
            self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)

        if os.path.isdir(self.path):
            newLabel = tk.Label(f1, text=self.language.get_text(30))
            self.newEntry = tk.Entry(f1, width=15)
            self.newEntry.insert(tk.END, os.path.basename(self.path))

            self.saveBtn = tk.Button(f2, text="确定", bd=0)
            self.cancelBtn = tk.Button(f2, text="取消", bd=0)

            newLabel.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15)
            self.newEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=15)

            self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)
            self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)

    def display(self):
        self.update()
        self.deiconify()
        self.grab_set()
        self.focus_set()
        self.newEntry.focus_set()
        self.wait_window()


class DeleteToplevel(QuantToplevel):
    def __init__(self, path, master=None):
        super().__init__(master)
        self.path = path
        self.attributes("-toolwindow", 1)
        # self.wm_attributes("-topmost", 1)
        self.title("删除")
        self.createWidget()

    def createWidget(self):
        f1, f2 = tk.Frame(self), tk.Frame(self)
        f1.pack(side=tk.TOP, fill=tk.X, pady=5)
        f2.pack(side=tk.BOTTOM, fill=tk.X)
        label = tk.Label(f1)
        label["text"] = self.language.get_text(34)
        path = self.path
        if len(self.path) > 1:
            label["text"] = "即将删除被选中项"
        else:
            if os.path.isdir(self.path[0]):
                label["text"] = self.language.get_text(35) + os.path.basename(self.path[0]) + "?"
            if os.path.isfile(self.path[0]):
                label["text"] = self.language.get_text(34) + \
                                os.path.join(os.path.basename(os.path.dirname(self.path[0])),
                                             os.path.basename(self.path[0])) + "?"

        self.saveBtn = tk.Button(f2, text=self.language.get_text(33), bd=0)
        self.cancelBtn = tk.Button(f2, text=self.language.get_text(20), bd=0)

        label.pack(side=tk.LEFT, fill=tk.X, expand=tk.NO, padx=15, pady=15)
        self.cancelBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)
        self.saveBtn.pack(side=tk.RIGHT, expand=tk.NO, ipadx=5, padx=15, pady=10)


def Singleton(cls):
    # 单例模式
    _instance = {}

    def __singleton(*args, **kw):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kw)
        return _instance[cls]

    return __singleton


# @Singleton
class HistoryToplevel(QuantToplevel):
    def __init__(self, view, master=None):
        super().__init__(master)
        self.withdraw()
        self.wm_attributes("-topmost", 0)  # 窗口置顶
        self._view = view
        self._master = master
        self.set_config()

    def set_config(self):
        self.title('回测报告')
        center_window(self, 1000, 600)
        self.minsize(1000, 600)

    def display_(self):
        self.update()
        self.deiconify()


class RunWin(QuantToplevel, QuantFrame):
    """运行按钮点击弹出窗口"""
    # 背景色
    bgColor = rgb_to_hex(245, 245, 245)
    bgColorW = "white"

    def __init__(self, control, master=None):
        super().__init__(master)
        self._control = control
        self._exchange = self._control.model.getExchange()
        self._commodity = self._control.model.getCommodity()
        self._contract = self._control.model.getContract()
        self._userNo = self._control.model.getUserNo()

        self.title("策略属性设置")
        self.attributes("-toolwindow", 1)
        self._master = master
        self.topFrame = tk.Frame(self, relief=tk.RAISED, bg=rgb_to_hex(245, 245, 245))
        self.topFrame.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=10)
        self.setPos()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        # 将函数包装一下(初始资金只能输入数字)
        self.testContent = self.register(self.testDigit)
        # 新建属性设置变量
        self.initVariable()
        # 初始化config
        self.config = {
            'Contract': ( ),

            'Trigger': {
                'Timer': None,
                'Cycle': None,
                'KLine': True,
                'SnapShot': None,
                'Trade': True,
            },

            'Sample': {
                    'KLineType': 'D',
                    'KLineSlice': 1
            },

        'RunMode': {
            'SendOrder': '1',
            'Simulate': {
                'Continues': True,
                'UseSample': True
            },
            'Actual': {
                'SendOrder2Actual': False
            }
        },

        'Money': {
            'UserNo': 'ET001',
            'InitFunds': '10000000',
            "MinQty": 1,
             'OrderQty': {
                'Type': '1',
                'Count': 1,
        },
             'Hedge': "T",
             'Margin': {'Type': 'F', 'Value': 0.08},
             'OpenFee': {'Type': 'F', 'Value': 1},
             'CloseFee': {'Type': 'F', 'Value': 1},
             'CloseTodayFee': {'Type': 'F', 'Value': 0},
        },

        'Limit': {
            'OpenTimes': -1,
            'ContinueOpenTimes': -1,
            'OpenAllowClose': True,
            'CloseAllowOpen': True,

        },

        'Other': {
            'Slippage': 0,
            'TradeDirection': 0
          }
        }

        self.fColor = self.bgColor
        self.sColor = self.bgColor
        self.rColor = self.bgColorW

        self.createNotebook(self.topFrame)

        self.fundFrame = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))
        self.sampleFrame = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))
        self.runFrame = tk.Frame(self.topFrame, bg=rgb_to_hex(255, 255, 255))

        self.runFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

        self.createRun(self.runFrame)
        self.createFund(self.fundFrame)
        self.createSample(self.sampleFrame)
        self.addButton(self.topFrame)

        # TODO： 如果将配置文件内容删除会报错
        self.setDefaultConfigure()
        # 根据用户设置内容初始化控件
        self.initWidget()

    def initVariable(self):
        # 变量
        self.contract = tk.StringVar()  # 基准合约
        self.user = tk.StringVar()  # 用户
        self.initFund = tk.StringVar()  # 初始资金
        self.defaultType = tk.StringVar()  # 默认下单方式
        self.defaultQty = tk.StringVar()  # 默认下单量（或资金、或比例）
        self.minQty = tk.StringVar()  # 最小下单量
        self.hedge = tk.StringVar()  # 投保标志
        self.margin = tk.StringVar()  # 保证金

        self.openType = tk.StringVar()  # 开仓收费方式
        self.closeType = tk.StringVar()  # 平仓收费方式
        self.openFee = tk.StringVar()  # 开仓手续费（率）
        self.closeFee = tk.StringVar()  # 平仓手续费（率）
        self.dir = tk.StringVar()  # 交易方向
        self.slippage = tk.StringVar()  # 滑点损耗
        # self.contract = tk.StringVar()  # 合约
        # self.timer = tk.StringVar()       # 定时触发
        self.isCycle = tk.IntVar()  # 是否按周期触发
        self.cycle = tk.StringVar()  # 周期
        # TODO：定时触发(text控件不能设置变量)
        self.isKLine = tk.IntVar()  # K线触发
        self.isMarket = tk.IntVar()  # 行情触发
        self.isTrade = tk.IntVar()  # 交易数据触发

        # 样本类型： 0. 所有K线  1. 起始日期  2. 固定根数  3. 不执行历史K线
        self.sampleVar = tk.IntVar()
        self.beginDate = tk.StringVar()  # 起始日期
        self.fixQty = tk.StringVar()  # 固定根数

        self.kLineType = tk.StringVar()  # K线类型
        self.kLineSlice = tk.StringVar()  # K线周期
        self.sendOrderMode = tk.IntVar()  # 发单时机： 0. 实时发单 1. K线稳定后发单
        self.isActual = tk.IntVar()  # 实时发单
        # self.isContinue = tk.IntVar()       # K线稳定后发单

        self.isOpenTimes = tk.IntVar()  # 每根K线同向开仓次数标志
        self.openTimes = tk.StringVar()  # 每根K线同向开仓次数
        self.isConOpenTimes = tk.IntVar()  # 最大连续同向开仓次数标志
        self.conOpenTimes = tk.StringVar()  # 最大连续同向开仓次数
        self.canClose = tk.IntVar()  # 开仓的当前K线不允许平仓
        self.canOpen = tk.IntVar()  # 平仓的当前K线不允许开仓

        # 根据选择内容设置标签内容变量
        self.unitVar = tk.StringVar()
        self.openTypeUnitVar = tk.StringVar()
        self.closeTypeUnitVar = tk.StringVar()

    def getTextConfigure(self):
        """从配置文件中得到配置信息"""
        try:
            configure = self.readConfig()
        except EOFError:
            configure = None

        key = self._control.getEditorText()["path"]
        if configure:
            if key in configure:
                return configure[key]
        return None

    def setDefaultConfigure(self):
        conf = self.getTextConfigure()
        if conf:
            # self.user.set(conf[VUser]),
            self.initFund.set(conf[VInitFund]),
            self.defaultType.set(conf[VDefaultType]),
            self.defaultQty.set(conf[VDefaultQty]),
            self.minQty.set(conf[VMinQty]),
            self.hedge.set(conf[VHedge]),
            self.margin.set(conf[VMinQty]),

            self.openType.set(conf[VOpenType]),
            self.closeType.set(conf[VCloseType]),
            self.openFee.set(conf[VOpenFee]),
            self.closeFee.set(conf[VCloseFee]),
            self.dir.set(conf[VDirection]),
            self.slippage.set(conf[VSlippage]),

            self.contract.set(conf[VContract])
            # self.setText(self.contractInfo, conf[VContract])

            self.isCycle.set(conf[VIsCycle]),
            self.cycle.set(conf[VCycle]),

            # 定时触发通过函数设置
            self.timerText.delete(0.0, tk.END)
            self.setText(self.timerText, conf[VTimer])

            self.isKLine.set(conf[VIsKLine]),
            self.isMarket.set(conf[VIsMarket]),
            self.isTrade.set(conf[VIsTrade]),

            self.sampleVar.set(conf[VSampleVar]),
            self.beginDate.set(conf[VBeginDate]),
            self.fixQty.set(conf[VFixQty]),

            self.kLineType.set(conf[VKLineType]),
            self.kLineSlice.set(conf[VKLineSlice]),
            self.sendOrderMode.set(conf[VSendOrderMode]),
            self.isActual.set(conf[VIsActual]),

            self.isOpenTimes.set(conf[VIsOpenTimes]),
            self.openTimes.set(conf[VOpenTimes]),
            self.isConOpenTimes.set(conf[VOpenTimes]),
            self.conOpenTimes.set(conf[VOpenTimes]),
            self.canClose.set(conf[VCanClose]),
            self.canOpen.set(conf[VCanOpen]),

        else:
            # 设置默认值
            self.isCycle.set(0),
            self.cycle.set(200),
            self.isKLine.set(1),
            self.isMarket.set(1),
            self.isTrade.set(0),
            # 指定时刻不好存

            # 发单时机
            self.sendOrderMode.set(0)
            # 运行模式
            self.isActual.set(0)

            # 数据合约

            # 账户

            # K线类型
            self.kLineType.set("日")
            # K线周期
            self.kLineSlice.set("1")

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
            self.hedge.set("投机")
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
            self.slippage.set("1")

            # 样本设置
            self.sampleVar.set(2)
            self.fixQty.set(2000)

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

    def getConfig(self):
        """获取用户配置的config"""
        return self.config

    def getUserContract(self):
        """获取用户所选的数据合约信息"""
        return self.contract.get()

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

        self.fundBtn = tk.Button(nbFrame, text="资金设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.fColor,
                                 bd=0, highlightthickness=1, command=self.toFundFrame)
        self.runBtn = tk.Button(nbFrame, text="运行设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.rColor,
                                bd=0, highlightthickness=1, command=self.toRunFrame)
        self.sampleBtn = tk.Button(nbFrame, text="样本设置", relief=tk.FLAT, padx=14, pady=1.5, bg=self.sColor,
                                   bd=0, highlightthickness=1, command=self.toSampFrame)

        self.runBtn.pack(side=tk.LEFT, expand=tk.NO)
        self.fundBtn.pack(side=tk.LEFT, expand=tk.NO)
        self.sampleBtn.pack(side=tk.LEFT, expand=tk.NO)

        for btn in (self.fundBtn, self.sampleBtn, self.runBtn):
            btn.bind("<Enter>", self.handlerAdaptor(self.onEnter, button=btn))
            btn.bind("<Leave>", self.handlerAdaptor(self.onLeave, button=btn))

    def toFundFrame(self):
        self.fundBtn.config(bg="white")
        self.fColor = self.fundBtn['bg']
        self.rColor = self.bgColor
        self.sColor = self.bgColor
        self.runBtn.config(bg=self.rColor)
        self.sampleBtn.config(bg=self.sColor)

        self.runFrame.pack_forget()
        self.sampleFrame.pack_forget()
        self.fundFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def toSampFrame(self):
        self.sampleBtn.config(bg="white")
        self.sColor = self.sampleBtn['bg']
        self.rColor = self.bgColor
        self.fColor = self.bgColor
        self.fundBtn.config(bg=self.fColor)
        self.runBtn.config(bg=self.rColor)

        self.fundFrame.pack_forget()
        self.runFrame.pack_forget()
        self.sampleFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def toRunFrame(self):
        self.runBtn.config(bg="white")
        self.rColor = self.runBtn['bg']
        self.fColor = self.bgColor
        self.sColor = self.bgColor
        self.fundBtn.config(bg=self.fColor)
        self.sampleBtn.config(bg=self.sColor)

        self.fundFrame.pack_forget()
        self.sampleFrame.pack_forget()
        self.runFrame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.YES)

    def onEnter(self, event, button):
        if button == self.fundBtn:
            button.config(bg='white')
            self.sampleBtn.config(bg=self.bgColor)
            self.runBtn.config(bg=self.bgColor)
        elif button == self.sampleBtn:
            button.config(bg='white')
            self.fundBtn.config(bg=self.bgColor)
            self.runBtn.config(bg=self.bgColor)
        else:
            button.config(bg='white')
            self.fundBtn.config(bg=self.bgColor)
            self.sampleBtn.config(bg=self.bgColor)

    def onLeave(self, event, button):
        button.config(bg=rgb_to_hex(227, 230, 233))
        if button == self.fundBtn:
            button['bg'] = self.fColor
            self.runBtn['bg'] = self.rColor
            self.sampleBtn['bg'] = self.sColor
        elif button == self.runBtn:
            button['bg'] = self.rColor
            self.fundBtn['bg'] = self.fColor
            self.sampleBtn['bg'] = self.sColor
        elif button == self.sampleBtn:
            button['bg'] = self.sColor
            self.fundBtn['bg'] = self.fColor
            self.runBtn['bg'] = self.rColor
        else:
            pass

    def createFund(self, frame):
        self.setInitFunds(frame)
        self.setTradeDir(frame)
        self.setDefaultOrder(frame)
        self.setOrderSym(frame)
        self.setMargin(frame)
        self.setCommision(frame)
        self.setSlippage(frame)

    def createSample(self, frame):
        self.setSample(frame)
        self.setSendOrderLimit(frame)

    def createRun(self, frame):
        self.setTrigger(frame)
        baseFrame = tk.LabelFrame(frame, text="基础设置", bg=rgb_to_hex(255, 255, 255), padx=5)
        baseFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, padx=15, pady=5)

        self.SendOrderMode(baseFrame)
        self.setRunMode(baseFrame)
        self.setContract(baseFrame)
        self.setUser(baseFrame)
        self.setKLineType(baseFrame)
        self.setKLineSlice(baseFrame)

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
        for user in self._userNo:
            userList.append(user["UserNo"])
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

    def testDigit(self, content):
        """判断Entry中内容"""
        if content.isdigit() or content == "":
            return True
        return False

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
        minQtyEntry = tk.Entry(minQtyFrame, relief=tk.GROOVE, bd=2, width=10, textvariable=self.minQty,
                               validate="key", validatecommand=(self.testContent, "%P"))
        # minQtyEntry.insert(tk.END, 1)
        minQtyEntry.pack(side=tk.LEFT, expand=tk.NO, padx=4)
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

    def setOrderSym(self, frame):
        """投保标志"""
        symFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        symFrame.pack(fill=tk.X, padx=15, pady=5)
        symLabel = tk.Label(symFrame, text="投保标志:", bg=rgb_to_hex(255, 255, 255),
                            justif=tk.LEFT, anchor=tk.W, width=15)
        symLabel.pack(side=tk.LEFT)

        symChosen = ttk.Combobox(symFrame, state="readonly", textvariable=self.hedge)
        symList = ['投机', '套利', '保值', '做市']  # TODO: userList需要从后台获取
        symChosen["values"] = symList
        # symChosen.current(0)
        symChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)

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
                                validate="key", validatecommand=(self.testContent, "%P"))
        # openFeeEntry.insert(tk.END, 1)
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
        # closeTypeChosen.current(0)
        closeTypeChosen.pack(side=tk.LEFT, fill=tk.X, padx=5)
        closeTypeChosen.bind('<<ComboboxSelected>>', self.closeTypeUnitSet)

        closeFeeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        closeFeeFrame.pack(fill=tk.X, padx=15, pady=5)
        tk.Label(closeFeeFrame, text='平仓手续费(率):', bg=rgb_to_hex(255, 255, 255),
                 justify=tk.LEFT, anchor=tk.W, width=15).pack(side=tk.LEFT)
        closeFeeEntry = tk.Entry(closeFeeFrame, relief=tk.GROOVE, bd=2, textvariable=self.closeFee,
                                 validate="key", validatecommand=(self.testContent, "%P"))
        # closeFeeEntry.insert(tk.END, 1)
        closeFeeEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)
        closeFeeUnit = tk.Label(closeFeeFrame, text=' ', bg=rgb_to_hex(255, 255, 255),
                                     textvariable=self.closeTypeUnitVar, justify=tk.LEFT, anchor=tk.W, width=2)
        closeFeeUnit.pack(side=tk.LEFT, padx=5)

    def openTypeUnitSet(self, event=None):
        """开仓手续费类型选择事件"""
        openType = self.openType.get()
        if openType == "固定值":
            self.openTypeUnitVar.set(" ")
            # self.openFeeUnit.config(text=" ")
        if openType == "比例":
            # self.openFeeUnit.config(text="%")
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
        # dirChosen.current(0)
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
        # slipEntry.insert(tk.END, 1)
        slipEntry.pack(side=tk.LEFT, fill=tk.X, padx=5)

    def setContract(self, frame):
        contractFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        contractFrame.pack(fill=tk.NONE, anchor=tk.W, padx=5, pady=5)

        contractLabel = tk.Label(contractFrame, text="基准合约:", bg=rgb_to_hex(255, 255, 255),
                                 justify=tk.LEFT, anchor=tk.NW, width=10)
        contractLabel.pack(side=tk.LEFT, padx=5)

        self.contractEntry = tk.Entry(contractFrame, bg=rgb_to_hex(255, 255, 255), bd=2, width=35, relief=tk.GROOVE,
                                      state="disabled", textvariable=self.contract)
        self.contractEntry.pack(side=tk.LEFT, fill=tk.X, expand=tk.YES, padx=10)

        contractButton = tk.Button(contractFrame, text="选择", relief=tk.FLAT,
                                   activebackground="lightblue",
                                   overrelief="groove",
                                   bg=rgb_to_hex(230, 230, 230),
                                   command=self.selectContract)
        contractButton.pack(side=tk.LEFT, ipadx=5, padx=5)

    def selectContract(self):
        """选择合约"""
        self.selectWin = SelectContractWin(self._exchange, self._commodity, self._contract, self)
        self.selectWin.display()

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

        # 即时行情触发
        self.marketCheck = tk.Checkbutton(marketFrame, text="即时行情触发", bg=rgb_to_hex(255, 255, 255),
                                          anchor=tk.W, variable=self.isMarket)
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

    def setSample(self, frame):
        """设置样本"""
        sampFrame = tk.LabelFrame(frame, text="运算起始点", bg=rgb_to_hex(255, 255, 255), padx=5, width=380)
        sampFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, padx=15, pady=5)
        allKFrame = tk.Frame(sampFrame, bg=rgb_to_hex(255, 255, 255), padx=5)
        allKFrame.pack(side=tk.TOP, fill=tk.X, pady=5)
        beginFrame = tk.Frame(sampFrame, bg=rgb_to_hex(255, 255, 255), padx=5)
        beginFrame.pack(side=tk.TOP, fill=tk.X, pady=5)
        fixFrame = tk.Frame(sampFrame, bg=rgb_to_hex(255, 255, 255), padx=5)
        fixFrame.pack(side=tk.TOP, fill=tk.X, pady=5)
        hisFrame = tk.Frame(sampFrame, bg=rgb_to_hex(255, 255, 255), padx=5)
        hisFrame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # self.sampleVar.set(2)
        # 所有K线
        allKRadio = tk.Radiobutton(allKFrame, text="所有K线", bg=rgb_to_hex(255, 255, 255),
                                   value=0, anchor=tk.W, variable=self.sampleVar)  # self.isAllK
        allKRadio.pack(side=tk.LEFT, padx=5)

        # 起始日期
        self.dateRatio = tk.Radiobutton(beginFrame, text="起始日期", bg=rgb_to_hex(255, 255, 255),
                                        value=1, anchor=tk.W, variable=self.sampleVar)  # self.isBeginDate
        self.dateRatio.pack(side=tk.LEFT, padx=5)

        # year = time.localtime().tm_year  # 当前年份
        # date_ = DateEntry(beginFrame, width=15, anchor=tk.W, background='darkblue', foreground="white", borderwidth=2,
        #                   year=year, textvariable=self.beginDate)
        # date_.pack(side=tk.LEFT, pady=5)
        # date_.bind("<ButtonRelease-1>", self.dateSelectEvent)
        date_ = tk.Entry(beginFrame, relief=tk.GROOVE, bd=2, width=10,
                         textvariable=self.beginDate, validate="key", validatecommand=(self.testContent, "%P"))
        date_.pack(side=tk.LEFT, fill=tk.X, padx=1)
        date_.bind("<ButtonRelease-1>", self.dateSelectEvent)
        tk.Label(beginFrame, text="(格式: YYYYMMDD)", bg=rgb_to_hex(255, 255, 255),
                 anchor=tk.W, width=18).pack(side=tk.LEFT, expand=tk.NO, padx=1)

        # 固定根数
        self.qtyRadio = tk.Radiobutton(fixFrame, text="固定根数", bg=rgb_to_hex(255, 255, 255),
                                       value=2, anchor=tk.W, variable=self.sampleVar)  # self.isFixQty
        self.qtyRadio.pack(side=tk.LEFT, padx=5)
        self.qtyEntry = tk.Entry(fixFrame, relief=tk.RIDGE, width=8, textvariable=self.fixQty,
                                 validate="key", validatecommand=(self.testContent, "%P"))
        self.qtyEntry.pack(side=tk.LEFT, fill=tk.X, padx=1)
        self.qtyEntry.bind("<Button-1>", self.qtyEnterEvent)
        tk.Label(fixFrame, text="根", bg=rgb_to_hex(255, 255, 255),
                 anchor=tk.W, width=25).pack(side=tk.LEFT, expand=tk.NO, padx=1)

        # 不执行历史K线
        hisRadio = tk.Radiobutton(hisFrame, text="不执行历史K线", bg=rgb_to_hex(255, 255, 255), anchor=tk.W,
                                  value=3, variable=self.sampleVar)  # self.isHistory
        hisRadio.pack(side=tk.LEFT, padx=5)

        for radio in [allKRadio, self.dateRatio, hisRadio]:
            radio.bind("<Button-1>", self.handlerAdaptor(self.radioBtnEvent, radioBtn=radio))

    def qtyEnterEvent(self, event):
        """点击qtyEntry时qtyRatio选中"""
        self.qtyRadio.select()

    def dateSelectEvent(self, event):
        """点击选择日期时dateRatio选中"""
        self.dateRatio.select()

    def radioBtnEvent(self, event, radioBtn):
        """从qtyEntry获取焦点"""
        radioBtn.focus_set()

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

    def setSendOrderLimit(self, frame):
        sendModeFrame = tk.LabelFrame(frame, text="发单设置", bg=rgb_to_hex(255, 255, 255), padx=5)
        sendModeFrame.pack(side=tk.TOP, fill=tk.X, anchor=tk.W, padx=15, pady=15)

        self.setContinueOpenTimes(sendModeFrame)
        self.setOpenTimes(sendModeFrame)
        self.setCanClose(sendModeFrame)
        self.setCanOpen(sendModeFrame)
        # self.setHelp(setFrame)
        # self.bindEvent()

    def setKLineType(self, frame):
        kLineTypeFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        kLineTypeFrame.pack(fill=tk.NONE, anchor=tk.W, padx=5, pady=5)
        kLineTypeLabel = tk.Label(kLineTypeFrame, text='K线类型:', bg=rgb_to_hex(255, 255, 255),
                                  justify=tk.LEFT, anchor=tk.W, width=10)
        kLineTypeLabel.pack(side=tk.LEFT, padx=5)

        self.kLineTypeChosen = ttk.Combobox(kLineTypeFrame, state="readonly", textvariable=self.kLineType)
        self.kLineTypeChosen['values'] = ['日', '分钟', '秒']
        # self.kLineTypeChosen.current(0)
        self.kLineTypeChosen.pack(side=tk.LEFT, fill=tk.X, padx=10)

    def setKLineSlice(self, frame):
        self.klineSliceFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.klineSliceFrame.pack(fill=tk.X, padx=5, pady=5)
        klineSliceLabel = tk.Label(self.klineSliceFrame, text="K线周期:", bg=rgb_to_hex(255, 255, 255),
                                   justify=tk.LEFT, anchor=tk.W, width=10)
        klineSliceLabel.pack(side=tk.LEFT, padx=5)

        self.klineSliceChosen = ttk.Combobox(self.klineSliceFrame, state="readonly", textvariable=self.kLineSlice)
        self.klineSliceChosen["values"] = ['1', '2', '3', '5', '10', '15', '30']
        # self.klineSliceChosen.current(0)
        self.klineSliceChosen.pack(side=tk.LEFT, fill=tk.X, padx=10)

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
        self.timesLabel = tk.Label(self.openTimesFrame, text='次(1-100)', bg=rgb_to_hex(255, 255, 255),
                 justif=tk.LEFT, anchor=tk.W, width=10)
        self.timesLabel.pack(side=tk.LEFT, expand=tk.NO, padx=1)

    def setContinueOpenTimes(self, frame):
        """最大连续同向开仓次数"""

        self.conTimesFrame = tk.Frame(frame, relief=tk.RAISED, bg=rgb_to_hex(255, 255, 255))
        self.conTimesFrame.pack(fill=tk.X, pady=6)

        self.conCheck = tk.Checkbutton(self.conTimesFrame, text="最大连续同向开仓次数:", bg=rgb_to_hex(255, 255, 255),
                                       anchor=tk.W, variable=self.isConOpenTimes)
        self.conCheck.pack(side=tk.LEFT, padx=10)

        self.conTimesEntry = tk.Entry(self.conTimesFrame, relief=tk.GROOVE, bd=2, width=8, textvariable=self.conOpenTimes,
                                      validate="key", validatecommand=(self.testContent, "%P"))
        # self.conTimesEntry.insert(tk.END, 1)
        self.conTimesEntry.pack(side=tk.LEFT, fill=tk.X, padx=1)
        self.conTimesLabel = tk.Label(self.conTimesFrame, text='次(1-100)', bg=rgb_to_hex(255, 255, 255),
                 justif=tk.LEFT, anchor=tk.W, width=10)
        self.conTimesLabel.pack(side=tk.LEFT, expand=tk.NO, padx=1)

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

    def enter(self):
        # TODO: IntVar()显示时会补充一个0？？？
        user = self.user.get()
        initFund = self.initFund.get()
        defaultType = self.defaultType.get()
        defaultQty = self.defaultQty.get()
        minQty = self.minQty.get()
        hedge = self.hedge.get()
        margin = self.margin.get()

        openType = self.openType.get()
        closeType = self.closeType.get()
        openFee = self.openFee.get()
        closeFee = self.closeFee.get()

        tradeDirection = self.dir.get()
        slippage = self.slippage.get()
        #TODO: contract
        contractInfo = self.contract.get()
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
        isMarket = self.isMarket.get()
        isTrade = self.isTrade.get()

        beginDate = self.beginDate.get()
        # beginDateFormatter = parseYMD(beginDate)
        fixQty = self.fixQty.get()
        sampleVar = self.sampleVar.get()

        kLineType = self.kLineType.get()
        kLineSlice = self.kLineSlice.get()
        sendOrderMode = self.sendOrderMode.get()  # 发单时机： 0. 实时发单 1. K线稳定后发单

        isActual = self.isActual.get()
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
                tempT = parseTime(t)
                timerFormatter.append(tempT)

        if cycle =="":
            messagebox.showinfo("极星量化", "定时触发周期不能为空", parent=self)
            return
        elif int(cycle) % 100 != 0:
            messagebox.showinfo("极星量化", "定时触发周期为100的整数倍", parent=self)
        else:
            pass

        if minQty == "":
            messagebox.showinfo("极星量化", "最小下单量不能为空", parent=self)
            return
        elif int(minQty) > MAXSINGLETRADESIZE:
            messagebox.showinfo("极星量化", "最小下单量不能大于1000", parent=self)
            return
        else:
            pass

        if isOpenTimes and (int(openTimes) < 1 or int(openTimes) > 100):
            messagebox.showinfo("极星量化", "每根K线同向开仓次数必须介于1-100之间", parent=self)
            return
        if isConOpenTimes and (int(conOpenTimes) < 1 or int(conOpenTimes) > 100):
            messagebox.showinfo("极星量化", "最大连续同向开仓次数必须介于1-100之间", parent=self)
            return

        self.config["Contract"] = (contractInfo,)
        # self.config["Contract"] = tuple(contractInfo)
        self.config["Trigger"]["Cycle"] = int(cycle) if isCycle else None
        self.config["Trigger"]["Timer"] = timerFormatter if timer else None
        self.config["Trigger"]["KLine"] = True if isKLine else False
        self.config["Trigger"]["SnapShot"] = True if isMarket else False
        self.config["Trigger"]["Trade"] = True if isTrade else False

        #样本设置
        if kLineType == "日":
            self.config["Sample"]["KLineType"] = "D"
        elif kLineType == "分钟":
            self.config["Sample"]["KLineType"] = "M"
        elif kLineType == "秒":
            self.config["Sample"]["KLineType"] = "S"
        else:
            raise Exception("K线类型未知异常")

        self.config["Sample"]["KLineSlice"] = int(kLineSlice)

        if sampleVar == 0:
            self.config["Sample"]["AllK"] = True
            self.config["RunMode"]["Simulate"]["UseSample"] = True
        elif sampleVar == 1:
            # 对用户输入的日期进行判断
            dateFormat = self._isDateFormat(beginDate)
            if not dateFormat:  # 没有正确返回日期就推出
                return

            self.config["Sample"]["BeginTime"] = beginDate
            self.config["RunMode"]["Simulate"]["UseSample"] = True
        elif sampleVar == 2:
            if not fixQty or int(fixQty) == 0:
                messagebox.showinfo("极星量化", "K线数量大于零且不能为空", parent=self)
                return
            # elif int(fixQty) == 0:
            #     messagebox.showinfo("极星量化", "K线数量大于零且不能为空")
            #     return
            else:
                self.config["Sample"]["KLineCount"] = int(fixQty)
                self.config["RunMode"]["Simulate"]["UseSample"] = True
        elif sampleVar == 3:
            self.config["RunMode"]["Simulate"]["UseSample"] = False
        else:
            raise Exception("运算起始点异常")


        #运行模式
        self.config["RunMode"]["Simulate"]["Continues"] = True
        self.config["RunMode"]["SendOrder"] = '1' if sendOrderMode == 0 else '2'

        # 是否实盘运行
        self.config["RunMode"]["Actual"]["SendOrder2Actual"] = False if isActual == 0 else True

        self.config["Money"]["UserNo"] = user
        self.config["Money"]["InitFunds"] = float(initFund)
        self.config["Money"]["MinQty"] = int(minQty)   # 最小下单量
        if defaultType == "按固定合约数":
            self.config["Money"]["OrderQty"]["Type"] = "1"
            self.config["Money"]["OrderQty"]["Count"] = int(defaultQty)
        elif defaultType == "按固定资金":
            self.config["Money"]["OrderQty"]["Type"] = "2"
            self.config["Money"]["OrderQty"]["Count"] = float(defaultQty)
        elif defaultType == "按资金比例":
            self.config["Money"]["OrderQty"]["Type"] = "3"
            self.config["Money"]["OrderQty"]["Count"] = float(defaultQty) / 100
        else:
            raise Exception("默认下单量类型异常")
        if hedge == "投机":
            self.config["Money"]["Hedge"] = "T"
        elif hedge == "套利":
            self.config["Money"]["Hedge"] = "B"
        elif hedge == "保值":
            self.config["Money"]["Hedge"] = "S"
        elif hedge == "做市":
            self.config["Money"]["Hedge"] = "M"
        else:
            raise Exception("投保标志异常")
        #TODO: margin类型没有设置！！！！！
        self.config["Money"]["Margin"]["Type"] = "R"
        self.config["Money"]["Margin"]["Value"] = float(margin) / 100

        if openType == "比例":
            self.config["Money"]["OpenFee"]["Type"] = 'R'
            self.config["Money"]["OpenFee"]["Value"] = float(openFee)/100
        else:
            self.config["Money"]["OpenFee"]["Type"] = 'F'
            self.config["Money"]["OpenFee"]["Value"] = float(openFee)
        if closeType == "比例":
            self.config["Money"]["CloseFee"]["Type"] = 'R'
            self.config["Money"]["CloseFee"]["Value"] = float(closeFee)/100
        else:
            self.config["Money"]["CloseFee"]["Type"] = 'F'
            self.config["Money"]["CloseFee"]["Value"] = float(closeFee)
        # TODO：平今手续费没有设置
        self.config["Money"]["CloseTodayFee"]["Type"] = "F"
        self.config["Money"]["CloseTodayFee"]["Type"] = 0

        # 下单限制
        self.config["Limit"]["OpenTimes"] = int(openTimes) if isOpenTimes else -1
        self.config["Limit"]["ContinueOpenTimes"] = int(conOpenTimes) if isConOpenTimes else -1
        self.config["Limit"]["OpenAllowClose"] = canClose
        self.config["Limit"]["CloseAllowOpen"] = canOpen

        # other
        self.config["Other"]["Slippage"] = float(slippage)
        if tradeDirection == "双向交易":
            self.config["Other"]["TradeDirection"] = 0
        elif tradeDirection == "仅多头":
            self.config["Other"]["TradeDirection"] = 1
        else:
            self.config["Other"]["TradeDirection"] = 2

        # -------------保存用户配置--------------------------
        strategyPath = self._control.getEditorText()["path"]
        userConfig = {
            strategyPath: {
                VUser: user,
                VInitFund: initFund,
                VDefaultType: defaultType,
                VDefaultQty: defaultQty,
                VMinQty: minQty,
                VHedge: hedge,
                VMargin: margin,
                VOpenType: openType,
                VCloseType: closeType,
                VOpenFee: openFee,
                VCloseFee: closeFee,
                VDirection: tradeDirection,
                VSlippage: slippage,
                VContract: contractInfo,
                VTimer: timer,
                VIsCycle: isCycle,
                VCycle: cycle,
                VIsKLine: isKLine,
                VIsMarket: isMarket,
                VIsTrade: isTrade,

                VSampleVar: sampleVar,
                VBeginDate: beginDate,
                VFixQty: fixQty,

                VKLineType: kLineType,
                VKLineSlice: kLineSlice,
                VSendOrderMode: sendOrderMode,
                VIsActual: isActual,
                VIsOpenTimes: isOpenTimes,
                VOpenTimes: openTimes,
                VIsConOpenTimes: isConOpenTimes,
                VConOpenTimes: conOpenTimes,
                VCanClose: canClose,
                VCanOpen: canOpen,
            }
        }

        # print("config: ", self.config)
        # 将配置信息保存到本地文件
        self.writeConfig(userConfig)

        self.destroy()

    def cancel(self):
        self.config = {}
        self.destroy()

    def handlerAdaptor(self, fun, **kwargs):
        return lambda event, fun=fun, kwargs=kwargs: fun(event, **kwargs)

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

    commodityType = {"P": '现货', 'F': '期货', 'O': '期权', 'S': '跨期', 'M': '跨品种', 'Z': '指数'}
    exchangeList = ["CFFEX", "CME", "DCE", "SGE", "SHFE", "ZCE", "INE", "NYMEX", "SSE", "SZSE"]

    def __init__(self, exchange, commodity, contract, master):
        super().__init__(master)
        self._master = master
        self._selectCon = []   # 所选合约列表

        self._exchange = exchange
        self._commodity = commodity
        self._contract = pd.DataFrame(contract)

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
        for exch in self._exchange:
            if exch["ExchangeNo"] in self.exchangeList:   #TODO: 暂时先取六个交易所
                exchangeId = self.exchangeTree.insert("", tk.END,
                                                      text=exch["ExchangeNo"] + "【" + exch["ExchangeName"] + "】",
                                                      values=exch["ExchangeNo"])
                for commodity in self._commodity:
                    if commodity["ExchangeNo"] == exch["ExchangeNo"]:
                        commId = self.exchangeTree.insert(exchangeId, tk.END,
                                                          text=commodity["CommodityName"],
                                                          values=commodity["CommodityNo"])

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
        # 选择合约界面增加原始信息
        contractText = self._master.getUserContract()
        con = contractText.strip("\n")
        if len(con) != 0:
            contractInfo = con.split("\n")
            for contract in contractInfo:
                self._selectCon.append(contract)
                self.contractText.setText(contract)
        # self.addScroll(frame, self.contractText, xscroll=False)
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
        self._master.contractEntry.config(state="normal")
        self._master.contractEntry.delete('0', tk.END)
        for con in self._selectCon:
            self._master.contractEntry.insert(tk.END, con)
        self._master.contractEntry.config(state="disabled")

        # 不加focus会出现选择合约确定后设置窗口后移
        self._master.focus()
        self.destroy()

    def cancel(self):
        self.destroy()

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
                contract = self._contract.loc[
                    (self._contract.ExchangeNo == exchangeNo[0]) & (self._contract.CommodityNo == commodityNo[0])]
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
