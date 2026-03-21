@echo off
title API Server
cd /d "%~dp0..\"
if exist .venv (
    call .venv\Scripts\activate
)
python run_api.py
pause
