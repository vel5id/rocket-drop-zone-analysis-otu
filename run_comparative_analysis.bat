@echo off
REM Batch file for running Task 5.3: Comparative Cost Analysis
REM Uses virtual environment venv_311

echo ========================================
echo TASK 5.3: COMPARATIVE COST ANALYSIS
echo ========================================

REM Check if virtual environment exists
if not exist "venv_311\Scripts\activate.bat" (
    echo Virtual environment venv_311 not found.
    echo Please create it using: python -m venv venv_311
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment venv_311...
call venv_311\Scripts\activate.bat

REM Check Python version
python --version

REM Install required packages if needed
echo Checking/installing required packages...
pip install numpy pandas matplotlib seaborn openpyxl --quiet

REM Run the comparative analysis script
echo.
echo Running comparative cost analysis...
python scripts/comparative_cost_analysis.py

REM Check if script completed successfully
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ANALYSIS COMPLETED SUCCESSFULLY
    echo ========================================
    echo Output files created in: outputs/economic/comparative/
    echo 1. Comparative_Cost_Analysis.xlsx
    echo 2. Cost_Comparison_Charts.png
    echo 3. Comparative_Analysis_Report.md
) else (
    echo.
    echo ========================================
    echo ANALYSIS FAILED
    echo ========================================
    echo Check the error messages above.
)

REM Deactivate virtual environment
call venv_311\Scripts\deactivate.bat

echo.
echo Press any key to exit...
pause > nul