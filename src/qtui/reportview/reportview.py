import sys
sys.path.append(".")

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qtui.reportview.dir import Dir
from qtui.reportview.tab import Tab


class ReportView(QWidget):

    # 显示回测报告窗口信号
    reportShowSig = pyqtSignal(list)

    def __init__(self, parent=None):
        super(ReportView, self).__init__(parent)
        self.parent=parent
        self._windowTitle = "回测报告"
        self._iconPath = r"icon/epolestar ix2.ico"
        self.styleFile = r"qtui/reportview/style.qss"

        self._datas = None

        self.setWindowTitle(self._windowTitle)
        self.setWindowIcon(QIcon(self._iconPath))

        self.initSettings()
        # 初始化界面
        self._initUI()
        # 接收报告显示信号
        self.reportShowSig.connect(self.showCallback)

    def _initUI(self):

        vLayout = QHBoxLayout()
        vLayout.setContentsMargins(0, 0, 0, 0)
        vLayout.setSpacing(0)

        self.tab = Tab()   #回测报告窗体
        self.tab.setObjectName("ReportTab")
        self.dir = Dir(self) #在左侧显示 资金详情 分析报告 阶段总结 交易详情 图表分析

        vLayout.addSpacing(0)
        vLayout.addWidget(self.dir)
        vLayout.setSpacing(1)
        vLayout.addWidget(self.tab)
        vLayout.setSpacing(2)

        self.setLayout(vLayout)

    def showCallback(self, datas):
        # 传入回测数据
        self._datas = datas[0]
        path = datas[1]

        self.tab.showData(self._datas)
        self.selectReportItem(path)

        self.parent.show()
        self.parent.raise_()
        # self.show()

    def selectReportItem(self, path):
        """定位报告位置"""
        index = self.dir.model.index(path)
        self.dir.expand(index.parent())
        self.dir.setCurrentIndex(index)

    def initSettings(self):
        self._settings = QSettings('config/settings.ini', QSettings.IniFormat)

    def saveSettings(self):
        """保存投资报告界面布局"""
        self._settings.setValue("report_win_geometry", self.parent.frameGeometry())

    def loadSettings(self):
        """设置保存的界面布局"""
        if self._settings.contains("report_win_geometry"):
            self.parent.setGeometry(self._settings.value("report_win_geometry"))
        else:
            pass


