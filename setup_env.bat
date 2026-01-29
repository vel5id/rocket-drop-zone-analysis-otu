@echo off
REM ============================================================
REM Setup script for Rocket Drop Zone Analysis
REM Creates virtual environment and installs UI dependencies
REM ============================================================

echo.
echo ============================================================
echo CREATING VIRTUAL ENVIRONMENT
echo ============================================================

REM Check if venv exists
if exist venv (
    echo [!] Virtual environment already exists. Using existing one...
) else (
    echo [1/4] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate venv
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo [4/4] Installing dependencies from requirements_ui.txt...
pip install -r requirements_ui.txt

echo.
echo ============================================================
echo INSTALLATION COMPLETE
echo ============================================================
echo.
echo To activate the environment, run:
echo     venv\Scripts\activate
echo.
echo To run the server:
echo     python run_server.py
echo.
pause
