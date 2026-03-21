@echo off
cd /d "%~dp0..\"
if not exist .venv (
    echo [API] Creating virtual environment...
    python -m venv .venv
)
echo [API] Activating virtual environment and installing requirements...
call .venv\Scripts\activate && pip install -r requirements.txt
