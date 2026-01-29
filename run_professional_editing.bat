@echo off
echo ========================================
echo Professional Editing Service - Task 4.5
echo MDPI Language Service Integration
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv_311\Scripts\activate.bat" (
    echo Error: Python 3.11 virtual environment not found.
    echo Please run setup_env_311.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv_311\Scripts\activate.bat

:menu
cls
echo ========================================
echo PROFESSIONAL EDITING SERVICE MENU
echo ========================================
echo.
echo 1. Create directory structure and samples
echo 2. Prepare files for MDPI submission
echo 3. Create submission package
echo 4. Track submission status
echo 5. Process editor feedback
echo 6. Integrate editor changes
echo 7. Create change summary
echo 8. Run all steps (demo)
echo 9. Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto step1
if "%choice%"=="2" goto step2
if "%choice%"=="3" goto step3
if "%choice%"=="4" goto step4
if "%choice%"=="5" goto step5
if "%choice%"=="6" goto step6
if "%choice%"=="7" goto step7
if "%choice%"=="8" goto step8
if "%choice%"=="9" goto end
echo Invalid choice. Please try again.
pause
goto menu

:step1
echo.
echo Step 1: Creating directory structure and sample files...
python scripts/create_professional_editing_structure.py
echo.
echo Step 1 complete. Sample structure created in outputs/professional_editing/
pause
goto menu

:step2
echo.
echo Step 2: Preparing files for MDPI submission...
echo Note: This requires manuscript files in outputs/manuscript_sections/
if not exist "outputs\manuscript_sections\*.md" (
    echo Warning: No manuscript files found. Creating samples first...
    python scripts/create_professional_editing_structure.py
)
python scripts/professional_editing_service.py --prepare --files outputs/manuscript_sections/*.md
echo.
echo Step 2 complete. Check preparation_report.json for results.
pause
goto menu

:step3
echo.
echo Step 3: Creating submission package for MDPI...
python scripts/professional_editing_service.py --create-package --files outputs/manuscript_sections/*.md
echo.
echo Step 3 complete. Submission package created.
echo File: outputs/professional_editing/Submission_Package.zip
pause
goto menu

:step4
echo.
echo Step 4: Tracking submission status...
python scripts/professional_editing_service.py --track-status
echo.
echo Step 4 complete. Check submission_status.json for details.
pause
goto menu

:step5
echo.
echo Step 5: Processing editor feedback...
echo Note: This requires an editor feedback file.
echo Creating sample feedback template first...
python scripts/create_feedback_template.py
echo.
echo Sample feedback created. To process real feedback:
echo python scripts/professional_editing_service.py --process-feedback "feedback_file.xlsx"
pause
goto menu

:step6
echo.
echo Step 6: Integrating editor changes...
echo Note: This requires original and edited files.
echo Example usage:
echo python scripts/professional_editing_service.py --integrate-changes original.docx edited.docx
echo.
echo For demo, creating sample integration report...
python scripts/create_professional_editing_structure.py
echo.
echo Step 6 demo complete. Check integration_report.json.
pause
goto menu

:step7
echo.
echo Step 7: Creating change summary...
echo Creating sample change summary from demo data...
python scripts/create_professional_editing_structure.py
echo.
echo Step 7 complete. Check change_summary.json.
pause
goto menu

:step8
echo.
echo Step 8: Running all steps (demo mode)...
echo This will create a complete demonstration of the workflow.
echo.

echo 8.1 Creating directory structure...
python scripts/create_professional_editing_structure.py

echo 8.2 Creating feedback template...
python scripts/create_feedback_template.py

echo 8.3 Running preparation demo...
python scripts/professional_editing_service.py --prepare --files outputs/manuscript_sections/*.md

echo 8.4 Creating submission package demo...
python scripts/professional_editing_service.py --create-package --files outputs/manuscript_sections/*.md

echo 8.5 Tracking status demo...
python scripts/professional_editing_service.py --track-status

echo.
echo ========================================
echo DEMO COMPLETE
echo ========================================
echo.
echo Files created in outputs/professional_editing/:
echo - preparation_report.json
echo - submission_status.json
echo - processed_feedback.json
echo - integration_report.json
echo - change_summary.json
echo - Editing_Service_Log.xlsx
echo.
echo Templates created:
echo - Editor_Feedback_Template.xlsx
echo - MDPI_Service_Guide.md
echo - Change_Integration_Checklist.md
echo.
pause
goto menu

:end
echo.
echo Professional Editing Service completed.
echo.
echo Generated files and documentation:
echo 1. scripts/professional_editing_service.py - Main service script
echo 2. MDPI_Service_Guide.md - User guide
echo 3. Editor_Feedback_Template.xlsx - Feedback template
echo 4. Change_Integration_Checklist.md - Integration checklist
echo 5. outputs/professional_editing/ - All output files
echo.
echo Next steps:
echo 1. Review MDPI_Service_Guide.md for instructions
echo 2. Prepare your manuscript files
echo 3. Use the batch menu or run scripts directly
echo 4. Submit to MDPI language service
echo.
pause
exit /b 0