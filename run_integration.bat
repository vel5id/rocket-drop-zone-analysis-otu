@echo off
echo Запуск интеграции результатов анализа чувствительности...
echo.

venv_311\Scripts\python.exe scripts/create_sensitivity_integration.py
if %errorlevel% neq 0 (
    echo Ошибка при выполнении интеграции
    pause
    exit /b 1
)

echo.
echo Интеграция выполнена успешно!
echo Проверьте результаты в outputs/sensitivity_analysis/ и outputs/supplementary_tables/
pause