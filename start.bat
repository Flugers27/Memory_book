@echo off
echo Starting Memory Book API Gateway System...
echo.

REM Создаем папку для логов если её нет
if not exist "logs" mkdir logs

echo Step 1: Starting Auth Service...
start cmd /k "cd services/Auth && python run.py"
timeout /t 3 /nobreak >nul

echo Step 2: Starting Memory Service...
start cmd /k "cd services/Memory && python run.py"
timeout /t 3 /nobreak >nul

echo Step 3: Starting API Gateway...
timeout /t 2 /nobreak >nul
cd gateway && python run.py

echo.
echo All services started!
echo.
echo Services:
echo - Auth:      http://localhost:8001
echo - Memory:    http://localhost:8002
echo - Gateway:   http://localhost:8000
echo.
echo Press any key to stop all services...
pause >nul

REM Останавливаем все сервисы
taskkill /F /IM python.exe >nul 2>&1
echo All services stopped.