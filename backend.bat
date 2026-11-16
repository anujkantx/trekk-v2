@echo off
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found at backend\.venv
    pause
    exit /b 1
)

echo Activating virtual environment and starting Trekking Backend...
call "backend\.venv\Scripts\activate.bat"
"backend\.venv\Scripts\python.exe" -m backend.app

pause
