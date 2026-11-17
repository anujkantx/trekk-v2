@echo off
title Trekking Management Application - Environment Setup
cd /d "%~dp0"

echo =====================================================================
echo    TREKKING MANAGEMENT APPLICATION (TMA) - ONE-TIME SETUP
echo =====================================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    echo Please install Python 3.11+ and add it to PATH.
    pause
    exit /b 1
)

where npm >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] npm / Node.js is not installed or not in system PATH.
    echo Please install Node.js (v18+) and npm.
    pause
    exit /b 1
)

echo [1/4] Setting up Python virtual environment...
if not exist "backend\.venv" (
    python -m venv "backend\.venv"
    echo       Virtual environment created at backend\.venv
) else (
    echo       Virtual environment already exists at backend\.venv
)

echo [2/4] Installing backend dependencies...
call "backend\.venv\Scripts\activate.bat"
"backend\.venv\Scripts\python.exe" -m pip install --upgrade pip >nul 2>nul
"backend\.venv\Scripts\pip.exe" install -r "backend\requirements.txt"

echo [3/4] Initializing database and seed data...
if not exist "backend\instance\exports" mkdir "backend\instance\exports"
if not exist "backend\instance\reports" mkdir "backend\instance\reports"
"backend\.venv\Scripts\python.exe" -m backend.init_db

echo [4/4] Installing frontend dependencies...
cd /d "%~dp0frontend"
call npm install
cd /d "%~dp0"

echo.
echo =====================================================================
echo    SETUP COMPLETE! YOU ARE READY TO RUN THE APPLICATION.
echo =====================================================================
echo.
echo Start the application using 4 terminal windows:
echo   1. backend.bat        (Flask REST API - Port 5001)
echo   2. celery_worker.bat  (Celery Async Tasks)
echo   3. celery_beat.bat    (Periodic Scheduler)
echo   4. frontend.bat       (Vue 3 App - Port 5173)
echo.
pause
