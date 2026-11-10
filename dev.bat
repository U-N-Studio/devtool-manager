@echo off
chcp 65001 >nul
title DevTool Manager - Development
echo ========================================
echo   DevTool Manager Development Mode
echo ========================================
echo.

:: 检查 Node.js
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js not found. Please install Node.js first.
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)

:: 检查依赖
echo [1/4] Checking dependencies...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)
cd /d "%~dp0electron"
if not exist "node_modules" (
    echo Installing electron dependencies...
    call npm install
)
cd /d "%~dp0"

:: 生成类型
echo [2/4] Generating types from protocol...
node scripts/generate-types.mjs

:: 启动后端监控
echo [3/4] Starting backend file watcher...
cd /d "%~dp0backend"
start "Backend Watcher" cmd /k "echo Watching backend changes... && npx nodemon --watch implementations/python --exec \"echo Backend changed, restart manually\""
cd /d "%~dp0"

:: 启动前端开发服务器
echo [4/4] Starting development servers...
cd /d "%~dp0frontend"
start "Frontend Dev" cmd /k "npm run dev"

:: 等待前端就绪
echo Waiting for frontend...
timeout /t 2 /nobreak >nul

:: 启动 Electron
cd /d "%~dp0electron"
start "Electron" cmd /k "npm run dev:electron"

echo.
echo ========================================
echo   Development servers started!
echo   Frontend: http://localhost:5173
echo   Press Ctrl+C in each window to stop
echo ========================================
echo.
