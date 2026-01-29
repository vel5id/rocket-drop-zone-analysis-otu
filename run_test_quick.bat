@echo off
echo Running quick test of Task 5.2 components...
echo.

REM Activate virtual environment if available
if exist "venv_311\Scripts\activate.bat" (
    call venv_311\Scripts\activate.bat
)

REM Run the test script
python test_run_worked_example.py

pause