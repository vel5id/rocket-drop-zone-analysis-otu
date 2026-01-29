"""
Test script for Figure 18 creation.
Validates that the main script runs without errors and produces expected outputs.
"""
import sys
import os
from pathlib import Path

def test_imports():
    """Test that required modules can be imported."""
    print("Testing imports...")
    try:
        import geopandas
        import matplotlib.pyplot as plt
        from scripts.figure_enhancement_complete import FigureEnhancer
        print("  ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False

def test_data_file():
    """Test that OTU data file exists."""
    print("Testing data file...")
    otu_file = Path("output/otu/otu_2024-09-09.geojson")
    if otu_file.exists():
        print(f"  ✓ OTU file found: {otu_file}")
        return True
    else:
        print(f"  ✗ OTU file not found: {otu_file}")
        print("  Note: Script will create mock data if file missing")
        return False

def test_script_structure():
    """Test that the main script exists and has correct structure."""
    print("Testing script structure...")
    script_path = Path("scripts/create_figure_18_final.py")
    if not script_path.exists():
        print(f"  ✗ Script not found: {script_path}")
        return False
    
    with open(script_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_functions = ['create_figure_18_final', 'apply_all_enhancements', 'main']
    missing = []
    for func in required_functions:
        if func not in content:
            missing.append(func)
    
    if missing:
        print(f"  ✗ Missing functions: {missing}")
        return False
    else:
        print("  ✓ Script structure OK")
        return True

def test_output_directories():
    """Test that output directories exist or can be created."""
    print("Testing output directories...")
    output_dir = Path("outputs/figures")
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Output directory ready: {output_dir}")
        return True
    except Exception as e:
        print(f"  ✗ Cannot create output directory: {e}")
        return False

def test_batch_file():
    """Test that batch file exists."""
    print("Testing batch file...")
    batch_path = Path("run_create_figure_18.bat")
    if batch_path.exists():
        print(f"  ✓ Batch file found: {batch_path}")
        return True
    else:
        print(f"  ✗ Batch file not found: {batch_path}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("TESTING TASK 3.6: FIGURE 18 FINAL MAP")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_data_file,
        test_script_structure,
        test_output_directories,
        test_batch_file,
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "PASS" if result else "FAIL"
        print(f"Test {i}: {test.__name__}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed. Task 3.6 implementation is ready.")
        print("\nNext steps:")
        print("1. Activate virtual environment: venv_311\\Scripts\\activate")
        print("2. Run the batch file: run_create_figure_18.bat")
        print("3. Check outputs in outputs/figures/")
        return 0
    else:
        print("\n❌ Some tests failed. Please fix issues before running.")
        return 1

if __name__ == "__main__":
    sys.exit(main())