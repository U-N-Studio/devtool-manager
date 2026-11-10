@echo off
chcp 65001 >nul
title DevTool Manager - Development
setlocal enabledelayedexpansion

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
echo [1/3] Checking dependencies...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install --silent
)
cd /d "%~dp0electron"
if not exist "node_modules" (
    echo Installing electron dependencies...
    call npm install --silent
)
cd /d "%~dp0"

:: 生成类型
echo [2/3] Generating types from protocol...
node scripts/generate-types.mjs

:: 启动前端开发服务器
echo [3/3] Starting frontend dev server...
cd /d "%~dp0frontend"
start "DevTool-Frontend" cmd /k "npm run dev"

:: 等待前端就绪（检查端口 5173）
echo Waiting for frontend to be ready...
set /a retries=0
:wait_loop
timeout /t 1 /nobreak >nul
netstat -ano | findstr ":5173" | findstr "LISTENING" >nul 2>nul
if !ERRORLEVEL! EQU 0 goto :frontend_ready
set /a retries+=1
if !retries! GEQ 30 (
    echo [ERROR] Frontend failed to start within 30 seconds
    pause
    exit /b 1
)
echo   Still waiting... ^(!retries!/30^)
goto :wait_loop

:frontend_ready
echo   Frontend ready at http://localhost:5173

:: 启动 Electron
echo Starting Electron...
cd /d "%~dp0electron"
start "DevTool-Electron" cmd /k "npm run dev:electron"

echo.
echo ========================================
echo   Development servers started!
echo   Frontend: http://localhost:5173
echo   Close both "DevTool-*" windows to stop
echo ========================================
echo.
pause
