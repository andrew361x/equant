'从2020年1月1日，成交量数据按照单边计算，之前的数据金字塔已经除以2了。   --2020/05/13

Sub GetHistoryData()
	Set myGrid = Technic.GetGridByName("Main")
	Set myHistory = myGrid.GetHistoryData()
	dim filename
	filename=myGrid.StockLabel & "_" & myGrid.CycType+1 & ".csv"  
	set fso=createobject("scripting.filesystemobject")
	set ftxt=fso.createtextfile("D:\jztfiles\" & filename,8)
	ftxt.write "datetime,open,high,low,close,volume,amount,openint" & vbcrlf   
		 for j= 0 to myHistory.Count-1
			  ftxt.write myHistory.Date(j) &  "," & myHistory.Open(j)  &  "," &  myHistory.High(j)  &  "," &  myHistory.Low(j)  &  "," &  myHistory.Close(j)  &  "," &  myHistory.Volume(j) &"," &  myHistory.Amount(j)&"," &  myHistory.Openint(j) & vbcrlf   
			 next
	 ftxt.close
End Sub