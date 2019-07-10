from capi.com_types import *


class LimitCtl(object):

    def __init__(self, logger, maxConOpenTimes, maxCurBarOpenTime, openNotReverse, coverNotOpen):

        self._logger = logger
        # 限制
        self._maxConOpenTime   = maxConOpenTimes      # 最大连续同向开仓次数
        self._maxCurBarOpenTime = maxCurBarOpenTime   # 最大每根K线同向开仓次数
        self._openNotReverse   = openNotReverse       # 开仓的当前K线不允许平仓
        self._coverNotOpen     = coverNotOpen         # 平仓的当前K线不允许开仓

        self._conOpenTime          = 0                # 连续同向开仓次数

        self._curBarOpenTime    = self._initCurBarOpenTime()   # 每根K线同向开仓次数

        self._hasCover         = False                # 当前K线是否有平仓单
        self._hasOpen          = False                # 当前K线是否有开仓单

        self._curBarIndex      = 0                    # 当前bar序号

    def _setCurBarIndex(self, index):
        if index == self._curBarIndex:
            return
        self._curBarIndex = index

    def _initCurBarOpenTime(self):
        self._curBarOpenTime = {
            "BuyOpen" : 0,
            "SellOpen":  0,
            "Buy"     :  0,
            "Sell"    :  0
        }

    def _setDCurBarOpenTime(self, order):
        """设置某一方向的开仓次数"""
        if order["Direct"] == dBuy and order["Offset"] == oOpen:  # 买开
            self._curBarOpenTime["BuyOpen"] += 1

        elif order["Direct"] == dSell and order["Offset"] == oOpen:  # 卖开
            self._curBarOpenTime["SellOpen"] += 1

        elif order["Direct"] == dBuy and order["Offset"] == oNone:  # 买
            self._curBarOpenTime["Buy"] += 1

        elif order["Direct"] == dSell and order["Offset"] == oNone:  # 卖
            self._curBarOpenTime["Sell"] += 1
        else:
            pass

    def _allowConOpen(self, order, lastOrder):
        """
        判断是否满足连续同向开仓次数限制，连续同向开仓次数是对策略限制的
        :param order: 订单
        :param lastOrder: 前一个订单
        :return: 1：订单满足限制条件   -1： 订单不满足限制条件
        """
        # TODO：暂时没有考虑外盘(外盘通过订单无法判断)
        if self._maxConOpenTime == -1:
            return 1  #  连续开仓次数不做限制

        if len(lastOrder) < 1:
            return 1

        if order["Offset"] == oOpen or order["Offset"] == oNone:   # 开仓单或外盘订单
            if lastOrder["Direct"] == order["Direct"] and \
                    lastOrder["Offset"] == order["Offset"]:  # 订单方向相同
                if self._conOpenTime >= self._maxConOpenTime:
                    return -1   # 大于同向开仓次数限制

        return 1

    def _allowCurBarOpen(self, order):
        """
        每根K线同向开仓次数是否满足条件
        :param order: 订单
        :param lastOrder: 前一个订单
        :return: 1：订单满足限制条件   -1： 订单不满足限制条件
        """
        # TODO：暂时没有考虑外盘
        if self._maxCurBarOpenTime == -1:
            return 1   # 每根K线同向开仓次数不做限制

        if order["CurBarIndex"] == self._curBarIndex:
            if order["Offset"] == oOpen or order["Offset"] == oNone:
                if order["Direct"] == dBuy and order["Offset"] == oOpen:  # 买开
                    if self._curBarOpenTime["BuyOpen"] >= self._maxCurBarOpenTime:
                        return -1

                elif order["Direct"] == dSell and order["Offset"] == oOpen:  # 卖开
                    if self._curBarOpenTime["SellOpen"] >= self._maxCurBarOpenTime:
                        return -1

                elif order["Direct"] == dBuy and order["Offset"] == oNone:  # 买
                    if self._curBarOpenTime["Buy"] >= self._maxCurBarOpenTime:
                        return -1

                elif order["Direct"] == dSell and order["Offset"] == oNone:  # 卖
                    if self._curBarOpenTime["Sell"] >= self._maxCurBarOpenTime:
                        return -1
                else:
                    pass

        return 1

    def _allowCover(self, order):
        """
        开仓的当前K线是否可以平仓判断
        :param order: 订单
        :return:  1：订单满足限制条件   -1： 订单不满足限制条件
        """
        # TODO：暂时没有考虑外盘
        if self._openNotReverse == 0:
            return 1   # 不做限制

        if order["CurBarIndex"] == self._curBarIndex:
            if self._hasOpen:
                if order["Offset"] == oCover:
                    return -1

        return 1

    def _allowOpen(self, order):
        """
        平仓的当前K线是否可以开仓判断
        :param order: 订单
        :return:  1：订单满足限制条件   -1： 订单不满足限制条件
        """
        # TODO：暂时没有考虑外盘
        if self._coverNotOpen == 0:
            return 1   # 不做限制

        if order["CurBarIndex"] == self._curBarIndex:
            if self._hasCover:     # 当前K线存在平仓单
                if order["Offset"] == oOpen:
                    return -1

        return 1

    def allowOrder(self, order, lastOrder):
        """
        判断是否可以下单
        :param order:
        :param lastOrder:
        :return: 0: 可以下单， -1: 不能下单
        """

        ret1 = self._allowConOpen(order, lastOrder)
        ret2 = self._allowCurBarOpen(order)
        ret3 = self._allowCover(order)
        ret4 = self._allowOpen(order)

        if ret1 == 1 and ret2 == 1 and ret3 == 1 and ret4 == 1:
            self._setConOpenTime(order, lastOrder)
            self._setCurBarOpenTime(order)
            self._setHasOpen(order)
            self._setHasCover(order)
            self._setCurBarIndex(order["CurBarIndex"])
            return 1
        else:
            return 0

    def _setConOpenTime(self, order, lastOrder):
        """更新连续同向开仓次数"""
        if self._maxConOpenTime == -1:
            return

        if len(lastOrder) < 1:
            if order["Offset"] == oOpen or order["Offset"] == oNone:
                self._conOpenTime += 1
                return

        if order["Offset"] == oOpen or order["Offset"] == oNone:   # 开仓单或外盘订单
            if lastOrder["Direct"] == order["Direct"] and \
                    lastOrder["Offset"] == order["Offset"]:  # 订单方向相同
                self._conOpenTime += 1

            else:
                self._conOpenTime = 1

        else:
            self._conOpenTime = 0

    def _setCurBarOpenTime(self, order):
        """更新每根K线同向开仓次数"""
        if self._maxCurBarOpenTime == -1:  # 每根K线同向开仓次数不做限制
            return

        if order["CurBarIndex"] == self._curBarIndex:

            if order["Offset"] == oOpen or order["Offset"] == oNone:
                self._setDCurBarOpenTime(order)

        else:
            if order["Offset"] == oOpen or order["Offset"] == oNone:
                if order["Direct"] == dBuy and order["Offset"] == oOpen:  # 买开
                    self._initCurBarOpenTime()
                    self._curBarOpenTime["BuyOpen"] += 1

                elif order["Direct"] == dSell and order["Offset"] == oOpen:  # 卖开
                    self._initCurBarOpenTime()
                    self._curBarOpenTime["SellOpen"] += 1

                elif order["Direct"] == dBuy and order["Offset"] == oNone:  # 买
                    self._initCurBarOpenTime()
                    self._curBarOpenTime["Buy"] += 1

                elif order["Direct"] == dSell and order["Offset"] == oNone:  # 卖
                    self._initCurBarOpenTime()
                    self._curBarOpenTime["Sell"] += 1
                else:
                    pass
            else:
                self._initCurBarOpenTime()

    def _setHasOpen(self, order):
        """更新当前K线是否有开仓单"""
        # if order["Offset"] == oOpen:
        #     self._hasOpen = True
        if self._openNotReverse == 0:
            return

        if order["CurBarIndex"] == self._curBarIndex:
            if order["Offset"] == oOpen:
                self._hasOpen = True
        else:
            if order["Offset"] == oOpen:
                self._hasOpen = True
            else:
                self._hasOpen = False

    def _setHasCover(self, order):
        """更新当前K线是否有平仓单"""
        if self._coverNotOpen == 0:
            return

        if order["CurBarIndex"] == self._curBarIndex:
            if order["Offset"] == oCover:
                self._hasCover = True
        else:
            if order["Offset"] == oCover:
                self._hasCover = True
            else:
                self._hasCover = False


class DirectionCtl(object):
    """根据用户选择的交易方向判断订单是否满足下单要求"""
    def __init__(self, logger, direction):
        self._logger = logger
        self._direction = direction

        self._dirCtlCallback()

    def _dirCtlCallback(self):
        self._dirCtlDict = {
            1      : self._longTrade,
            2      : self._shortTrade,
        }

    def handleDirCtl(self, order):
        if self._direction not in self._dirCtlDict and self._direction != 0:
            self._logger.error("Unknown trade direction (%d)" % self._direction)
            return 0
        elif self._direction == 0:
            return 1
        else:
            return self._dirCtlDict[self._direction](order)

    def _longTrade(self, order):
        """交易方向仅多头"""
        if order["Direct"] == dSell and order["Offset"] == oOpen:   # 空头不下单
            return 0
        return 1

    def _shortTrade(self, order):
        """交易方向仅空头"""
        if order["Direct"] == dBuy and order["Offset"] == oOpen:  # 多头不下单
            return 0
        return 1








