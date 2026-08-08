@echo off
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup-noetide.ps1"
if errorlevel 1 pause
