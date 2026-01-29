@echo off
echo Creating Editor Feedback Template for MDPI Language Service...
echo Task 4.5: Professional Editing Service
echo.

REM Activate Python 3.11 virtual environment
call venv_311\Scripts\activate.bat

REM Run the template creation script
python scripts/create_feedback_template.py

echo.
echo Template creation complete.
echo Files created:
echo 1. Editor_Feedback_Template.xlsx (main template)
echo 2. outputs/professional_editing/Editor_Feedback_Sample.xlsx (sample)
echo.
pause