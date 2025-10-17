# Check if PyInv-Auto scheduled task exists and is configured correctly

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "PyInv-Auto Scheduled Task Diagnostic" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check for the task
$taskName = "PyInv-Auto-Invoice-Processor"
$task = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($null -eq $task) {
    Write-Host "✗ Task NOT found: $taskName" -ForegroundColor Red
    Write-Host ""
    Write-Host "The scheduled task has not been created yet." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To create it, run:" -ForegroundColor Cyan
    Write-Host "  .\setup-scheduler-admin.bat" -ForegroundColor White
    Write-Host ""
    Write-Host "Or manually run:" -ForegroundColor Cyan
    Write-Host "  .\setup_scheduler.ps1" -ForegroundColor White
    exit 1
}

Write-Host "✓ Task found: $taskName" -ForegroundColor Green
Write-Host ""

# Get task details
$taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
$taskDetails = $task | Get-ScheduledTask

Write-Host "Task Status:" -ForegroundColor Cyan
Write-Host "  State: $($task.State)" -ForegroundColor $(if ($task.State -eq "Ready") { "Green" } else { "Yellow" })
Write-Host "  Last Run Time: $($taskInfo.LastRunTime)" -ForegroundColor White
Write-Host "  Last Result: $($taskInfo.LastTaskResult)" -ForegroundColor $(if ($taskInfo.LastTaskResult -eq 0) { "Green" } else { "Red" })
Write-Host "  Next Run Time: $($taskInfo.NextRunTime)" -ForegroundColor White
Write-Host ""

# Check triggers
Write-Host "Triggers:" -ForegroundColor Cyan
foreach ($trigger in $task.Triggers) {
    Write-Host "  Type: $($trigger.CimClass.CimClassName)" -ForegroundColor White
    if ($trigger.CimClass.CimClassName -eq "MSFT_TaskLogonTrigger") {
        Write-Host "  ✓ Configured to run at logon" -ForegroundColor Green
    }
}
Write-Host ""

# Check actions
Write-Host "Actions:" -ForegroundColor Cyan
foreach ($action in $task.Actions) {
    Write-Host "  Execute: $($action.Execute)" -ForegroundColor White
    Write-Host "  Arguments: $($action.Arguments)" -ForegroundColor White
    Write-Host "  Working Directory: $($action.WorkingDirectory)" -ForegroundColor White
}
Write-Host ""

# Check if Python exists
$pythonPath = $task.Actions[0].Execute
Write-Host "Python Check:" -ForegroundColor Cyan
try {
    $pythonVersion = & $pythonPath --version 2>&1
    Write-Host "  ✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python NOT found at: $pythonPath" -ForegroundColor Red
    Write-Host "  This is likely why the task fails!" -ForegroundColor Yellow
}
Write-Host ""

# Check if script exists
$scriptPath = ($task.Actions[0].Arguments -split '"')[1]
Write-Host "Script Check:" -ForegroundColor Cyan
if (Test-Path $scriptPath) {
    Write-Host "  ✓ Script found: $scriptPath" -ForegroundColor Green
} else {
    Write-Host "  ✗ Script NOT found: $scriptPath" -ForegroundColor Red
    Write-Host "  This is likely why the task fails!" -ForegroundColor Yellow
}
Write-Host ""

# Recommendations
Write-Host "Recommendations:" -ForegroundColor Cyan
if ($task.State -ne "Ready") {
    Write-Host "  • Enable the task in Task Scheduler" -ForegroundColor Yellow
}
if ($taskInfo.LastTaskResult -ne 0 -and $taskInfo.LastTaskResult -ne $null) {
    Write-Host "  • Task failed on last run (code: $($taskInfo.LastTaskResult))" -ForegroundColor Yellow
    Write-Host "  • Check Event Viewer for details" -ForegroundColor Yellow
}
Write-Host "  • Test the task manually:" -ForegroundColor Cyan
Write-Host "    Start-ScheduledTask -TaskName '$taskName'" -ForegroundColor White
Write-Host ""

# Offer to test now
$testResponse = Read-Host "Would you like to test the task now? (Y/N)"
if ($testResponse -eq "Y" -or $testResponse -eq "y") {
    Write-Host "`nRunning task..." -ForegroundColor Cyan
    Start-ScheduledTask -TaskName $taskName
    Start-Sleep -Seconds 2
    $newInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "Last Result: $($newInfo.LastTaskResult)" -ForegroundColor $(if ($newInfo.LastTaskResult -eq 0) { "Green" } else { "Red" })
    if ($newInfo.LastTaskResult -eq 0) {
        Write-Host "✓ Task ran successfully!" -ForegroundColor Green
    } else {
        Write-Host "✗ Task failed. Check Event Viewer or logs." -ForegroundColor Red
    }
}
