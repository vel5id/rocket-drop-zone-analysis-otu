@echo off
echo Running Bibliography Formatting Test...
echo.

REM Activate virtual environment if exists
if exist "venv_311\Scripts\activate.bat" (
    call venv_311\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Virtual environment not found, using system Python.
)

REM Install required packages if needed
echo Installing required packages...
pip install bibtexparser pandas openpyxl requests --quiet

REM Run test script
echo.
echo Running bibliography formatting test...
python scripts/test_bibliography_formatting.py

echo.
echo Test completed. Check outputs/bibliography/ for generated files.
pause