from pyqtgraph.Qt import QtGui, QtCore, QtWidgets
from pyqtgraph.Point import Point
import pyqtgraph as pg
import datetime as dt
import traceback
import pandas as pd


def int2date(d):
    # 去掉最后三个0
    millisecond = d%1000
    second = int(d/1000)%100
    minute = int(d/100000)%100
    hour = int(d/10000000)%100
    day = int(d/1000000000)%100
    month = int(d/100000000000)%100
    year = int(d/10000000000000)
    time = '{:0>4d}-{:0>2d}-{:0>2d} {:0>2d}:{:0>2d}:{:0>2d}'.format(year, month, day, hour, minute, second)
    return time


########################################################################
# 十字光标支持
########################################################################
class Crosshair(QtCore.QObject):
    """
    此类给pg.PlotWidget()添加crossHair功能,PlotWidget实例需要初始化时传入
    """
    signal = QtCore.pyqtSignal(type(tuple([])))

    # ----------------------------------------------------------------------
    def __init__(self, parent, master):
        """Constructor"""
        self.__view = parent
        self.master = master
        super(Crosshair, self).__init__()

        self.xAxis = 0
        self.yAxis = 0

        # 文字信息是否显示标志位
        self.flags = False

        self.datas = None

        self.yAxises = 0
        self.leftX = 0
        self.showHLine = False
        self.textPrices = pg.TextItem('', anchor=(1, 1))
        self.view = parent.centralWidget.getItem(1, 0)
        self.rect = self.view.sceneBoundingRect()
        self.vLines = pg.InfiniteLine(angle=90, movable=False)
        self.hLines = pg.InfiniteLine(angle=0, movable=False)

        # mid 在y轴动态跟随最新价显示资金信息和最新时间
        self.__textDate = pg.TextItem('date')
        self.__textInfo = pg.TextItem('lastBarInfo')

        self.__textDate.setZValue(2)
        # 堆叠顺序置于下层
        self.__textInfo.setZValue(-1)
        self.__textInfo.border = pg.mkPen(color=(181, 181, 181, 255), width=1.2)

        self.__texts = [self.__textDate, self.__textInfo, self.textPrices]

        self.textPrices.setZValue(2)
        self.vLines.setPos(0)
        self.hLines.setPos(0)
        self.view.addItem(self.vLines)
        self.view.addItem(self.hLines)
        self.view.addItem(self.textPrices)

        self.view.addItem(self.__textInfo, ignoreBounds=True)
        self.view.addItem(self.__textDate, ignoreBounds=True)

        self.__setVisibileOrNot(self.flags)

        self.proxy = pg.SignalProxy(self.__view.scene().sigMouseMoved, rateLimit=60, slot=self.__mouseMoved)
        self.click_slot = pg.SignalProxy(self.__view.scene().sigMouseClicked, rateLimit=60, slot=self.__mouseClicked)
        # 跨线程刷新界面支持
        self.signal.connect(self.update)

    def __setVisibileOrNot(self, flags):
        """Set the text visiblity"""
        self.vLines.setVisible(flags)
        self.hLines.setVisible(flags)

        for obj in self.__texts:
            obj.setVisible(flags)

    # ----------------------------------------------------------------------
    def update(self, pos):
        """刷新界面显示"""
        xAxis, yAxis = pos
        xAxis, yAxis = (self.xAxis, self.yAxis) if xAxis is None else (xAxis, yAxis)
        if self.datas is None:
            return
        self.moveTo(xAxis, yAxis)

    # ----------------------------------------------------------------------
    def __mouseMoved(self, evt):
        """鼠标移动回调"""
        if self.datas is None:
            return
        pos = evt[0]
        self.rect = self.view.sceneBoundingRect()

        self.showHLine = False
        if self.rect.contains(pos):
            mousePoint = self.view.vb.mapSceneToView(pos)
            xAxis = mousePoint.x()
            yAxis = mousePoint.y()
            self.yAxises = yAxis
            self.showHLine = True
            self.moveTo(xAxis, yAxis)

    # ----------------------------------------------------------------------
    def __mouseClicked(self):
        self.__setVisibileOrNot(not self.flags)
        self.flags = not self.flags

    # ----------------------------------------------------------------------
    #TODO: 不生效
    def eventFilter(self, obj, event):
        """事件过滤器,用于解决鼠标进入其它控件后还原为标准鼠标样式"""
        if obj is self.__view:
            if event.type() == QtCore.QEvent.MouseButtonPress:
                print("bc")
            elif event.type() == QtCore.QEvent.MouseButtonRelease:
                print('ha')

        return QtWidgets.QWidget.eventFilter(self, obj, event)

    def __mouseLeaved(self):
        print("testing....")

    # ----------------------------------------------------------------------
    def moveTo(self, xAxis, yAxis):
        xAxis, yAxis = (self.xAxis, self.yAxis) if xAxis is None else (xAxis, yAxis)
        self.rect = self.view.sceneBoundingRect()
        if not xAxis or not yAxis:
            return
        self.xAxis = xAxis
        self.yAxis = yAxis
        self.vhLinesSetXY(xAxis, yAxis)
        self.plotPrice(yAxis)
        self.plotInfo(xAxis)

    # ----------------------------------------------------------------------
    def vhLinesSetXY(self, xAxis, yAxis):
        """水平和竖线位置设置"""
        self.vLines.setPos(xAxis)
        if self.showHLine:
            self.hLines.setPos(yAxis)
        else:
            topLeft = self.view.vb.mapSceneToView(QtCore.QPointF(self.rect.left(), self.rect.top()))
            self.hLines.setPos(topLeft.y() + abs(topLeft.y()))

    # ----------------------------------------------------------------------
    def plotPrice(self, yAxis):
        """价格位置设置"""
        if self.showHLine:
            rightAxis = self.view.getAxis('right')
            rightAxisWidth = rightAxis.width()
            topRight = self.view.vb.mapSceneToView(
                QtCore.QPointF(self.rect.right() - rightAxisWidth, self.rect.top()))
            self.textPrices.setHtml(
                '<div style="text-align: right;">\
                    <span style="color: yellow; font-size: 12px;">\
                      %0.3f\
                    </span>\
                </div>' \
                % (yAxis))
            self.textPrices.setPos(topRight.x(), yAxis)
        else:
            topRight = self.view.vb.mapSceneToView(QtCore.QPointF(self.rect.right(), self.rect.top()))
            self.textPrices.setPos(topRight.x(), topRight.y() + abs(topRight.y()))

    # ----------------------------------------------------------------------
    def plotInfo(self, xAxis):
        """
        被嵌入的plotWidget在需要的时候通过调用此方法显示K线信息
        """
        xAxis = round(xAxis)
        if self.datas is None:
            return
        try:
            # 获取资金数据
            Time = self.datas.Time[int(xAxis)]
            TradeDate = self.datas.TradeDate[int(xAxis)]
            TradeCost = self.datas.TradeCost[int(xAxis)]
            LongMargin = self.datas.LongMargin[int(xAxis)]
            ShortMargin = self.datas.ShortMargin[int(xAxis)]
            Available = self.datas.Available[int(xAxis)]
            StaticEquity = self.datas.StaticEquity[int(xAxis)]
            DynamicEquity = self.datas.DynamicEquity[int(xAxis)]
            YieldRate = self.datas.YieldRate[int(xAxis)]
        except Exception as e:
            return

        tickDatetime = int2date(Time)

        if (isinstance(tickDatetime, dt.datetime)):
            datetimeText = dt.datetime.strftime(tickDatetime, '%Y-%m-%d %H:%M:%S')
            dateText = dt.datetime.strftime(tickDatetime, '%Y-%m-%d')
            timeText = dt.datetime.strftime(tickDatetime, '%H:%M:%S')
        elif (isinstance(tickDatetime, (str))):
            datetimeText = tickDatetime

            dateTemp = dt.datetime.strptime(datetimeText, '%Y-%m-%d %H:%M:%S')

            dateText = dt.datetime.strftime(dateTemp, '%Y-%m-%d')
            timeText = dt.datetime.strftime(dateTemp, '%H:%M:%S')
        else:
            datetimeText = ""
            dateText = ""
            timeText = ""

        self.__textInfo.setHtml(
            u'<div style="text-align: center; background-color:#000;height:auto ">\
                <span style="color: white;  font-size: 12px;">时间</span><br>\
                <span style="color: #96CDCD; font-size: 12px;">%s</span><br>\
                <span style="color: white;  font-size: 12px;">交易日</span><br>\
                <span style="color: #96CDCD; font-size: 12px;">%s</span><br>\
                <span style="color: white;  font-size: 12px;">手续费</span><br>\
                <span style="color: #96CDCD;     font-size: 12px;">%.2f</span><br>\
                <span style="color: white;  font-size: 12px;">多头保证金</span><br>\
                <span style="color: #96CDCD;     font-size: 12px;">%.2f</span><br>\
                <span style="color: white;  font-size: 12px;">空头保证金</span><br>\
                <span style="color: #96CDCD;     font-size: 12px;">%.2f</span><br>\
                <span style="color: white;  font-size: 12px;">可用资金</span><br>\
                <span style="color: #96CDCD;     font-size: 12px;">%.2f</span><br>\
                <span style="color: white;  font-size: 12px;">静态权益</span><br>\
                <span style="color: #96CDCD; font-size: 12px;">%.2f</span><br>\
                <span style="color: white;  font-size: 12px;">动态权益</span><br>\
                <span style="color: #96CDCD;     font-size: 12px;">%.2f</span><br>\
                <span style="color: white;  font-size: 12px;">收益率</span><br>\
                <span style="color: #96CDCD; font-size: 12px;">%.2f</span><br>\
            </div>' \
            % (Time, TradeDate, TradeCost, LongMargin, ShortMargin, Available, StaticEquity, DynamicEquity, YieldRate))

        self.__textDate.setHtml(
            '<div style="text-align: center">\
                <span style="color: yellow; font-size: 12px;">%s</span>\
            </div>' \
            % (datetimeText))

        # 资金信息，左上角显示
        leftAxis = self.view.getAxis('left')
        leftAxisWidth = leftAxis.width()
        topLeft = self.view.vb.mapSceneToView(
            QtCore.QPointF(self.rect.left() + leftAxisWidth, self.rect.top()))
        x = topLeft.x()
        y = topLeft.y()
        self.__textInfo.setPos(x, y)

        # X坐标时间显示
        rectTextDate = self.__textDate.boundingRect()
        rectTextDateHeight = rectTextDate.height()
        bottomAxis = self.view.getAxis('bottom')
        bottomAxisHeight = bottomAxis.height()
        bottomRight = self.view.vb.mapSceneToView(QtCore.QPointF(self.rect.width(),
                                                                     self.rect.bottom() - (
                                                                                bottomAxisHeight + rectTextDateHeight)))
        # 修改对称方式防止遮挡
        if xAxis > self.master.index:
            self.__textDate.anchor = Point((1, 0))
        else:
            self.__textDate.anchor = Point((0, 0))
        self.__textDate.setPos(xAxis, bottomRight.y())

