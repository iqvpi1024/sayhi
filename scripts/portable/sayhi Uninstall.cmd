@echo off
setlocal
set "STAGED=%TEMP%\noetide-uninstall-%RANDOM%.ps1"
copy /y "%~dp0uninstall-noetide.ps1" "%STAGED%" >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%STAGED%" -InstallRoot "%~dp0.." %*
set "RC=%errorlevel%"
del /q "%STAGED%" >nul 2>&1
if not "%RC%"=="0" pause
exit /b %RC%
