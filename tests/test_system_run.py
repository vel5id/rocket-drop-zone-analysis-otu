#!/usr/bin/env python3
"""
Test system run for OTU pipeline.
"""
import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, timeout=300, use_venv=True):
    """Run command with timeout."""
    if use_venv and sys.platform == "win32":
        # Use virtual environment Python on Windows
        venv_python = "venv_311\\Scripts\\python.exe"
        if Path(venv_python).exists():
            # Replace "python" with venv python
            if cmd.startswith("python "):
                cmd = f"{venv_python} {cmd[7:]}"
            elif "python " in cmd:
                cmd = cmd.replace("python ", f"{venv_python} ")
    
    print(f"Running: {cmd}")
    start = time.time()
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            encoding='utf-8',
            errors='ignore'
        )
        elapsed = time.time() - start
        
        print(f"  Exit code: {result.returncode}")
        print(f"  Time: {elapsed:.1f}s")
        
        if result.stdout:
            # Show first 500 chars, but avoid Unicode errors
            output_preview = result.stdout[:500].replace('\n', '\\n')
            print(f"  Output (first 500 chars):")
            print(f"    {output_preview}...")
        
        if result.returncode != 0 and result.stderr:
            error_preview = result.stderr[:500].replace('\n', '\\n')
            print(f"  Error (first 500 chars):")
            print(f"    {error_preview}...")
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"  [ERROR] Command timed out after {timeout}s")
        return False
    except Exception as e:
        print(f"  [ERROR] Command failed: {e}")
        return False

def test_imports():
    """Test basic imports."""
    print("\n" + "="*60)
    print("TEST 1: BASIC IMPORTS")
    print("="*60)
    
    test_code = """
import sys
sys.path.insert(0, '.')
try:
    import numpy as np
    print(f"  numpy: OK ({np.__version__})")
    
    import config.otu_config
    print(f"  config.otu_config: OK")
    
    from otu.otu_logic import compute_q_si, compute_q_bi, compute_otu_index
    print(f"  otu.otu_logic: OK")
    
    print("  [SUCCESS] All imports work")
except Exception as e:
    print(f"  [ERROR] Import failed: {e}")
    sys.exit(1)
"""
    
    with open("test_imports.py", "w") as f:
        f.write(test_code)
    
    return run_command("python test_imports.py")

def test_quick_pipeline():
    """Test quick pipeline run with mock data."""
    print("\n" + "="*60)
    print("TEST 2: QUICK PIPELINE RUN (MOCK MODE)")
    print("="*60)
    
    cmd = "python run_otu_pipeline.py --date 2024-09-09 --iterations 10 --mock --no-gpu --output output/test_run"
    
    # Clean previous test output
    test_dir = Path("output/test_run")
    if test_dir.exists():
        import shutil
        shutil.rmtree(test_dir)
    
    return run_command(cmd, timeout=600)

def test_sensitivity_analysis():
    """Test sensitivity analysis script."""
    print("\n" + "="*60)
    print("TEST 3: SENSITIVITY ANALYSIS")
    print("="*60)
    
    # Check if sensitivity script exists
    if not Path("scripts/run_sensitivity_complete.py").exists():
        print("  [SKIP] Sensitivity script not found")
        return True
    
    cmd = "python scripts/run_sensitivity_complete.py --quick"
    return run_command(cmd, timeout=300)

def check_output_files():
    """Check generated output files."""
    print("\n" + "="*60)
    print("TEST 4: OUTPUT FILES CHECK")
    print("="*60)
    
    required_files = [
        "output/test_run/otu/otu_2024-09-09.geojson",
        "output/test_run/otu_visualization.html",
        "output/test_run/indices/q_ndvi.html",
    ]
    
    all_ok = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            size_kb = path.stat().st_size / 1024
            print(f"  {file_path}: OK ({size_kb:.1f} KB)")
        else:
            print(f"  {file_path}: MISSING")
            all_ok = False
    
    # Check for any output files
    test_dir = Path("output/test_run")
    if test_dir.exists():
        files = list(test_dir.rglob("*"))
        print(f"  Total files in test_run: {len(files)}")
        for f in files[:10]:  # Show first 10
            if f.is_file():
                print(f"    - {f.relative_to(test_dir)}")
    
    return all_ok

def main():
    """Main test function."""
    print("="*60)
    print("OTU SYSTEM TEST RUN")
    print("="*60)
    
    tests = [
        ("Basic Imports", test_imports),
        ("Quick Pipeline", test_quick_pipeline),
        ("Sensitivity Analysis", test_sensitivity_analysis),
        ("Output Files", check_output_files),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n>>> Running: {test_name}")
        success = test_func()
        results.append((test_name, success))
        if not success:
            print(f"  [WARNING] Test '{test_name}' failed")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    # Cleanup
    for temp_file in ["test_imports.py"]:
        if Path(temp_file).exists():
            Path(temp_file).unlink()
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)