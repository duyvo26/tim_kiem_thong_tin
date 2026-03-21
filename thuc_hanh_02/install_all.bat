@echo off
title Install All Dependencies
setlocal

echo ==========================================
echo [1/2] Installing Backend Dependencies...
echo ==========================================
call utils\install_api.bat

echo.
echo ==========================================
echo [2/2] Installing Frontend Dependencies...
echo ==========================================
call utils\install_frontend.bat

echo.
echo ==========================================
echo Installation complete! You can now run run_all.bat
echo ==========================================
pause
