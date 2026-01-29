@echo off
echo Запуск всех скриптов анализа чувствительности...
echo.

echo 1. Запуск OAT анализа...
venv_311\Scripts\python.exe scripts/sensitivity_analysis_oat.py
if %errorlevel% neq 0 (
    echo Ошибка при выполнении OAT анализа
    pause
    exit /b 1
)

echo.
echo 2. Запуск Monte Carlo анализа...
venv_311\Scripts\python.exe scripts/sensitivity_analysis_monte_carlo_complete.py
if %errorlevel% neq 0 (
    echo Ошибка при выполнении Monte Carlo анализа
    pause
    exit /b 1
)

echo.
echo 3. Запуск Sobol анализа...
venv_311\Scripts\python.exe scripts/sensitivity_analysis_sobol_complete.py
if %errorlevel% neq 0 (
    echo Ошибка при выполнении Sobol анализа
    pause
    exit /b 1
)

echo.
echo Все скрипты выполнены успешно!
echo Результаты сохранены в outputs/sensitivity_analysis/
pause