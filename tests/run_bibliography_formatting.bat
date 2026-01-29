@echo off
echo ========================================
echo Bibliography Formatting Script
echo Task 4.4 from IMPLEMENTATION_ROADMAP.md
echo ========================================
echo.

REM Check if virtual environment exists
if exist "venv_311\Scripts\activate.bat" (
    echo Activating virtual environment venv_311...
    call venv_311\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo Warning: Virtual environment venv_311 not found.
    echo Using system Python. Ensure required packages are installed.
)

REM Install required packages if needed
echo.
echo Checking/installing required packages...
pip install bibtexparser pandas openpyxl requests --quiet
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install required packages.
    echo Please install manually: pip install bibtexparser pandas openpyxl requests
    pause
    exit /b 1
)

REM Check if input file exists
if not exist "data\bibliography\test_references.bib" (
    echo Input file not found: data\bibliography\test_references.bib
    echo Creating sample bibliography file...
    mkdir data\bibliography 2>nul
    echo @article{sample, > data\bibliography\test_references.bib
    echo   author = {Sample Author}, >> data\bibliography\test_references.bib
    echo   title = {Sample Title}, >> data\bibliography\test_references.bib
    echo   journal = {Sample Journal}, >> data\bibliography\test_references.bib
    echo   year = {2023}, >> data\bibliography\test_references.bib
    echo   doi = {10.1234/sample.2023.123456} >> data\bibliography\test_references.bib
    echo } >> data\bibliography\test_references.bib
    echo Created sample bibliography file.
)

REM Create output directory
mkdir outputs\bibliography 2>nul

REM Run the bibliography formatting script
echo.
echo Running bibliography formatting script...
echo This may take a moment as it fetches metadata from Crossref API...
echo.
python scripts/format_bibliography.py --input "data\bibliography\test_references.bib"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Bibliography formatting completed successfully!
    echo.
    echo Generated files in outputs\bibliography\:
    echo   - formatted_references.bib
    echo   - Missing_Metadata_Report.xlsx
    echo   - DOI_Validation_Report.txt
    echo   - Bibliography_Formatting_Summary.md
    echo   - bibliography_formatting.log
    echo.
    echo To use a different .bib file, run:
    echo   python scripts/format_bibliography.py --input "path\to\your\file.bib"
    echo ========================================
) else (
    echo.
    echo ========================================
    echo Bibliography formatting failed!
    echo Check the log file: outputs\bibliography\bibliography_formatting.log
    echo ========================================
)

echo.
pause