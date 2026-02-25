param(
  [string]$ProjectPath = "C:\Users\Ryan\VC\NEWSFEED"
)

$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ProjectPath\scripts\run_local.ps1`""
$trigger = @(
  (New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Monday -At 8:30am),
  (New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Thursday -At 8:30am)
)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Limited

Register-ScheduledTask -TaskName "NewsfeedDigest" -Action $action -Trigger $trigger -Principal $principal -Description "NEWSFEED digest schedule"

