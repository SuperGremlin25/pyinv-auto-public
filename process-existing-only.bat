@echo off
REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
REM Remove trailing backslash
set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

echo ========================================
echo PyInv-Auto - Process Existing Files
echo ========================================
echo.
echo Processing all existing invoices...
echo Watch folder: %SCRIPT_DIR%\invoices
echo Output: %SCRIPT_DIR%\invoices_parsed.csv
echo.

cd /d "%SCRIPT_DIR%"
python pyinv_auto.py --process-only

echo.
echo Done! Press any key to close...
pause > nul
