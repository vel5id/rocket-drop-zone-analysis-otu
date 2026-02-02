@echo off
echo ============================================
echo   Rocket OTU - Full Stack Launcher
echo ============================================
echo.

REM Check if backend is already running
netstat -ano | findstr :8000 > nul
if %errorlevel% == 0 (
    echo [WARNING] Backend already running on port 8000
    echo.
) else (
    echo [1/2] Starting Backend Server...
    start "OTU Backend" cmd /k "py run_server.py"
    timeout /t 3 /nobreak > nul
)

REM Check if frontend is already running
netstat -ano | findstr :5173 > nul
if %errorlevel% == 0 (
    echo [WARNING] Frontend already running on port 5173
    echo.
) else (
    echo [2/2] Starting Frontend...
    start "OTU Frontend" cmd /k "run_frontend.bat"
    timeout /t 3 /nobreak > nul
)

echo.
echo ============================================
echo   Services Started!
echo ============================================
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:5173
echo ============================================
echo.
echo Press any key to open browser...
pause > nul

start http://localhost:5173

echo.
echo To stop services, close the terminal windows
echo or press Ctrl+C in each window
