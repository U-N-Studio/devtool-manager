$ErrorActionPreference = "Stop"
$projectRoot = Split-Path $PSScriptRoot -Parent
$mainDir = Join-Path $projectRoot "main"
$outputDir = Join-Path $projectRoot "output"
$distDir = Join-Path $outputDir "dist"

if (-not (Test-Path -LiteralPath $outputDir)) { New-Item -ItemType Directory -Path $outputDir -Force | Out-Null }

Write-Host "===== Build DevTool Manager =====" -ForegroundColor Cyan

$pyInstaller = Get-Command pyinstaller -ErrorAction SilentlyContinue
if (-not $pyInstaller) {
    Write-Host "PyInstaller not found, installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

Write-Host "Building exe..." -ForegroundColor Cyan
pyinstaller --onefile --windowed --name "DevToolManager" --distpath $distDir --workpath (Join-Path $outputDir "build") --specpath $outputDir (Join-Path $mainDir "main.py")

if (Test-Path (Join-Path $distDir "DevToolManager.exe")) {
    Write-Host "`nBuild success!" -ForegroundColor Green
    Write-Host "Output: $(Join-Path $distDir 'DevToolManager.exe')" -ForegroundColor Green
} else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
}
