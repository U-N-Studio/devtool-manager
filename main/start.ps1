$ErrorActionPreference = "Stop"
$scriptDir = $PSScriptRoot
$requirements = Join-Path $scriptDir "requirements.txt"

$ctk = pip show customtkinter 2>$null
if (-not $ctk) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r $requirements
}

python (Join-Path $scriptDir "main.py")
