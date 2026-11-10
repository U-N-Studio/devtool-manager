@echo off
chcp 65001 >nul
title DevTool Manager
setlocal enabledelayedexpansion

echo ========================================
echo   DevTool Manager
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

:: 启动前端开发服务器
echo [1/2] Starting frontend dev server...
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

:: 启动 Electron（设置 NODE_ENV=development 以加载 dev server）
echo [2/2] Starting Electron...
cd /d "%~dp0electron"
set NODE_ENV=development
npm start
