@echo off
echo Запуск Task 2.7: Validation Section in Manuscript
echo ================================================
echo.

REM Проверка существования виртуального окружения
if not exist "venv_311\Scripts\python.exe" (
    echo ОШИБКА: Виртуальное окружение venv_311 не найдено!
    echo Создайте виртуальное окружение с помощью setup_env_311.bat
    pause
    exit /b 1
)

REM Проверка существования скрипта
if not exist "scripts\validation_section_manuscript.py" (
    echo ОШИБКА: Скрипт validation_section_manuscript.py не найден!
    pause
    exit /b 1
)

echo Запуск скрипта validation_section_manuscript.py...
echo.

REM Запуск скрипта через виртуальное окружение
venv_311\Scripts\python.exe scripts\validation_section_manuscript.py

echo.
echo ================================================
echo Завершено выполнение Task 2.7
echo Проверьте результаты в outputs/validation_framework/
echo.
pause