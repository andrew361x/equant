@echo off

set eqtpath="%MYWORKSPACEHOME%\equant\src\equant-script.py"

set pypath="C:\ProgramData\Anaconda3\python.exe"
if not exist %pypath% (
	set pypath="python.exe"
)

C:\ProgramData\Anaconda3\Scripts\activate.bat C:\ProgramData\Anaconda3 && %pypath% %eqtpath%
TIMEOUT /T 10