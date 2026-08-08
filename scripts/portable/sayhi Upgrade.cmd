@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0upgrade-noetide.ps1" %*
if errorlevel 1 pause
