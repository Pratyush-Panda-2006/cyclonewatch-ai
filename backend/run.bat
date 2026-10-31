@echo off
cd /d "%~dp0"
call .venv\Scripts\activate.bat
echo Starting ReliefSense / CycloneWatch AI Backend on http://localhost:8000 ...
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause
