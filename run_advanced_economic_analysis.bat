@echo off
echo ========================================
echo Advanced Economic Analysis - Tasks 5.4-5.5
echo ========================================
echo.
echo This batch file runs the advanced economic analysis for rocket drop zone assessment.
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python 3.8+ and try again.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if exist venv_311 (
    echo Activating virtual environment venv_311...
    call venv_311\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment venv_311 not found.
    echo Running with system Python...
)

REM Create output directory
if not exist outputs\economic\advanced (
    mkdir outputs\economic\advanced
    echo Created output directory: outputs\economic\advanced
)

REM Run the advanced economic analysis
echo.
echo Running advanced economic analysis...
echo ========================================
python scripts/run_advanced_economic_analysis_complete.py

if errorlevel 1 (
    echo.
    echo ERROR: Analysis script failed.
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ANALYSIS COMPLETED SUCCESSFULLY
echo ========================================
echo.
echo Output files created in outputs\economic\advanced\:
echo.
echo   1. Advanced_Economic_Analysis.xlsx    - Comprehensive analysis in Excel
echo   2. Sensitivity_Analysis_Report.md     - Sensitivity analysis report
echo   3. Risk_Assessment_Report.md          - Risk assessment report  
echo   4. Cost_Benefit_Analysis.md           - Cost-benefit analysis report
echo   5. Economic_Scenario_Visualizations.png - Scenario visualizations
echo.
echo Summary of Tasks 5.4-5.5 completed:
echo   - Sensitivity analysis of economic parameters
echo   - What-if scenarios for different rocket types
echo   - Long-term forecasts with inflation
echo   - Risk assessment with probability distributions
echo   - Cost-benefit analysis
echo.
pause