@echo off
echo ========================================
echo LANGUAGE EDITING PIPELINE - Tasks 4.2-4.3
echo ========================================
echo.
echo This batch file runs the complete language editing pipeline
echo for Tasks 4.2-4.3: Manual Language Editing
echo.
echo Based on: IMPLEMENTATION_ROADMAP.md lines 535-551
echo Date: 2026-01-28
echo.

REM Check if virtual environment exists
if not exist "venv_311\Scripts\activate.bat" (
    echo ERROR: Virtual environment 'venv_311' not found!
    echo Please run setup_env_311.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv_311\Scripts\activate.bat

echo.
echo ========================================
echo STEP 1: Create Common Errors Catalog
echo ========================================
echo.
python scripts/create_errors_catalog.py --output outputs/language_editing/Common_Errors_Catalog.xlsx

echo.
echo ========================================
echo STEP 2: Integrate with Task 4.1 Results
echo ========================================
echo.
if exist "outputs\language_check" (
    echo Found Task 4.1 results, integrating...
    python scripts/integrate_task4_1.py --run-all
) else (
    echo No Task 4.1 results found, skipping integration...
    echo (Task 4.1 outputs expected in: outputs\language_check\)
)

echo.
echo ========================================
echo STEP 3: Generate Edited Manuscript Files
echo ========================================
echo.
echo Options:
echo 1. Batch mode (automatic, recommended for first pass)
echo 2. Interactive mode (step-by-step with user confirmation)
echo 3. Sample mode (process only Abstract section for testing)
echo.
set /p mode="Select mode (1, 2, or 3): "

if "%mode%"=="1" (
    echo Running in BATCH mode...
    python scripts/generate_edited_manuscript.py --batch --output-dir outputs/language_editing
) else if "%mode%"=="2" (
    echo Running in INTERACTIVE mode...
    python scripts/generate_edited_manuscript.py --interactive --output-dir outputs/language_editing
) else if "%mode%"=="3" (
    echo Running in SAMPLE mode (Abstract only)...
    python scripts/generate_edited_manuscript.py --sample --output-dir outputs/language_editing
) else (
    echo Invalid selection. Using BATCH mode by default.
    python scripts/generate_edited_manuscript.py --batch --output-dir outputs/language_editing
)

echo.
echo ========================================
echo STEP 4: Generate Language Quality Report
echo ========================================
echo.
python scripts/generate_quality_report.py --output-dir outputs/language_editing

echo.
echo ========================================
echo STEP 5: Launch Interactive Editor (Optional)
echo ========================================
echo.
set /p launch_editor="Launch interactive editor for additional edits? (y/n): "

if /i "%launch_editor%"=="y" (
    echo Launching interactive editor...
    python scripts/interactive_language_editor.py
) else (
    echo Skipping interactive editor.
)

echo.
echo ========================================
echo COMPLETION SUMMARY
echo ========================================
echo.
echo Language editing pipeline complete!
echo.
echo Generated files in: outputs\language_editing\
echo.
echo Key files created:
echo 1. Common_Errors_Catalog.xlsx - Catalog of typical errors
echo 2. [section]_edited.md - Edited manuscript sections
echo 3. [section]_changes.csv - Change logs for each section
echo 4. Editing_Change_Log.xlsx - Master change log
echo 5. Language_Quality_Report.md - Quality assessment
echo 6. Editing_Statistics.xlsx - Editing statistics
echo.
echo Next steps:
echo 1. Review edited files in outputs\language_editing\
echo 2. Check Language_Quality_Report.md for quality assessment
echo 3. Proceed to Task 4.4 (Bibliography Formatting)
echo.
echo ========================================
pause