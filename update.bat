@echo off

set curdir="%~dp0"
set pypath="%~dp0../Miniconda/"


if not exist %pypath% (
	set pypath=
)

::cmd /k %pypath%python.exe %curdir%update.py %1
cmd /k %pypath%python.exe "%~dp0\update.py"
pause
                