@echo off
echo ========================================
echo FINAL EXECUTION: TASK 5.3 COMPARATIVE ANALYSIS
echo ========================================

REM Activate virtual environment if exists
if exist "venv_311\Scripts\activate.bat" (
    call venv_311\Scripts\activate.bat
    echo Using virtual environment venv_311
)

REM Run the execution script
python execute_comparative.py

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: All output files generated
    echo ========================================
    
    REM List generated files
    echo.
    echo Generated files in outputs/economic/comparative/:
    if exist "outputs\economic\comparative\Comparative_Cost_Analysis.xlsx" (
        echo   ✓ Comparative_Cost_Analysis.xlsx
    )
    if exist "outputs\economic\comparative\Cost_Comparison_Charts.png" (
        echo   ✓ Cost_Comparison_Charts.png
    )
    if exist "outputs\economic\comparative\Comparative_Analysis_Report.md" (
        echo   ✓ Comparative_Analysis_Report.md
    )
) else (
    echo.
    echo ========================================
    echo ERROR: Analysis failed
    echo ========================================
)

REM Deactivate virtual environment if was activated
if exist "venv_311\Scripts\deactivate.bat" (
    call venv_311\Scripts\deactivate.bat
)

echo.
echo Press any key to exit...
pause > nul