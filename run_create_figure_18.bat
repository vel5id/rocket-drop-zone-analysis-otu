@echo off
REM Batch file for Task 3.6: Final Map - Figure 18
REM Created based on IMPLEMENTATION_ROADMAP.md lines 351-398
REM Uses virtual environment venv_311

echo ========================================
echo Task 3.6: Creating Figure 18 Final Map
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
call venv_311\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo Virtual environment activated.
echo.

REM Check if script exists
if not exist "scripts\create_figure_18_final.py" (
    echo ERROR: Script scripts\create_figure_18_final.py not found.
    pause
    exit /b 1
)

echo Running create_figure_18_final.py...
echo.

REM Run the script
python scripts\create_figure_18_final.py
if errorlevel 1 (
    echo ERROR: Script execution failed.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Figure 18 creation completed successfully!
echo ========================================
echo.
echo Output files created:
echo   - outputs\figures\Figure_18_Recommended_OTUs_Final.png (300 DPI)
echo   - outputs\figures\Figure_18_Recommended_OTUs_Final.svg (vector)
echo   - outputs\figures\Figure_18_Creation_Report.txt
echo.
echo Quality checks performed:
echo   - DPI: 300 (publication standard)
echo   - Colorblind-friendly palette: viridis
echo   - North arrow: top-right
echo   - Scale bar: 10 km, bottom-left
echo   - Legend font size: ≥10pt
echo   - Hatching patterns: applied for accessibility
echo.
echo Task 3.6 completed according to IMPLEMENTATION_ROADMAP.md spec.
pause