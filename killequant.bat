@echo off


set /p user_option=Are you sure to close all python.exe?(y/n):


if %user_option%==y  taskkill /f /fi "IMAGENAME eq python.exe"

if %user_option% neq y  exit

echo Success
pause