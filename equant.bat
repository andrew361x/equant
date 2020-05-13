@echo off

set eqtpath="%MYWORKSPACEHOME%\github\equant\src\equant-script.py"

set pypath="C:\Anaconda3\python.exe"
if not exist %pypath% (
	set pypath="python.exe"
)

C:\Anaconda3\Scripts\activate.bat C:\Anaconda3 && %pypath% %eqtpath%
TIMEOUT /T 10