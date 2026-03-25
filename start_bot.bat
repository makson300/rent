@echo off
echo Launching RentBot Marketplace Services...

taskkill /F /IM python.exe >nul 2>&1

echo [1/2] Starting Web Dashboard on http://localhost:8080...
start "RentBot Dashboard" cmd /k ".\venv\Scripts\python.exe web/dashboard.py"

echo [2/2] Starting Telegram Bot...
.\venv\Scripts\python.exe main.py

pause
