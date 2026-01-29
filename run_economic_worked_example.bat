@echo off
REM Batch file for running Task 5.2: Worked Example for OTU
REM Uses virtual environment venv_311 as specified in IMPLEMENTATION_ROADMAP.md
REM Author: Rocket Drop Zone Analysis Team
REM Date: 2026-01-28

echo ========================================
echo Rocket Drop Zone Analysis - Task 5.2
echo Economic Worked Example for OTU
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv_311\Scripts\activate.bat" (
    echo ERROR: Virtual environment venv_311 not found.
    echo Please run setup_env_311.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment venv_311...
call venv_311\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Check Python version
echo Checking Python version...
python --version

REM Create necessary directories
echo Creating output directories...
if not exist "outputs\economic" mkdir "outputs\economic"
if not exist "logs" mkdir "logs"

REM Run the worked example script
echo.
echo ========================================
echo Running Economic Worked Example Script
echo ========================================
echo.

python scripts/create_economic_worked_example.py

REM Check if script succeeded
if errorlevel 1 (
    echo.
    echo ERROR: Script execution failed.
    echo Check logs\economic_worked_example.log for details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo TASK 5.2 COMPLETED SUCCESSFULLY
echo ========================================
echo.
echo Generated files:
echo   - outputs\economic\OTU_245_Worked_Example.xlsx
echo   - outputs\economic\OTU_245_Cost_Distribution_Pie.png
echo   - outputs\economic\OTU_245_Cost_Comparison_Bar.png
echo   - outputs\economic\OTU_245_Scenario_Description.md
echo   - outputs\economic\Economic_Worked_Example.md
echo.
echo Log file: logs\economic_worked_example.log
echo.

REM Open the output directory
echo Opening output directory...
if exist "outputs\economic" start "" "outputs\economic"

pause