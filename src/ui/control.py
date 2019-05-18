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

        # 创建日志更新线程
        self.logThread = ChildThread(self.updateLog)
        # 创建策略信息更新线程
        self.monitorThread = ChildThread(self.updateMonitor, 1)
        # 创建接收引擎数据线程
        self.receiveEgThread = ChildThread(self.model.receiveEgEvent)

    def get_logger(self):
        return self.logger

    def updateLog(self):
        self.app.updateLogText()
        self.app.updateSigText()
        self.app.updateErrText()

    def updateMonitor(self):
        # 更新监控界面策略信息
        strategyDict = self.strategyManager.getStrategyDict()
        for stId in strategyDict:
            self.app.updateStatus(stId, strategyDict[stId])

    def quitThread(self):
        # 停止更新界面子线程
        self.logThread.stop()
        self.logThread.join()
        self.monitorThread.stop()
        self.monitorThread.join()
        # 停止接收策略引擎队列数据
        self.receiveEgThread.stop()
        self.receiveEgThread.join()
        
        self.top.destroy()

    def run(self):
        #启动日志线程
        self.logThread.start()
        #启动监控策略线程
        self.monitorThread.start()
        #启动接收数据线程
        self.receiveEgThread.start()
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
        # 量化启动时的恢复策略列表中的策略没有回测数据
        # 策略停止之后的报告数据从本地获取，不发送请求
        # 策略启动时查看数据发送报告请求，从engine获取数据
        # 查看策略的投资报告(不支持查看多个)
        if len(strategyIdList) >= 1:
            id = strategyIdList[0]
            status = self.strategyManager.queryStrategyStatus(id)
            strategyData = self.strategyManager.getSingleStrategy(id)
            if status == ST_STATUS_QUIT:  # 策略已停止，从本地获取数据
                if "RunningData" not in strategyData:  # 程序启动时恢复的策略没有回测数据
                    messagebox.showinfo("提示", "策略未启动，报告数据不存在", parent=self.top)
                    return
                reportData = strategyData["RunningData"]
                self.app.reportDisplay(reportData, id)
                return
            self._request.reportRequest(id)


    def newStrategy(self, path):
        """右键新建策略"""
        if not os.path.exists(path):
            f = open(path, "w")
            f.write('import talib\n'
                    '\n\n'
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
                    self.logger.info("策略%s已停止!"%(id))
                    continue
                self._request.strategyQuit(id)
            else:
                self.logger.info("策略管理器中不存在策略%s"%(id))

    def delStrategy(self, strategyIdList):
        # 获取策略管理器
        for id in strategyIdList:
            # self._request.strategyRemove(id)
            strategyDict = self.strategyManager.getStrategyDict()
            if id in strategyDict:
                if strategyDict[id]["StrategyState"] == ST_STATUS_QUIT:  # 策略已经停止
                    self.strategyManager.removeStrategy(id)
                    self.app.delUIStrategy(id)
                    # return
                self._request.strategyRemove(id)
            else:  # 策略已经停止， 直接删除
                self.app.delUIStrategy(id)

    def signalDisplay(self, strategyIdList):
        # 查看策略的信号及指标图(默认查看一个)
        if len(strategyIdList) >= 1:
            id = strategyIdList[0]
            self._request.strategySignal(id)


class ChildThread(threading.Thread):
    """带停止标志位的线程"""
    def __init__(self, target, wait=0):
        threading.Thread.__init__(self)

        self.target = target
        self.sleepTime = wait

        # self.cond = threading.Condition()
        self.isStopped = False

    def run(self):
        while not self.isStopped:
            self.target()
            time.sleep(self.sleepTime)

    def stop(self):
        # 设置停止标志位
        self.isStopped = True
