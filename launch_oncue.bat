@echo off
cd /d "%~dp0"
echo Starting OnCUE... > launch_oncue.log
"C:\Users\samr1\AppData\Local\Programs\Python\Python313\python.exe" -m oncue >> launch_oncue.log 2>&1
echo Exit code: %ERRORLEVEL% >> launch_oncue.log
