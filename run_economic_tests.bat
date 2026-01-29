@echo off
REM =================================================================
REM Economic Damage Tests Batch File
REM Task 5.1: Economic Calculator Implementation
REM Created: 2026-01-28
REM =================================================================

echo.
echo ========================================
echo  ECONOMIC DAMAGE ASSESSMENT TESTS
echo  Task 5.1 Implementation
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv_311\Scripts\activate.bat" (
    echo ERROR: Virtual environment 'venv_311' not found.
    echo Please run setup_env_311.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv_311\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [1/5] Checking Python version...
python --version

echo.
echo [2/5] Running unit tests for EconomicDamageCalculator...
python -m pytest tests/test_economic_damage.py -v --tb=short

if errorlevel 1 (
    echo WARNING: Some tests failed. Check output above.
) else (
    echo SUCCESS: All unit tests passed.
)

echo.
echo [3/5] Running specific test classes...
echo.
echo --- TestEconomicDamageCalculator ---
python -m pytest tests/test_economic_damage.py::TestEconomicDamageCalculator -v --tb=no

echo.
echo --- TestLegacyFunctions ---
python -m pytest tests/test_economic_damage.py::TestLegacyFunctions -v --tb=no

echo.
echo --- TestIntegration ---
python -m pytest tests/test_economic_damage.py::TestIntegration -v --tb=no

echo.
echo [4/5] Running coverage report...
python -m pytest tests/test_economic_damage.py --cov=otu.economic_damage --cov-report=term-missing

echo.
echo [5/5] Running quick functionality test...
python -c "
import numpy as np
from otu.economic_damage import EconomicDamageCalculator, calculate_comprehensive_damage

print('Quick functionality test:')
print('=' * 40)

# Test data (OTU_245 from roadmap)
otu_data = np.array([[0.45, 0.35, 0.28, 0.82, 0.31, 0.52]])

# Test new calculator
calculator = EconomicDamageCalculator()
result = calculator.calculate_total_damage(otu_data, cell_size_km=1.0)

print(f'Test Cell: OTU_245 (q_otu=0.31)')
print(f'Area: {result[\"total_area_ha\"]:.0f} ha')
print(f'Vegetation Cost: {result[\"vegetation_cost_kzt\"]:,.0f} KZT')
print(f'Soil Cost: {result[\"soil_cost_kzt\"]:,.0f} KZT')
print(f'Fire Cost: {result[\"fire_cost_kzt\"]:,.0f} KZT')
print(f'Contamination Cost: {result[\"contamination_cost_kzt\"]:,.0f} KZT')
print(f'Mechanical Cost: {result[\"mechanical_cost_kzt\"]:,.0f} KZT')
print('-' * 40)
print(f'TOTAL: {result[\"grand_total_kzt\"]:,.0f} KZT')
print(f'      = {result[\"grand_total_usd\"]:,.0f} USD')

# Test convenience function
conv_result = calculate_comprehensive_damage(otu_data)
print(f'\\nConvenience function test: {conv_result[\"grand_total_kzt\"]:,.0f} KZT')

print('\\nAll components tested successfully.')
"

echo.
echo ========================================
echo  TEST COMPLETE
echo ========================================
echo.
echo Documentation created: docs/economic_damage_methodology.md
echo Test file: tests/test_economic_damage.py
echo Implementation: otu/economic_damage.py
echo.
echo To view methodology:
echo   type docs/economic_damage_methodology.md
echo.
pause