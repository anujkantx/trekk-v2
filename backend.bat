@echo off
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
    echo Virtual environment not found at backend\.venv
    pause
    exit /b 1
)

if not exist "backend\instance\exports" mkdir "backend\instance\exports"
if not exist "backend\instance\reports" mkdir "backend\instance\reports"

where docker >nul 2>nul
if %ERRORLEVEL% equ 0 (
    docker compose up -d >nul 2>nul
)

if not exist "backend\instance\trekking.db" (
    echo Initializing database...
    "backend\.venv\Scripts\python.exe" -m backend.init_db
)

echo Starting Flask backend on http://localhost:5001 ...
call "backend\.venv\Scripts\activate.bat"
"backend\.venv\Scripts\python.exe" -m backend.app

pause
