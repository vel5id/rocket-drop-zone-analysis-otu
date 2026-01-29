@echo off
echo Creating Common Errors Catalog for Tasks 4.2-4.3...
echo.

REM Activate virtual environment
call venv_311\Scripts\activate.bat

REM Run the script
python scripts/create_errors_catalog.py --output outputs/language_editing/Common_Errors_Catalog.xlsx

echo.
echo Common Errors Catalog created successfully!
echo Location: outputs/language_editing/Common_Errors_Catalog.xlsx
echo.
pause