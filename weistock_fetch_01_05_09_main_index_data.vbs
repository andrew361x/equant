Sub GetHistoryData()
	Set myGrid = Technic.GetGridByName("Main")
	Set myHistory = myGrid.GetHistoryData()
	dim filename
	filename=myGrid.StockLabel & "_" & myGrid.CycType+1 & ".csv"  
	set fso=createobject("scripting.filesystemobject")
	set ftxt=fso.createtextfile(%MYWORKSPACEHOME% & "\"&filename,8)
	ftxt.write "datetime,open,high,low,close,volume" & vbcrlf   
		 for j= 0 to myHistory.Count-1
			  ftxt.write myHistory.Date(j) &  "," & myHistory.Open(j)  &  "," &  myHistory.High(j)  &  "," &  myHistory.Low(j)  &  "," &  myHistory.Close(j)  &  "," &  myHistory.VOLUME(j) & vbcrlf   
			 next
	 ftxt.close
End Sub