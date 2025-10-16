@echo off
REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

echo ========================================
echo PyInv-Auto Invoice Processor
echo ========================================
echo.
echo Starting invoice processor...
echo Watch folder: %SCRIPT_DIR%\invoices
echo Output: %SCRIPT_DIR%\invoices_parsed.csv
echo.

cd /d "%SCRIPT_DIR%"
python pyinv_auto.py

echo.
echo Press any key to close...
pause > nul
