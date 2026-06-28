@echo off
REM Double-click installer for C.H.R.I.S. on Windows.
REM
REM This just runs the PowerShell setup script (setup.ps1) with execution policy
REM bypassed, so you don't have to open PowerShell yourself. It installs uv,
REM Python 3.12, the virtualenv and all dependencies into the venv.
REM
REM Usage: double-click this file, or run `setup.bat` from a terminal.

REM %~dp0 is the folder this .bat lives in, so it finds setup.ps1 next to it.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"

echo.
echo Done. You can close this window.
pause
