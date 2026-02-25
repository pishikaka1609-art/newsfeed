param(
  [string]$GitPath = "C:\Program Files\Git\cmd",
  [string]$PyPath = "C:\Users\Ryan\AppData\Local\Programs\Python\Python311",
  [string]$PyScripts = "C:\Users\Ryan\AppData\Local\Programs\Python\Python311\Scripts"
)

$env:Path = "$GitPath;$PyPath;$PyScripts;$env:Path"

Write-Host "Session PATH bootstrapped."
Write-Host "git -> $(git --version)"
Write-Host "python -> $(python --version)"

