@echo off
REM install_languagetool.bat - Установка LanguageTool для Task 4.1 Automated Language Check
REM Ссылка на спецификацию: IMPLEMENTATION_ROADMAP.md строки 478-532

echo ============================================
echo Установка LanguageTool для автоматической проверки языка
echo Task 4.1: Automated Language Check
echo ============================================

REM Проверка наличия виртуального окружения
if not exist "venv_311\Scripts\activate.bat" (
    echo ОШИБКА: Виртуальное окружение venv_311 не найдено!
    echo Создайте его с помощью: python -m venv venv_311
    pause
    exit /b 1
)

REM Активация виртуального окружения
call venv_311\Scripts\activate.bat

echo Установка language-tool-python...
pip install language-tool-python

echo Установка дополнительных зависимостей для отчетов...
pip install pandas openpyxl

echo Проверка установки...
python -c "import language_tool_python; print('LanguageTool импортирован успешно')"

if %ERRORLEVEL% NEQ 0 (
    echo ОШИБКА: Не удалось импортировать language_tool_python
    pause
    exit /b 1
)

echo ============================================
echo Установка завершена успешно!
echo Для запуска проверки используйте: run_language_check.bat
echo ============================================
pause