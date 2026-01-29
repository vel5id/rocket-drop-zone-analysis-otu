@echo off
echo Запуск реализации фреймворка валидации...
echo.

venv_311\Scripts\python.exe scripts/validation_framework_implementation.py
if %errorlevel% neq 0 (
    echo Ошибка при выполнении фреймворка валидации
    pause
    exit /b 1
)

echo.
echo Фреймворк валидации выполнен успешно!
echo Проверьте результаты в outputs/validation_framework/ и outputs/figures/
pause