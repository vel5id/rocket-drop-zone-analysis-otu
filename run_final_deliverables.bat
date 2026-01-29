@echo off
REM ============================================
REM Final Deliverables Creation Batch Script
REM Rocket Drop Zone Analysis Project
REM ============================================

echo.
echo ============================================
echo FINAL DELIVERABLES CREATION SCRIPT
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Activate virtual environment if exists
if exist "venv_311\Scripts\activate.bat" (
    echo Activating virtual environment venv_311...
    call venv_311\Scripts\activate.bat
) else (
    echo Virtual environment venv_311 not found.
    echo Using system Python installation.
)

REM Install required packages if needed
echo Checking required packages...
python -c "import pandas, openpyxl" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages (pandas, openpyxl)...
    pip install pandas openpyxl --quiet
) else (
    echo Required packages are already installed.
)

REM Run the final deliverables script
echo.
echo Running final deliverables creation script...
echo ============================================
python scripts/create_final_deliverables.py

REM Check if script succeeded
if errorlevel 1 (
    echo.
    echo ERROR: Script execution failed.
    echo Check the log file in final_deliverables/deliverables_creation.log
    pause
    exit /b 1
)

echo.
echo ============================================
echo FINAL DELIVERABLES CREATED SUCCESSFULLY
echo ============================================
echo.
echo Output files are located in: final_deliverables/
echo.
echo Summary of created files:
echo   - Final_Manuscript.md/.tex
echo   - Figure_Catalog.xlsx
echo   - Table_Catalog.xlsx
echo   - Supplementary_Materials_Final.zip
echo   - Supplementary_README.md
echo   - File_Manifest.csv
echo   - Final_Deliverables_Report.md
echo.
echo For detailed report, see: final_deliverables/Final_Deliverables_Report.md
echo.

REM Open the final deliverables directory
echo Opening final deliverables directory...
if exist "final_deliverables" (
    explorer "final_deliverables"
)

pause