/*!-----------------------------------------------------------------------------
 * Copyright (c) Microsoft Corporation. All rights reserved.
 * monaco-languages version: 1.8.0(0ed9a6c3e90a24375fab54f7205fb76ce992f117)
 * Released under the MIT license
 * https://github.com/Microsoft/monaco-languages/blob/master/LICENSE.md
 *-----------------------------------------------------------------------------*/
define("vs/basic-languages/python/python",["require","exports"],function(e,n){"use strict";Object.defineProperty(n,"__esModule",{value:!0});var t="undefined"==typeof monaco?self.monaco:monaco;n.conf={comments:{lineComment:"#",blockComment:["'''","'''"]},brackets:[["{","}"],["[","]"],["(",")"]],autoClosingPairs:[{open:"{",close:"}"},{open:"[",close:"]"},{open:"(",close:")"},{open:'"',close:'"',notIn:["string"]},{open:"'",close:"'",notIn:["string","comment"]}],surroundingPairs:[{open:"{",close:"}"},{open:"[",close:"]"},{open:"(",close:")"},{open:'"',close:'"'},{open:"'",close:"'"}],onEnterRules:[{beforeText:new RegExp("^\\s*(?:def|class|for|if|elif|else|while|try|with|finally|except|async).*?:\\s*$"),action:{indentAction:t.languages.IndentAction.Indent}}],folding:{offSide:!0,markers:{start:new RegExp("^\\s*#region\\b"),end:new RegExp("^\\s*#endregion\\b")}}},n.language={defaultToken:"",tokenPostfix:".python",keywords:["abs","all","and","any","apply","as","assert","basestring","bin","bool","break","buffer","bytearray","callable","chr","class","classmethod","cmp","coerce","compile","complex","continue","def","del","delattr","dict","dir","divmod","elif","else","enumerate","eval","except","exec","execfile","file","filter","finally","Flase","float","for","format","from","frozenset","getattr","global","globals","hasattr","hash","help","hex","id","if","import","in","input","int","intern","is","isinstance","issubclass","iter","lambda","len","list","locals","long","map","max","memoryview","min","next","None","not","nt","object","oct","open","or","ord","pass","pow","print","property","raise","range","raw_input","reduce","reload","repr","return","reverse","reversed","round","self","set","setattr","slice","sorted","staticmethod","str","sum","super","try","tuple","type","unichr","unicode","vars","while","with","xrange","yield","zip","False","True","__bases__","__call__","__class__","__enter__","__exit__","__dict__","__import_","__init__","__members__","__methods__","__mro__","__name__","__subclasses__"],equantkeys:["g_params","context","initialize","handle_data","hisover_callback","exit_callback"],equantfuns:["BarCount","Open","Close","High","Low","OpenD","CloseD","HighD","LowD","Vol","OpenInt","BarStatus","CurrentBar","Date","Time","TradeDate","HistoryDataExist","HisData","HisBarsInfo","Q_UpdateTime","Q_AskPrice","Q_AskVol","Q_AvgPrice","Q_BidPrice","Q_BidVol","Q_Close","Q_High","Q_HisHigh","Q_HisLow","Q_Last","Q_LastDate","Q_LastTime","Q_Low","Q_LowLimit","Q_Open","Q_OpenInt","Q_PreOpenInt","Q_PreSettlePrice","Q_PriceChg","Q_PriceChgRadio","Q_TotalVol","Q_TurnOver","Q_UpperLimit","Q_TheoryPrice","Q_Sigma","Q_Delta","Q_Gamma","Q_Vega","Q_Theta","Q_Rho","Q_PreClose","Q_SettlePrice","Q_LastVol","Q_BuyTotalVol","Q_SellTotalVol","QuoteDataExist","CalcTradeDate","Buy","BuyToCover","Sell","SellShort","StartTrade","StopTrade","IsTradeAllowed","BarInterval","BarType","BidAskSize","ContractUnit","ExchangeName","ExchangeTime","ExchangeStatus","CommodityStatus","GetSessionCount","GetSessionStartTime","GetSessionEndTime","TradeSessionBeginTime","TradeSessionEndTime","GetNextTimeInfo","CurrentDate","CurrentTime","TimeDiff","IsInSession","MarginRatio","MaxBarsBack","MaxSingleTradeSize","PriceTick","OptionType","PriceScale","Symbol","SymbolName","SymbolType","GetTrendContract","AvgEntryPrice","BarsSinceEntry","BarsSinceExit","BarsSinceLastEntry","BarsSinceLastBuyEntry","BarsSinceLastSellEntry","BarsSinceToday","ContractProfit","CurrentContracts","BuyPosition","SellPosition","EntryDate","EntryPrice","EntryTime","ExitDate","ExitPrice","ExitTime","LastEntryDate","LastEntryPrice","LastBuyEntryPrice","LastSellEntryPrice","HighestSinceLastBuyEntry","LowestSinceLastBuyEntry","HighestSinceLastSellEntry","LowestSinceLastSellEntry","LastEntryTime","MarketPosition","PositionProfit","BarsLast","StrategyId","Available","CurrentEquity","FloatProfit","GrossLoss","GrossProfit","Margin","NetProfit","NumAllTimes","NumWinTimes","NumLoseTimes","NumEventTimes","PercentProfit","TradeCost","TotalTrades","A_AccountID","A_AllAccountID","A_GetAllPositionSymbol","A_Cost","A_Assets","A_Available","A_Margin","A_ProfitLoss","A_CoverProfit","A_TotalFreeze","A_BuyAvgPrice","A_BuyPosition","A_BuyPositionCanCover","A_BuyProfitLoss","A_SellAvgPrice","A_SellPosition","A_SellPositionCanCover","A_SellProfitLoss","A_TotalAvgPrice","A_TotalPosition","A_TotalProfitLoss","A_TodayBuyPosition","A_TodaySellPosition","A_OrderBuyOrSell","A_OrderEntryOrExit","A_OrderFilledLot","A_OrderFilledPrice","A_OrderLot","A_OrderPrice","A_OrderStatus","A_OrderIsClose","A_OrderTime","A_FirstOrderNo","A_NextOrderNo","A_LastOrderNo","A_FirstQueueOrderNo","A_NextQueueOrderNo","A_AllQueueOrderNo","A_LatestFilledTime","A_AllOrderNo","A_OrderContractNo","A_SendOrder","A_ModifyOrder","A_DeleteOrder","A_GetOrderNo","A_PerProfitLoss","A_PerCoverProfit","A_OrderFilledList","A_PerProfitLoss","A_PerCoverProfit","DeleteAllOrders","SetUserNo","SetBarInterval","SetInitCapital","SetMargin","SetTradeFee","SetActual","SetOrderWay","SetTradeDirection","SetMinTradeQuantity","SetHedge","SetSlippage","SetTriggerType","SetWinPoint","SetStopPoint","SetFloatStopPoint","SubQuote","UnsubQuote","PlotNumeric","PlotIcon","PlotDot","PlotBar","PlotText","PlotVertLine","PlotPartLine","PlotStickLine","UnPlotText","UnPlotIcon","UnPlotDot","UnPlotBar","UnPlotNumeric","UnPlotVertLine","UnPlotPartLine","UnPlotStickLine","SMA","ParabolicSAR","REF","Highest","Lowest","CountIf","CrossOver","CrossUnder","SwingHigh","SwingLow","LogDebug","LogInfo","LogWarn","LogError","Alert","strategyStatus","triggerType","contractNo","kLineType","kLineSlice","tradeDate","dateTimeStamp","triggerData"],equantconsts:["Enum_Buy","Enum_Sell","Enum_Entry","Enum_Exit","Enum_ExitToday","Enum_EntryExitIgnore","Enum_Sended","Enum_Accept","Enum_Triggering","Enum_Active","Enum_Queued","Enum_FillPart","Enum_Filled","Enum_Canceling","Enum_Modifying","Enum_Canceled","Enum_PartCanceled","Enum_Fail","Enum_Suspended","Enum_Apply","Enum_Period_Tick","Enum_Period_Min","Enum_Period_Day","RGB_Red","RGB_Green","RGB_Blue","RGB_Yellow","RGB_Purple","RGB_Gray","RGB_Brown","Enum_Order_Market","Enum_Order_Limit","Enum_Order_MarketStop","Enum_Order_LimitStop","Enum_Order_Execute","Enum_Order_Abandon","Enum_Order_Enquiry","Enum_Order_Offer","Enum_Order_Iceberg","Enum_Order_Ghost","Enum_Order_Swap","Enum_Order_SpreadApply","Enum_Order_HedgApply","Enum_Order_OptionAutoClose","Enum_Order_FutureAutoClose","Enum_Order_MarketOptionKeep","Enum_GFD","Enum_GTC","Enum_GTD","Enum_IOC","Enum_FOK","Enum_Speculate","Enum_Hedge","Enum_Spread","Enum_Market","Enum_Data_Close","Enum_Data_Open","Enum_Data_High","Enum_Data_Low","Enum_Data_Median","Enum_Data_Typical","Enum_Data_Weighted","Enum_Data_Vol","Enum_Data_Opi","Enum_Data_Time"],pykeys:["False","None","True","assert","del","from","global","import","lambda","nonlocal","pass","yield","self","super","async","await"],flowkeys:["class","def","if","elif","else","for","continue","while","break","try","finally","except","raise","with","as","return"],brackets:[{open:"{",close:"}",token:"delimiter.curly"},{open:"[",close:"]",token:"delimiter.bracket"},{open:"(",close:")",token:"delimiter.parenthesis"}],tokenizer:{root:[{include:"@whitespace"},{include:"@numbers"},{include:"@strings"},[/[,:;]/,"delimiter"],[/[{}\[\]()]/,"@brackets"],[/@[_a-zA-Z]\w*/,"tag"],[/[_a-zA-Z]\w*(?=\s*\()/,{cases:{"@pykeys":"pykey","@flowkeys":"flowkey","@keywords":"keyword","@equantkeys":"equantkey","@equantfuns":"equantfun","@equantconsts":"equantconst","@default":"function"}}],[/[_a-zA-Z]\w*/,{cases:{"@pykeys":"pykey","@flowkeys":"flowkey","@keywords":"keyword","@equantkeys":"equantkey","@equantfuns":"equantfun","@equantconsts":"equantconst","@default":"identifier"}}]],whitespace:[[/\s+/,"white"],[/(^#.*$)/,"comment"],[/'''/,"string","@endDocString"],[/"""/,"string","@endDblDocString"]],endDocString:[[/[^']+/,"string"],[/\\'/,"string"],[/'''/,"string","@popall"],[/'/,"string"]],endDblDocString:[[/[^"]+/,"string"],[/\\"/,"string"],[/"""/,"string","@popall"],[/"/,"string"]],numbers:[[/-?0x([abcdef]|[ABCDEF]|\d)+[lL]?/,"number.hex"],[/-?(\d*\.)?\d+([eE][+\-]?\d+)?[jJ]?[lL]?/,"number"]],strings:[[/'$/,"string.escape","@popall"],[/'/,"string.escape","@stringBody"],[/"$/,"string.escape","@popall"],[/"/,"string.escape","@dblStringBody"]],stringBody:[[/[^\\']+$/,"string","@popall"],[/[^\\']+/,"string"],[/\\./,"string"],[/'/,"string.escape","@popall"],[/\\$/,"string"]],dblStringBody:[[/[^\\"]+$/,"string","@popall"],[/[^\\"]+/,"string"],[/\\./,"string"],[/"/,"string.escape","@popall"],[/\\$/,"string"]]}}});
