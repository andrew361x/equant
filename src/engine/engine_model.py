from capi.event import *
from copy import deepcopy
from datetime import datetime,timedelta
from .trade_model import TradeModel
from .quote_model import QuoteModel

class DataModel(object):
    def __init__(self, logger):
        self.logger = logger
        self._quoteModel = QuoteModel(logger)
        self._tradeModel = TradeModel(logger)

    def getTradeModel(self):
        return self._tradeModel

    def getQuoteModel(self):
        return self._quoteModel