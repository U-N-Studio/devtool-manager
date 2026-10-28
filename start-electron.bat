@echo off
chcp 65001 >nul
title DevTool Manager (Electron)
cd /d "%~dp0electron"
echo Starting DevTool Manager...
npm run dev:electron
pause
