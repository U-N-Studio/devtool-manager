param(
    [string]$PythonVersion = "3.12"
)

$projectRoot = Split-Path $PSScriptRoot -Parent
$venvDir = Join-Path $projectRoot "venv"

Write-Host "===== Python Environment Init =====" -ForegroundColor Cyan

$pyCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    try {
        $ver = & $cmd --version 2>&1 | Out-String
        if ($ver -match "Python") {
            $pyCmd = $cmd
            Write-Host ("Found: {0}" -f $ver.Trim()) -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pyCmd) {
    Write-Host "Python not found. Installing via winget..." -ForegroundColor Yellow
    winget install Python.Python.$PythonVersion --accept-package-agreements --accept-source-agreements
    $pyCmd = "python"
}

Write-Host "`nPython is ready." -ForegroundColor Green

Write-Host "`n===== Done =====" -ForegroundColor Green
