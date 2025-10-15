# PyInv-Auto Windows Scheduler Setup Script
# This script sets up a scheduled task to run PyInv-Auto on user login

param(
    [string]$ScriptPath = "",
    [string]$PythonPath = "python",
    [switch]$Help
)

# Display help
if ($Help) {
    Write-Host @"
PyInv-Auto Windows Scheduler Setup Script
==========================================

This script creates a Windows scheduled task that runs PyInv-Auto 
automatically when you log in to Windows.

Usage:
    .\setup_scheduler.ps1 [options]

Options:
    -ScriptPath <path>  : Full path to pyinv_auto.py (default: current directory)
    -PythonPath <path>  : Path to Python executable (default: 'python')
    -Help               : Show this help message

Examples:
    # Use defaults (current directory, system Python)
    .\setup_scheduler.ps1

    # Specify custom paths
    .\setup_scheduler.ps1 -ScriptPath "C:\MyScripts\pyinv_auto.py" -PythonPath "C:\Python39\python.exe"

"@
    exit
}

Write-Host "=" -ForegroundColor Cyan
Write-Host "PyInv-Auto Scheduled Task Setup" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Determine script path
if ($ScriptPath -eq "") {
    $ScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "pyinv_auto.py"
}

# Check if Python script exists
if (-not (Test-Path $ScriptPath)) {
    Write-Host "ERROR: Python script not found at: $ScriptPath" -ForegroundColor Red
    Write-Host "Please specify the correct path using -ScriptPath parameter" -ForegroundColor Yellow
    exit 1
}

Write-Host "Python script: $ScriptPath" -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = & $PythonPath --version 2>&1
    Write-Host "Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found at: $PythonPath" -ForegroundColor Red
    Write-Host "Please install Python or specify the correct path using -PythonPath parameter" -ForegroundColor Yellow
    exit 1
}

# Check for required packages
Write-Host "`nChecking required Python packages..." -ForegroundColor Cyan
$requirementsFile = Join-Path -Path $PSScriptRoot -ChildPath "requirements.txt"

if (Test-Path $requirementsFile) {
    Write-Host "Installing/verifying requirements..." -ForegroundColor Yellow
    & $PythonPath -m pip install -q -r $requirementsFile
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ All requirements installed" -ForegroundColor Green
    } else {
        Write-Host "⚠ Warning: Some requirements may not have installed correctly" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Warning: requirements.txt not found. Make sure dependencies are installed." -ForegroundColor Yellow
}

# Task details
$TaskName = "PyInv-Auto-Invoice-Processor"
$TaskDescription = "Automatically watches folders and processes invoice PDFs to CSV on user login"
$WorkingDirectory = Split-Path -Parent $ScriptPath

Write-Host "`nCreating scheduled task..." -ForegroundColor Cyan
Write-Host "Task Name: $TaskName" -ForegroundColor Gray
Write-Host "Working Directory: $WorkingDirectory" -ForegroundColor Gray

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "`n⚠ Task '$TaskName' already exists." -ForegroundColor Yellow
    $response = Read-Host "Do you want to replace it? (Y/N)"
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Host "Setup cancelled." -ForegroundColor Yellow
        exit 0
    }
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Existing task removed." -ForegroundColor Yellow
}

# Create the action
$Action = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$ScriptPath`" --process-only" `
    -WorkingDirectory $WorkingDirectory

# Create the trigger (at logon)
$Trigger = New-ScheduledTaskTrigger -AtLogOn

# Create additional settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

# Get current user
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType Interactive `
    -RunLevel Limited

# Register the scheduled task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description $TaskDescription `
        -Force | Out-Null
    
    Write-Host "`n✓ Scheduled task created successfully!" -ForegroundColor Green
    Write-Host "`nTask Details:" -ForegroundColor Cyan
    Write-Host "  Name: $TaskName" -ForegroundColor White
    Write-Host "  Trigger: At user logon" -ForegroundColor White
    Write-Host "  Action: Process existing invoices only" -ForegroundColor White
    Write-Host "  Status: Ready" -ForegroundColor White
    
    Write-Host "`nThe task will run automatically on your next login." -ForegroundColor Green
    Write-Host "To manage this task, use Task Scheduler (taskschd.msc)" -ForegroundColor Yellow
    
    # Offer to test the task
    Write-Host "`n" -NoNewline
    $testResponse = Read-Host "Would you like to test the task now? (Y/N)"
    if ($testResponse -eq "Y" -or $testResponse -eq "y") {
        Write-Host "`nRunning task..." -ForegroundColor Cyan
        Start-ScheduledTask -TaskName $TaskName
        Write-Host "✓ Task started. Check Task Scheduler for results." -ForegroundColor Green
    }
    
} catch {
    Write-Host "`n✗ ERROR: Failed to create scheduled task" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host "`nSetup complete!" -ForegroundColor Green
