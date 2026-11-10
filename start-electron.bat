@echo off
chcp 65001 >nul
title DevTool Manager
echo Starting DevTool Manager...
echo.

:: Start frontend dev server in background
echo Starting frontend dev server...
start "Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

:: Wait for frontend to be ready
timeout /t 3 /nobreak >nul

:: Start electron
echo Starting Electron...
cd /d "%~dp0electron"
npm start
