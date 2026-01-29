@echo off
echo Running quick economic damage test...
echo.

REM Check if virtual environment exists
if exist "venv_311\Scripts\python.exe" (
    echo Using virtual environment venv_311...
    venv_311\Scripts\python.exe test_economic_quick.py
) else (
    echo Virtual environment not found, using system Python...
    python test_economic_quick.py
)

echo.
echo Test complete.
pause