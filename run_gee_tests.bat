@echo off
REM Batch file for running GEE integration tests
REM Usage: run_gee_tests.bat [test_type]
REM   test_type: all, imports, auth, mock, gee, pipeline (default: all)

setlocal

set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

echo ============================================================
echo GEE Integration Test Runner
echo ============================================================
echo Test Type: %TEST_TYPE%
echo.

REM Check if venv_311 exists
if not exist "venv_311\Scripts\python.exe" (
    echo [ERROR] Virtual environment venv_311 not found!
    echo Please run setup_env_311.bat first.
    exit /b 1
)

REM Run tests
echo Running tests...
echo.
venv_311\Scripts\python.exe test_gee_integration.py --test %TEST_TYPE%

set EXIT_CODE=%ERRORLEVEL%

echo.
echo ============================================================
if %EXIT_CODE%==0 (
    echo [SUCCESS] All tests passed!
) else (
    echo [FAILURE] Some tests failed. Check output above.
)
echo ============================================================
echo.
echo Test report saved to: output\test_report.json
echo Full report available in: GEE_TESTING_REPORT.md
echo.

exit /b %EXIT_CODE%
