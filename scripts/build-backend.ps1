# PyInstaller 打包 Python backend
$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path "$PSScriptRoot/.."
$backendDir = Join-Path $repoRoot "backend"
$electronResources = Join-Path $repoRoot "electron/resources/backend"

Write-Host "Building Python backend with PyInstaller..."
Push-Location $backendDir
try {
    pip install pyinstaller

    pyinstaller --onefile --name devtool-backend --console --clean `
        --add-data "$repoRoot/main/src;src" `
        --hidden-import src.core.env --hidden-import src.core.tools `
        --hidden-import src.core.packages --hidden-import src.core.executor `
        --hidden-import src.core.commands --hidden-import src.core.commands.definitions `
        --hidden-import src.core.commands.probes --hidden-import src.core.commands.glossary `
        --hidden-import src.utils.python_finder `
        server.py

    New-Item -ItemType Directory -Path $electronResources -Force | Out-Null
    Copy-Item "dist/devtool-backend.exe" $electronResources -Force
    Write-Host "Backend built and copied to $electronResources"
} finally {
    Pop-Location
}
