import threading
import time

from tkinter import Tk
from tkinter import messagebox
from .model import QuantModel, SendRequest
from .view import QuantApplication
from .language import *
from capi.com_types import *



class TkinterController(object):
    '''程序化入口类'''

    def __init__(self, logger, ui2eg_q, eg2ui_q):

        #日志对象
        self.logger = logger
        #初始化多语言
        load_language("config")
        self._ui2egQueue = ui2eg_q
        self._eg2uiQueue = eg2ui_q

        # UI2EG发送请求对象
        self._request = SendRequest(self._ui2egQueue)

        # 创建主窗口
        self.top = Tk()
        self.app = QuantApplication(self.top, self)
        self.app.create_window()

        # 创建模块
        self.model = QuantModel(self.app, self._ui2egQueue, self._eg2uiQueue, self.logger)
        self.logger.info("Create quant model!")

        # 策略管理器
        self.strategyManager = self.getStManager()

        # 设置日志更新
        self.update_log()
        # 监控信息
        self.update_monitor()

    def get_logger(self):
        return self.logger

    def update_log(self):
        self.app.updateLogText()
        self.app.updateSigText()
        self.app.updateErrText()
        #TODO:
        self.top.after(10, self.update_log)

    def update_monitor(self):
        # 更新监控界面策略信息
        strategyDict = self.strategyManager.getStrategyDict()
        for stId in strategyDict:
            self.app.updateStatus(stId, strategyDict[stId])
        self.top.after(1000, self.update_monitor)

    def run(self):
        #启动主界面线程
        self.app.mainloop()
        
    def set_help_text(self, funcName, text):
        self.app.set_help_text(funcName, text)

    def setEditorTextCode(self, path):
        """设置当前编辑的策略路径和代码信息"""
        self.model.setEditorTextCode(path)

    def getEditorText(self):
        return self.model.getEditorText()

    def getStManager(self):
        """获取策略管理器"""
        return self.model.getStrategyManaegr()

    def saveStrategy(self):
        """保存当前策略"""
        self.app.quant_editor.saveEditor()

    def load(self, strategyPath):
        """加载合约事件"""
        self.app.createRunWin()

        config = self.app.runWin.getConfig()
        if config:   # 获取到config
            self._request.loadRequest(strategyPath, config)
            self.logger.info("load strategy")
            return

        return

    def generateReportReq(self, strategyIdList):
        """发送生成报告请求"""
        # TODO：生成报告，如果RepData为空，则显示最新日期的历史报告，
        # TODO：不为空，代表获取到的数据为传过来的数据
        # 查看策略的投资报告(不支持查看多个)
        if len(strategyIdList) >= 1:
            id = strategyIdList[0]
            self._request.reportRequest(id)

        # for id in strategyIdList:
        #     self._request.reportRequest(id)

    def newStrategy(self, path):
        """右键新建策略"""
        if not os.path.exists(path):
            f = open(path, "w")
            f.write('\n'
                    'def initialize(context): \n    pass\n\n\n'
                    'def handle_data(context):\n    pass')
            f.close()

        # 更新策略路径
        self.setEditorTextCode(path)

        self.app.updateStrategyTree(path)

        # 更新策略编辑界面内容
        self.updateEditor(path)

    def newDir(self, path):
        """策略目录右键新建文件夹"""
        if not os.path.exists(path):
            os.makedirs(path)
        self.app.updateStrategyTree(path)

    def updateEditor(self, path):
        """
        更新策略编辑的内容和表头
        :param path: 策略路径，为空则将编辑界面内容置为空
        :return:
        """
        editor = self.getEditorText()
        fileName = os.path.basename(path)

        self.updateEditorHead(fileName)
        self.app.updateEditorText(editor["code"])

    def updateEditorHead(self, text):
        """更新策略表头"""
        self.app.updateEditorHead(text)

    def sendExitRequest(self):
        """发送量化界面退出请求"""
        self._request.quantExitRequest()

    def pauseRequest(self, strategyIdList):
        """
        发送所选策略暂停请求
        :param strategyId: 所选策略Id列表
        :return:
        """
        for id in strategyIdList:
            self._request.strategyPause(id)

    def resumeRequest(self, strategyIdList):
        """
        发送所选策略恢复运行请求
        :param strategyId: 所选策略Id列表
        :return:
        """
        for id in strategyIdList:
            # 策略如果是启动状态，则忽略此次启动请求
            strategyDict = self.strategyManager.getStrategyDict()
            if id in strategyDict:
                status = self.strategyManager.queryStrategyStatus(id)
                if status == ST_STATUS_HISTORY or status == ST_STATUS_CONTINUES:
                    self.logger.info("策略重复启动！")
                    continue
            self._request.strategyResume(id)

    def quitRequest(self, strategyIdList):
        """
        发送所选策略停止请求
        :param strategyId:  所选策略Id列表
        :return:
        """
        for id in strategyIdList:
            strategyDict = self.strategyManager.getStrategyDict()
            if id in strategyDict:
                status = self.strategyManager.queryStrategyStatus(id)
                if status == ST_STATUS_QUIT:
                    print("I have been quitted!")
                    continue
            self._request.strategyQuit(id)

    def delStrategy(self, strategyIdList):
        # 获取策略管理器
        for id in strategyIdList:
            self._request.strategyRemove(id)
            strategyDict = self.strategyManager.getStrategyDict()
            if id in strategyDict:
                self._request.strategyRemove(id)
            else:  # 策略已经停止， 直接删除
                self.app.delUIStrategy(id)

    def signalDisplay(self, strategyIdList):
        # 查看策略的信号及指标图(默认查看一个)
        if len(strategyIdList) >= 1:
            id = strategyIdList[0]
            self._request.strategySignal(id)
