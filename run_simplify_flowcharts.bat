@echo off
REM ============================================================
REM Task 3.5: Simplify Flowcharts - Batch Execution Script
REM ============================================================
REM Executes simplify_flowcharts.py using Python 3.11 virtual environment
REM Created: 2026-01-28
REM ============================================================

echo.
echo ============================================================
echo TASK 3.5: SIMPLIFY FLOWCHARTS
echo ============================================================
echo.

REM Check if virtual environment exists
if not exist "venv_311\Scripts\python.exe" (
    echo [ERROR] Python virtual environment not found.
    echo Please run setup_env_311.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating Python 3.11 virtual environment...
call venv_311\Scripts\activate.bat

REM Check Python version
echo [INFO] Checking Python version...
venv_311\Scripts\python.exe --version

REM Run the simplification script
echo.
echo [INFO] Running simplify_flowcharts.py...
echo ============================================================
venv_311\Scripts\python.exe scripts/simplify_flowcharts.py

REM Check exit code
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo SUCCESS: Task 3.5 completed successfully!
    echo ============================================================
    echo.
    echo Generated files:
    echo   - outputs/figures/Figure_4_IAS_Architecture_Simplified.svg
    echo   - outputs/figures/Figure_4_IAS_Architecture_Simplified.png (300 DPI)
    echo   - outputs/figures/Figure_5_IAS_Detailed_Simplified.svg
    echo   - outputs/figures/Figure_5_IAS_Detailed_Simplified.png (300 DPI)
    echo   - outputs/manuscript_sections/Figure_Captions.md
    echo   - outputs/Task_3.5_Simplify_Flowcharts_Report.md
    echo.
    echo Check the logs directory for detailed execution logs.
) else (
    echo.
    echo ============================================================
    echo ERROR: Task 3.5 failed with exit code %errorlevel%
    echo ============================================================
    echo Check the error messages above and logs/simplify_flowcharts.log
)

REM Deactivate virtual environment (optional)
call venv_311\Scripts\deactivate.bat

echo.
echo ============================================================
echo Batch execution completed.
echo ============================================================
echo.
pause