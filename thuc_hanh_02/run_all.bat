@echo off
title Starting API and Frontend
setlocal

echo Starting Backend API...
start "API Server" cmd /k "call utils\run_api.bat"

echo Starting Frontend Dev Server...
start "Frontend Server" cmd /k "call utils\run_frontend.bat"

echo.
echo Both services are starting in separate windows.
echo API: http://localhost:3005
echo Frontend: http://localhost:3000
timeout /t 5
