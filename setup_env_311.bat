@echo off
REM ============================================================
REM Setup script for Python 3.11 (Required for Numba/GDAL)
REM Uses venv_311 to avoid file lock issues with old venv
REM ============================================================

echo.
echo ============================================================
echo CHECKING FOR PYTHON 3.11
echo ============================================================

REM Try to find Python 3.11 launcher
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3.11 not found!
    echo.
    echo The scientific libraries Numba, GDAL, Rasterio DO NOT support 
    echo Python 3.14 yet. You must install Python 3.11.
    echo.
    echo Please download and install Python 3.11 from:
    echo https://www.python.org/downloads/release/python-3119/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    echo Done.
    exit /b 1
)

echo [OK] Python 3.11 found.

echo.
echo ============================================================
echo CREATING VIRTUAL ENVIRONMENT (venv_311)
echo ============================================================

if exist venv_311 (
    echo [!] Deleting old venv_311...
    rmdir /s /q venv_311
)

echo [1/4] Creating venv_311 with Python 3.11...
py -3.11 -m venv venv_311
if errorlevel 1 (
    echo [ERROR] Failed to create venv_311
    echo Done.
    exit /b 1
)

REM Activate
call venv_311\Scripts\activate.bat

echo [2/4] Upgrading pip...
python -m pip install --upgrade pip

echo [3/4] Installing dependencies...
echo.
echo NOTE: Attempting to install full requirements (including Numba)...
pip install -r requirements.txt

echo.
echo ============================================================
echo SETUP COMPLETE
echo ============================================================
echo.
echo Now you can run the server with full acceleration:
echo     venv_311\Scripts\activate
echo     python run_server.py
echo.
echo Done.
