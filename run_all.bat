@echo off
echo [1/3] Killing existing Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] Starting Web Dashboard (Port 8000)...
start /B .\venv\Scripts\python.exe web/dashboard.py

echo [3/3] Starting Telegram Bot...
.\venv\Scripts\python.exe main.py

pause
