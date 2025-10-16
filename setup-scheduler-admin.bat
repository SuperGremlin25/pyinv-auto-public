@echo off
REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

echo ========================================
echo PyInv-Auto - Task Scheduler Setup
echo ========================================
echo.
echo This will create a scheduled task that runs
echo PyInv-Auto automatically when you log in.
echo.
echo Script directory: %SCRIPT_DIR%
echo.
pause

powershell -Command "Start-Process powershell -ArgumentList '-ExecutionPolicy Bypass -File ""%SCRIPT_DIR%\setup_scheduler.ps1""' -Verb RunAs"
