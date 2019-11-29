import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qtui.reportview.fundtab import LineWidget
from qtui.reportview.analysetab import AnalyseTable
from qtui.reportview.tradetab import TradeTab
from qtui.reportview.stagetab import StageTab
from qtui.reportview.graphtab import GraphTab


TABTEXT = {
    1: "资金曲线",
    2: "分析报告",
    3: "阶段总结",
    4: "交易详情",
    5: "图表分析",
}


DATAS = {
	'Fund': [{
		'id': 0,
		'Time': 20191023092700000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 1,
		'Time': 20191023092800000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 2,
		'Time': 20191023093000000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 3,
		'Time': 20191023093100000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 4,
		'Time': 20191023093300000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 5,
		'Time': 20191023093400000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 6,
		'Time': 20191023093500000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	} ,
        {
		'id': 7,
		'Time': 20191023093700000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 8,
		'Time': 20191023093800000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 9,
		'Time': 20191023093900000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	} ,
        {
		'id': 10,
		'Time': 20191023094000000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 11,
		'Time': 20191023094100000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 12,
		'Time': 20191023094200000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	},
        {
		'id': 13,
		'Time': 20191023094300000,
		'TradeDate': 20191023,
		'TradeCost': 0,
		'LongMargin': 0,
		'ShortMargin': 0,
		'Available': 10000000,
		'StaticEquity': 10000000,
		'DynamicEquity': 10000000,
		'YieldRate': 0.0
	}],
	'Stage': {
		'年度分析': [{
			'Time': 20191101,
			'Equity': 9996731.0,
			'NetProfit': -3269.0,
			'TradeTimes': 129,
			'WinTimes': 25,
			'LoseTimes': 104,
			'EventTimes': 0,
			'TotalWin': 8205.0,
			'TotalLose': 11404.0,
			'Returns': -0.0003269,
			'WinRate': 0.1937984496124031,
			'MeanReturns': 2.993055068397054,
			'IncSpeed': -0.0003269
		}],
		'季度分析': [{
			'Time': 20191101,
			'Equity': 9996731.0,
			'NetProfit': -3269.0,
			'TradeTimes': 129,
			'WinTimes': 25,
			'LoseTimes': 104,
			'EventTimes': 0,
			'TotalWin': 8205.0,
			'TotalLose': 11404.0,
			'Returns': -0.0003269,
			'WinRate': 0.1937984496124031,
			'MeanReturns': 2.993055068397054,
			'IncSpeed': -0.0003269
		}],
		'月度分析': [{
			'Time': 20191031,
			'Equity': 9996955.0,
			'NetProfit': -3045.0,
			'TradeTimes': 127,
			'WinTimes': 24,
			'LoseTimes': 103,
			'EventTimes': 0,
			'TotalWin': 7846.0,
			'TotalLose': 11021.0,
			'Returns': -0.0003045,
			'WinRate': 0.1889763779527559,
			'MeanReturns': 3.055295950155763,
			'IncSpeed': -0.0003045
		},{
			'Time': 20191101,
			'Equity': 9996731.0,
			'NetProfit': -224.0,
			'TradeTimes': 2,
			'WinTimes': 1,
			'LoseTimes': 1,
			'EventTimes': 0,
			'TotalWin': 359.0,
			'TotalLose': 383.0,
			'Returns': -2.24e-05,
			'WinRate': 0.5,
			'MeanReturns': 0.9373368146214099,
			'IncSpeed': 0.00028209999999999997
		}],
		'周分析': [{
			'Time': 20191025,
			'Equity': 10000035.0,
			'NetProfit': 35.0,
			'TradeTimes': 47,
			'WinTimes': 9,
			'LoseTimes': 38,
			'EventTimes': 0,
			'TotalWin': 3551.0,
			'TotalLose': 3546.0,
			'Returns': 3.5e-06,
			'WinRate': 0.19148936170212766,
			'MeanReturns': 4.228175722253557,
			'IncSpeed': 3.5e-06
		}, {
			'Time': 20191101,
			'Equity': 9996731.0,
			'NetProfit': -3304.0,
			'TradeTimes': 82,
			'WinTimes': 16,
			'LoseTimes': 66,
			'EventTimes': 0,
			'TotalWin': 4654.0,
			'TotalLose': 7858.0,
			'Returns': -0.0003304,
			'WinRate': 0.1951219512195122,
			'MeanReturns': 2.443083481801985,
			'IncSpeed': -0.0003339
		}],
		'日分析': [{
			'Time': 20191023,
			'Equity': 10001445.0,
			'NetProfit': 1445.0,
			'TradeTimes': 12,
			'WinTimes': 2,
			'LoseTimes': 10,
			'EventTimes': 0,
			'TotalWin': 2168.0,
			'TotalLose': 963.0,
			'Returns': 0.0001445,
			'WinRate': 0.16666666666666666,
			'MeanReturns': 11.256490134994808,
			'IncSpeed': 0.0001445
		}, {
			'Time': 20191024,
			'Equity': 9999767.0,
			'NetProfit': -1678.0,
			'TradeTimes': 19,
			'WinTimes': 3,
			'LoseTimes': 16,
			'EventTimes': 0,
			'TotalWin': 187.0,
			'TotalLose': 1625.0,
			'Returns': -0.0001678,
			'WinRate': 0.15789473684210525,
			'MeanReturns': 0.6137435897435898,
			'IncSpeed': -0.0003123
		}, {
			'Time': 20191025,
			'Equity': 10000035.0,
			'NetProfit': 268.0,
			'TradeTimes': 16,
			'WinTimes': 4,
			'LoseTimes': 12,
			'EventTimes': 0,
			'TotalWin': 1196.0,
			'TotalLose': 958.0,
			'Returns': 2.68e-05,
			'WinRate': 0.25,
			'MeanReturns': 3.7453027139874737,
			'IncSpeed': 0.00019460000000000001
		}, {
			'Time': 20191028,
			'Equity': 9998979.0,
			'NetProfit': -1056.0,
			'TradeTimes': 18,
			'WinTimes': 3,
			'LoseTimes': 15,
			'EventTimes': 0,
			'TotalWin': 337.0,
			'TotalLose': 1993.0,
			'Returns': -0.0001056,
			'WinRate': 0.16666666666666666,
			'MeanReturns': 0.8454591068740592,
			'IncSpeed': -0.00013240000000000002
		}, {
			'Time': 20191029,
			'Equity': 9999683.0,
			'NetProfit': 704.0,
			'TradeTimes': 23,
			'WinTimes': 5,
			'LoseTimes': 18,
			'EventTimes': 0,
			'TotalWin': 2985.0,
			'TotalLose': 1661.0,
			'Returns': 7.04e-05,
			'WinRate': 0.21739130434782608,
			'MeanReturns': 6.469596628537026,
			'IncSpeed': 0.000176
		} , {
			'Time': 20191030,
			'Equity': 9996771.0,
			'NetProfit': -2912.0,
			'TradeTimes': 26,
			'WinTimes': 3,
			'LoseTimes': 23,
			'EventTimes': 0,
			'TotalWin': 117.0,
			'TotalLose': 2969.0,
			'Returns': -0.0002912,
			'WinRate': 0.11538461538461539,
			'MeanReturns': 0.30212192657460424,
			'IncSpeed': -0.0003616
		}, {
			'Time': 20191031,
			'Equity': 9996955.0,
			'NetProfit': 184.0,
			'TradeTimes': 13,
			'WinTimes': 4,
			'LoseTimes': 9,
			'EventTimes': 0,
			'TotalWin': 856.0,
			'TotalLose': 852.0,
			'Returns': 1.84e-05,
			'WinRate': 0.3076923076923077,
			'MeanReturns': 2.26056338028169,
			'IncSpeed': 0.0003096
		}, {
			'Time': 20191101,
			'Equity': 9996731.0,
			'NetProfit': -224.0,
			'TradeTimes': 2,
			'WinTimes': 1,
			'LoseTimes': 1,
			'EventTimes': 0,
			'TotalWin': 359.0,
			'TotalLose': 383.0,
			'Returns': -2.24e-05,
			'WinRate': 0.5,
			'MeanReturns': 0.9373368146214099,
			'IncSpeed': -4.08e-05
		}]
	},
	'Orders': [{
		'Order': {
			'UserNo': 'Default',
			'OrderType': '2',
			'ValidType': '0',
			'ValidTime': '0',
			'Cont': 'ZCE|F|AP|001',
			'Direct': 'S',
			'Offset': 'O',
			'Hedge': 'T',
			'OrderPrice': 7896.0,
			'OrderQty': 1,
			'DateTimeStamp': 20191023094500000,
			'TradeDate': 20191023,
			'TriggerType': 'H',
			'CurBar': {
				'ContractNo': 'ZCE|F|AP|001',
				'DateTimeStamp': 20191023094500000,
				'HighPrice': 7897.0,
				'KLineIndex': 20,
				'KLineQty': 738,
				'KLineSlice': 1,
				'KLineType': 'M',
				'LastPrice': 7896.0,
				'LowPrice': 7893.0,
				'OpeningPrice': 7894.0,
				'PositionQty': 155140,
				'Priority': 30002,
				'SettlePrice': 7903.0,
				'TotalQty': 127140,
				'TradeDate': 20191023,
				'DateTimeStampForSort': '20191023094400000000'
			},
			'CurBarIndex': 20,
			'StrategyId': 2,
			'StrategyName': 'DualMA',
			'StrategyStage': 'H',
			'OrderId': 0
		},
		'Cost': 1.0,
		'Margin': 789.6,
		'Turnover': 78960.0,
		'LiquidateProfit': 0,
		'Profit': -1.0,
		'SlippageLoss': 0.0,
		'OpenLink': None,
		'LinkNum': 0,
		'LeftNum': 0
	}, {
		'Order': {
			'UserNo': 'Default',
			'OrderType': '2',
			'ValidType': '0',
			'ValidTime': '0',
			'Cont': 'ZCE|F|AP|001',
			'Direct': 'B',
			'Offset': 'C',
			'Hedge': 'T',
			'OrderPrice': 7901.0,
			'OrderQty': 1,
			'DateTimeStamp': 20191023100000000,
			'TradeDate': 20191023,
			'TriggerType': 'H',
			'CurBar': {
				'ContractNo': 'ZCE|F|AP|001',
				'DateTimeStamp': 20191023100000000,
				'HighPrice': 7906.0,
				'KLineIndex': 35,
				'KLineQty': 1722,
				'KLineSlice': 1,
				'KLineType': 'M',
				'LastPrice': 7901.0,
				'LowPrice': 7889.0,
				'OpeningPrice': 7889.0,
				'PositionQty': 153710,
				'Priority': 30002,
				'SettlePrice': 7900.0,
				'TotalQty': 144990,
				'TradeDate': 20191023,
				'DateTimeStampForSort': '20191023095900000000'
			},
			'CurBarIndex': 35,
			'StrategyId': 2,
			'StrategyName': 'DualMA',
			'StrategyStage': 'H',
			'OrderId': 1
		},
		'Cost': 1.0,
		'Margin': 0,
		'Turnover': 79010.0,
		'LiquidateProfit': -50.0,
		'Profit': -51.0,
		'SlippageLoss': 0.0,
		'OpenLink': [{
			'id': 0,
			'vol': 1
		}],
		'LinkNum': 1,
		'LeftNum': 0
	}],
	'Detail': {
		'InitialFund': 10000000.0,
		'Contract': ['ZCE|F|AP|001'],
		'Period': '1分钟',
		'StartTime': 20191023,
		'EndTime': 20191101,
		'TestDay': 10,
		'FinalEquity': 9996731.0,
		'EmptyPeriod': 16,
		'MaxContinueEmpty': 1,
		'StdDev': 261.91196752582573,
		'StdDevRate': -10.56162669922836,
		'Sharpe': 0.0006531492478894995,
		'PlmLm': -0.22615211852770278,
		'MaxRetrace': 5762.0,
		'MaxRetraceTime': 20191031105900000,
		'MaxRetraceRate': 0.000576079772151552,
		'MaxRetraceRateTime': 20191031105900000,
		'Risky': 0.0003674999999999651,
		'RateofReturnRisk': -31.772380952383973,
		'Returns': -0.0003199,
		'RealReturns': -0.0003199,
		'AnnualizedSimple': -0.01167635,
		'MonthlySimple': -0.0009597000000000002,
		'AnnualizedCompound': -0.011862875303423892,
		'MonthlyCompound': -0.000980379444103785,
		'WinRate': 0.1937984496124031,
		'MeanWinLose': 2.993055068397054,
		'MeanWinLoseRate': -3.898787724415243,
		'NetProfit': -3199.0,
		'TotalWin': 8205.0,
		'TotalLose': 11404.0,
		'RatioofWinLose': 0.7194843914415995,
		'HoldProfit': -70.0,
		'TradeTimes': 129,
		'WinPercentage': 0.1937984496124031,
		'WinTimes': 25,
		'LoseTimes': 104,
		'EventTimes': 0,
		'MeanProfit': -24.7984496124031,
		'MeanWin': 328.2,
		'MeanLose': 109.65384615384616,
		'MaxWinContinueDays': 1,
		'MaxWinContinueDaysTime': '20191024 - 20191024',
		'MaxLoseContinueDays': 4,
		'MaxLoseContinueDaysTime': '20191029 - 20191101',
		'MaxWinComparedIncreaseContinueDays': 1,
		'MaxWinComparedIncreaseContinueDaysTime': '20191028 - 20191028',
		'MaxLoseComparedIncreaseContinueDays': 1,
		'MaxLoseComparedIncreaseContinueDaysTime': '20191025 - 20191025',
		'MaxEquity': 10002087.0,
		'MinEquity': 9996325.0,
		'Cost': 259.0,
		'SlippageCost': 0.0,
		'Turnover': 20618400.0
	},
	'KLineType': {
		'KLineType': 'M',
		'KLineSlice': 1
	}
}


