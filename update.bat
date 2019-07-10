@echo off
set curdir=%~dp0

set pypath=%curdir%../Miniconda3/


if not exist %pypath% (
	set pypath=
)

cmd /k %pypath%python.exe %curdir%update.py
pause
