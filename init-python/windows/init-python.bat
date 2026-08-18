@echo off
chcp 65001 >nul
powershell -ExecutionPolicy Bypass -File "%~dp0init-python.ps1" %*
pause
