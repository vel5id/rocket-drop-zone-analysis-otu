@echo off
REM run_language_check.bat - Запуск автоматической проверки языка для Task 4.1
REM Ссылка на спецификацию: IMPLEMENTATION_ROADMAP.md строки 478-532

echo ============================================
echo Запуск автоматической проверки языка
echo Task 4.1: Automated Language Check
echo ============================================

REM Проверка наличия виртуального окружения
if not exist "venv_311\Scripts\activate.bat" (
    echo ОШИБКА: Виртуальное окружение venv_311 не найдено!
    echo Установите его с помощью: install_languagetool.bat
    pause
    exit /b 1
)

REM Активация виртуального окружения
call venv_311\Scripts\activate.bat

REM Проверка установки language-tool-python
python -c "import language_tool_python" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: language-tool-python не установлен!
    echo Установите его с помощью: install_languagetool.bat
    pause
    exit /b 1
)

REM Создание выходной директории
if not exist "outputs\language_check" mkdir "outputs\language_check"

echo Запуск скрипта automated_language_check.py...
python scripts/automated_language_check.py

if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Скрипт завершился с ошибкой!
    pause
    exit /b 1
)

echo ============================================
echo Проверка завершена успешно!
echo Сгенерированные файлы:
echo   - outputs\language_check\Grammar_Errors_Report.xlsx
echo   - outputs\language_check\Article_Usage_Issues.xlsx
echo   - outputs\language_check\Subject_Verb_Agreement_Issues.xlsx
echo   - outputs\language_check\Language_Check_Summary.md
echo   - outputs\language_check\language_check.log
echo ============================================

REM Открытие папки с результатами
if exist "outputs\language_check" (
    echo Открытие папки с результатами...
    start "" "outputs\language_check"
)

pause