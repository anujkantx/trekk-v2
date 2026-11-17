@echo off
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
    echo Virtual environment not found
    pause
    exit /b 1
)

echo Starting Celery Worker (Pool: solo) ...
call "backend\.venv\Scripts\activate.bat"
"backend\.venv\Scripts\python.exe" -m celery -A backend.celery_app.celery_app worker --loglevel=info --pool=solo

pause
