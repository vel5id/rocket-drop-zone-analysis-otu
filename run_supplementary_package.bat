@echo off
REM ============================================================================
REM Task 3.9: Supplementary Materials Package
REM Based on IMPLEMENTATION_ROADMAP.md (lines 401-474)
REM ============================================================================
echo.
echo ============================================================================
echo Supplementary Materials Package Creator
echo Task 3.9 from IMPLEMENTATION_ROADMAP.md
echo ============================================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.11 or later.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv_311\Scripts\activate.bat" (
    echo [WARNING] Virtual environment 'venv_311' not found.
    echo Creating virtual environment...
    python -m venv venv_311
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv_311\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

REM Check and install required packages
echo Checking required packages...
python -c "import pandas, numpy, openpyxl, pillow, zipfile" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERROR] Failed to install required packages.
        pause
        exit /b 1
    )
    echo Packages installed successfully.
)

REM Create necessary directories
echo Creating output directories...
if not exist "outputs" mkdir outputs
if not exist "outputs\supplementary_materials" mkdir outputs\supplementary_materials
if not exist "outputs\supplementary_materials\tables" mkdir outputs\supplementary_materials\tables
if not exist "outputs\supplementary_materials\figures" mkdir outputs\supplementary_materials\figures
if not exist "outputs\supplementary_materials\data" mkdir outputs\supplementary_materials\data
if not exist "logs" mkdir logs

REM Run the supplementary materials package script
echo.
echo ============================================================================
echo Running Supplementary Materials Package Creator...
echo ============================================================================
echo.

python scripts/supplementary_materials_package.py
if errorlevel 1 (
    echo.
    echo [ERROR] Supplementary materials package creation failed.
    echo Check logs/supplementary_materials_package.log for details.
    pause
    exit /b 1
)

REM Check if ZIP archive was created
if exist "outputs\Supplementary_Materials.zip" (
    echo.
    echo ============================================================================
    echo SUCCESS: Supplementary materials package created!
    echo ============================================================================
    echo.
    echo Output files:
    echo   - outputs\Supplementary_Materials.zip
    echo   - outputs\supplementary_materials\README.md
    echo   - outputs\supplementary_materials\File_Manifest.xlsx
    echo   - outputs\supplementary_materials\completion_report.json
    echo.
    
    REM Show file sizes
    for %%F in ("outputs\Supplementary_Materials.zip") do (
        for /f "tokens=3" %%S in ('dir "%%F" ^| find "%%F"') do (
            echo ZIP archive size: %%S
        )
    )
    
    echo.
    echo You can find the complete supplementary materials in:
    echo   outputs\supplementary_materials\
    echo.
    echo To distribute the materials, share the ZIP file:
    echo   outputs\Supplementary_Materials.zip
    echo.
) else (
    echo [WARNING] ZIP archive not created, but script completed.
)

REM Deactivate virtual environment
call venv_311\Scripts\deactivate.bat

echo.
echo ============================================================================
echo Task 3.9: Supplementary Materials Package - COMPLETED
echo ============================================================================
echo.
pause