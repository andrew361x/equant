# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 14:32:43 2019

@author: LT004

获取品种的全部历史合约，和FundamentalsAnalytics 没有关系
2019年11月14日 更新数据时，9月合约已经到期，要选择最新的09合约，然后重新更新

"""

from mytoolbox.lib.wind import WindClient
import os
import time
scriptDir = r'D:\\workspace\\github\\equant'
os.chdir(scriptDir)
StartTime = "2008-01-01"
EndTime = "2020-5-12"

wd = WindClient.client()
from  pandas.io.json import json_normalize
contractList =[
        {"category":"黑色","symbol":"i","main":"I.DCE",
         "leg1":"I2001.DCE","leg2":"I2005.DCE","leg3":"I2009.DCE",
         "indexSymbol":"IFI.WI","spot":"W00014SPT.NM","spotName":"铁矿石现货(青岛港，PB粉矿,61.5%,澳产)"},
        {"category":"黑色","symbol":"rb","main":"RB.SHF",
         "leg1":"RB01M.SHF","leg2":"RB05M.SHF","leg3":"RB09M.SHF",
         "indexSymbol":"RBFI.WI","spot":"W00035SPT.NM","spotName":"螺纹钢现货(上海,HRB400,20MM)"},
        {"category":"黑色","symbol":"hc","main":"HC.SHF",
         "leg1":"HC2001.SHF","leg2":"HC2005.SHF","leg3":"HC2009.SHF",
         "indexSymbol":"HCFI.WI","spot":"W00054SPT.NM","spotName":"热轧卷板现货(上海,Q235B,4.75MM)"},
        {"category":"黑色","symbol":"j","main":"J.DCE",
         "leg1":"J2001.DCE","leg2":"J2005.DCE","leg3":"J2009.DCE",
         "indexSymbol":"JFI.WI","spot":"W00012SPT.NM","spotName":"焦炭现货(唐山,二级,A13.5,S0.7)"},#用唐山二级，是因为这个数据最多最全
        {"category":"黑色","symbol":"jm","main":"JM.DCE",
         "leg1":"JM2001.DCE","leg2":"JM2005.DCE","leg3":"JM2009.DCE",
         "indexSymbol":"JMFI.WI","spot":"W00013SPT.NM","spotName":"焦煤现货(吕梁,主焦,A10.5,V20-24,S1,G75,Y12-15,Mt8)"},
        {"category":"黑色","symbol":"zc","main":"ZC.CZC",
         "leg1":"ZC001.CZC","leg2":"ZC005.CZC","leg3":"ZC009.CZC",
         "indexSymbol":"ZCFI.WI","spot":"W00025SPT.NM","spotName":"动力煤现货(秦皇岛港,动力末煤,Q5500,山西)"},
        {"category":"黑色","symbol":"fg","main":"FG.CZC",
         "leg1":"FG001.CZC","leg2":"FG005.CZC","leg3":"FG009.CZC",
         "indexSymbol":"FGFI.WI","spot":"W00056SPT.NM","spotName":"玻璃现货(沙河安全,5mm)"},

        {"category":"化工","symbol":"pp","main":"PP.DCE",
         "leg1":"PP2001.DCE","leg2":"PP2005.DCE","leg3":"PP2009.DCE",
         "indexSymbol":"PPFI.WI","spot":"W00011SPT.NM","spotName":"聚丙烯现货(T30S,齐鲁石化)"},
        {"category":"化工","symbol":"l","main":"L.DCE",
         "leg1":"L2001.DCE","leg2":"L2005.DCE","leg3":"L2009.DCE",
         "indexSymbol":"LFI.WI","spot":"W00069SPT.NM","spotName":"塑料LLDPE现货(DFDA-7042,吉林石化)"},  
        {"category":"化工","symbol":"ta","main":"TA.CZC",
         "leg1":"TA001.CZC","leg2":"TA005.CZC","leg3":"TA009.CZC",
         "indexSymbol":"TAFI.WI","spot":"W00018SPT.NM","spotName":"PTA现货(华东)"},  
        {"category":"化工","symbol":"ma","main":"MA.CZC",
         "leg1":"MA001.CZC","leg2":"MA005.CZC","leg3":"MA009.CZC",
         "indexSymbol":"MAFI.WI","spot":"W00021SPT.NM","spotName":"甲醇现货(华东)"},  
        {"category":"化工","symbol":"v","main":"V.DCE",
         "leg1":"V2001.DCE","leg2":"V2005.DCE","leg3":"V2009.DCE",
         "indexSymbol":"VFI.WI","spot":"W00010SPT.NM","spotName":"PVC现货(华东,电石法)"}, 
        {"category":"化工","symbol":"ru","main":"RU.SHF",
         "leg1":"RU2001.SHF","leg2":"RU2005.SHF","leg3":"RU2009.SHF",
         "indexSymbol":"RUFI.WI","spot":"W00040SPT.NM","spotName":"橡胶现货(上海,全乳胶SCR5,云南国营)"}, 
        {"category":"化工","symbol":"bu","main":"BU.SHF",
         "leg1":"BU1912.SHF","leg2":"BU2006.SHF","leg3":"BU2106.SHF",
         "indexSymbol":"BUFI.WI","spot":"W00067SPT.NM","spotName":"沥青现货(道路,70#,齐鲁石化)"}, 

        {"category":"农产品","symbol":"m","main":"M.DCE",
         "leg1":"M2001.DCE","leg2":"M2005.DCE","leg3":"M2009.DCE",
         "indexSymbol":"MFI.WI","spot":"W00058SPT.NM","spotName":"豆粕现货(张家港)"}, 
        {"category":"农产品","symbol":"rm","main":"RM.CZC",
         "leg1":"RM001.CZC","leg2":"RM005.CZC","leg3":"RM009.CZC",
         "indexSymbol":"RMFI.WI","spot":"W00065SPT.NM","spotName":"菜粕现货(福建漳州)"}, 
        {"category":"农产品","symbol":"y","main":"Y.DCE",
         "leg1":"Y2001.DCE","leg2":"Y2005.DCE","leg3":"Y2009.DCE",
         "indexSymbol":"YFI.WI","spot":"W00059SPT.NM","spotName":"四级豆油现货(张家港)"},
        {"category":"农产品","symbol":"p","main":"P.DCE",
         "leg1":"P2001.DCE","leg2":"P2005.DCE","leg3":"P2009.DCE",
         "indexSymbol":"PFI.WI","spot":"W00060SPT.NM","spotName":"棕榈油现货(广东,24度)"},
        {"category":"农产品","symbol":"oi","main":"OI.CZC",
         "leg1":"OI001.CZC","leg2":"OI005.CZC","leg3":"OI009.CZC",
         "indexSymbol":"OIFI.WI","spot":"W00064SPT.NM","spotName":"菜油现货(江苏)"},
        {"category":"农产品","symbol":"sr","main":"SR.CZC",
         "leg1":"SR001.CZC","leg2":"SR005.CZC","leg3":"SR009.CZC",
         "indexSymbol":"SRFI.WI","spot":"W00017SPT.NM","spotName":"白糖现货(柳糖)"},
        {"category":"农产品","symbol":"cf","main":"CF.CZC",
         "leg1":"CF001.CZC","leg2":"CF005.CZC","leg3":"CF009.CZC",
         "indexSymbol":"CFFI.WI","spot":"W00063SPT.NM","spotName":"棉花现货(新疆)"},    
        {"category":"农产品","symbol":"ap","main":"AP.CZC",
         "leg1":"AP001.CZC","leg2":"AP005.CZC","leg3":"AP010.CZC",
         "indexSymbol":"APFI.WI","spot":"","spotName":""},      
        {"category":"农产品","symbol":"cs","main":"CS.DCE",
         "leg1":"CS2001.DCE","leg2":"CS2005.DCE","leg3":"CS2009.DCE",
         "indexSymbol":"CSFI.WI","spot":"W00062SPT.NM","spotName":"玉米淀粉现货(长春)"},   
        {"category":"农产品","symbol":"c","main":"C.DCE",
         "leg1":"C2001.DCE","leg2":"C2005.DCE","leg3":"C2009.DCE",
         "indexSymbol":"CFI.WI","spot":"W00061SPT.NM","spotName":"玉米现货(大连平舱价)"},
        {"category":"农产品","symbol":"a","main":"A.DCE",
         "leg1":"A2001.DCE","leg2":"A2005.DCE","leg3":"A2009.DCE",
         "indexSymbol":"AFI.WI","spot":"W00057SPT.NM","spotName":"大豆现货(大连,国产三等)"},
        {"category":"农产品","symbol":"b","main":"B.DCE",
         "leg1":"B2001.DCE","leg2":"B2005.DCE","leg3":"B2009.DCE",
         "indexSymbol":"BFI.WI","spot":"W00002SPT.NM","spotName":"大豆现货"},
        {"category":"农产品","symbol":"jd","main":"JD.DCE",
         "leg1":"JD2001.DCE","leg2":"JD2005.DCE","leg3":"JD2009.DCE",
         "indexSymbol":"JDFI.WI","spot":"W00066SPT.NM","spotName":"鸡蛋现货(山东青岛)"},
        ]
contractList =contractList[1] #rb
cfg=json_normalize(contractList)
  
srcDir = scriptDir#+'\\files'
if not os.path.exists(srcDir):
    os.makedirs(srcDir)
os.chdir(srcDir)

for i,data in cfg.iterrows():
    print('*'*50)
    print(data.category,data.symbol)
    if not os.path.exists(srcDir+'\\'+data.symbol.upper()):
        os.makedirs(srcDir+'\\'+data.symbol.upper())
    os.chdir(srcDir+'\\'+data.symbol.upper())
    
    # 现货价格
    if data.spot:
        spotdata = wd.getDayData(data.spot, fields='close', startTime=StartTime, endTime=EndTime)
        time.sleep(3)
        spotdata.to_csv(data.symbol.upper()+"_spotprice.csv")
        print(data.symbol.upper()+"_spotprice.csv")
#srcDir = scriptDir+'\\equant\\files'
os.chdir(srcDir)

