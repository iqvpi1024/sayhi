@echo off
setlocal
set "BUNDLE_ROOT=%~dp0.."
set "SETTINGS_FILE=%LOCALAPPDATA%\NoetideSyntheticPreview\data_dir.txt"
if not exist "%SETTINGS_FILE%" (
  powershell -ExecutionPolicy Bypass -File "%BUNDLE_ROOT%\scripts\setup-synthetic-preview.ps1"
  if errorlevel 1 exit /b %errorlevel%
)
set /p DATA_DIRECTORY=<"%SETTINGS_FILE%"
"%BUNDLE_ROOT%\runtime\python.exe" -m noetide_micro --data-dir "%DATA_DIRECTORY%" %*
endlocal
