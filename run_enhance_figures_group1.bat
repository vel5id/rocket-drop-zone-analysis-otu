@echo off
REM Batch file for Task 3.3: Enhance Specific Figures (Group 1)
REM Использует виртуальное окружение venv_311
REM Запускает скрипт scripts/enhance_figures_group1.py

echo ========================================
echo TASK 3.3: ENHANCE SPECIFIC FIGURES (GROUP 1)
echo ========================================
echo Date: %date% %time%
echo.

REM Проверка существования виртуального окружения
if not exist "venv_311\Scripts\python.exe" (
    echo ERROR: Virtual environment venv_311 not found!
    echo Please create it using: setup_env_311.bat
    pause
    exit /b 1
)

REM Проверка существования скрипта
if not exist "scripts\enhance_figures_group1.py" (
    echo ERROR: Script scripts\enhance_figures_group1.py not found!
    pause
    exit /b 1
)

REM Активация виртуального окружения и запуск скрипта
echo Activating virtual environment venv_311...
call venv_311\Scripts\activate.bat

echo Running enhancement script...
echo.

REM Запуск Python скрипта
python scripts\enhance_figures_group1.py

REM Проверка кода возврата
if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: All figures enhanced successfully!
    echo ========================================
    echo.
    echo Generated files in outputs\figures\:
    dir outputs\figures\Figure_*_Enhanced.png /b
    echo.
    echo Report: outputs\figures\Task_3.3_Enhancement_Report.txt
) else (
    echo.
    echo ========================================
    echo ERROR: Script failed with code %errorlevel%
    echo ========================================
)

REM Пауза для просмотра результатов
pause