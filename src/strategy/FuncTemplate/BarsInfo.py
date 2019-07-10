import talib


class Bars:
    def __init__(self):
        self._barIndexWhenTrue = 0

    def BarsLast(self, condition, contNo, barType, barValue):
        if not condition:
            return self._barIndexWhenTrue

        barsLast = CurrentBar(contNo, barType, barValue) - self._barIndexWhenTrue
        self._barIndexWhenTrue = CurrentBar(contNo, barType, barValue)
        return barsLast
