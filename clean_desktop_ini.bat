@echo off
echo Dang xoa tat ca cac tep desktop.ini trong thu muc nay va cac thu muc con...

:: Xoa cac tep desktop.ini (bao gom ca tep an va tep he thong)
del /s /q /f /a:h desktop.ini 2>nul
del /s /q /f /a:s desktop.ini 2>nul
del /s /q /f desktop.ini 2>nul

echo.
echo Da hoan tat! Vui long thu thuc hien lai lenh git pull.
pause