class Tab(QTabWidget):

    def __init__(self, parent=None):
        super(Tab, self).__init__(parent)
        self._createTab()

    def _createTab(self):
        self.fundTab = LineWidget()
        self.analyseTab = AnalyseTable()
        self.stageTab = StageTab()
        self.tradeTab = TradeTab()
        self.graphTab = GraphTab()

        self.addTab(self.fundTab, "资金详情")
        self.addTab(self.analyseTab, "分析报告")
        self.addTab(self.stageTab, "阶段总结")
        self.addTab(self.tradeTab, "交易详情")
        self.addTab(self.graphTab, "图表分析")

    def showData(self, datas):
        """显示回测结果"""
        self._addFundData(datas)
        self._addAnalyseData(datas)
        self._addStageData(datas)
        self._addTradeData(datas)
        self._addGraphData(datas)

    def _addFundData(self, datas):
        try:
            fundDatas = datas['Fund']
        except Exception as e:
            raise e
        self.fundTab.loadData(fundDatas)

    def _addAnalyseData(self, datas):
        try:
            details = datas["Detail"]
        except Exception as e:
            raise e
        self.analyseTab.addAnalyseResult(details)

    def _addStageData(self, datas):
        try:
            stage = datas["Stage"]
        except Exception as e:
            raise e
        self.stageTab.addStageDatas(stage)

    def _addTradeData(self, datas):
        try:
            orders = datas["Orders"]
            kLineInfo = datas["KLineType"]
        except Exception as e:
            raise e
        self.tradeTab.addTradeDatas(orders, kLineInfo)

    def _addGraphData(self, datas):
        try:
            stage = datas["Stage"]
        except Exception as e:
            raise e
        self.graphTab.addGraphDatas(stage)