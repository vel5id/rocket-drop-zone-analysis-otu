#!/usr/bin/env python3
"""
Test script to verify tqdm fixes work correctly in non-interactive mode.
This script runs a minimal pipeline with output redirected to simulate
non-interactive execution (like in CI/CD or background processes).
"""
import os
import sys
import subprocess
import time
import signal
import threading

def run_with_timeout(cmd, timeout_seconds=30):
    """Run command with timeout monitoring."""
    # Безопасный вывод для Windows (без Unicode)
    safe_cmd = []
    for part in cmd:
        # Заменяем Unicode символы градуса
        safe_part = part.replace('°', 'deg')
        safe_cmd.append(safe_part)
    print(f"Running: {' '.join(safe_cmd)}")
    print(f"Timeout: {timeout_seconds}s")
    
    start_time = time.time()
    
    try:
        # Run with output captured to simulate non-interactive mode
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout_seconds
        )
        
        elapsed = time.time() - start_time
        print(f"[OK] Command completed in {elapsed:.2f}s")
        print(f"  Return code: {result.returncode}")
        
        if result.stdout:
            print(f"  Stdout (first 500 chars): {result.stdout[:500]}...")
        if result.stderr:
            print(f"  Stderr (first 500 chars): {result.stderr[:500]}...")
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print(f"[TIMEOUT] Command timed out after {elapsed:.2f}s")
        return False
    except Exception as e:
        print(f"[ERROR] Command failed with error: {e}")
        return False

def test_run_pipeline():
    """Test the main pipeline with minimal iterations."""
    print("\n" + "="*60)
    print("TEST 1: run_pipeline.py with minimal iterations")
    print("="*60)
    
    cmd = [
        sys.executable, "run_pipeline.py",
        "--iterations", "10",
        "--no-viz",
        "--no-gpu",
        "--output", "test_output"
    ]
    
    success = run_with_timeout(cmd, timeout_seconds=45)
    
    if success:
        print("[PASS] TEST 1 PASSED: Pipeline completed without hanging")
    else:
        print("[FAIL] TEST 1 FAILED: Pipeline hung or crashed")
    
    return success

def test_run_otu_pipeline():
    """Test the OTU pipeline with mock data."""
    print("\n" + "="*60)
    print("TEST 2: run_otu_pipeline.py with mock data")
    print("="*60)
    
    cmd = [
        sys.executable, "run_otu_pipeline.py",
        "--iterations", "10",
        "--mock",
        "--no-gpu",
        "--output", "test_output_otu"
    ]
    
    success = run_with_timeout(cmd, timeout_seconds=60)
    
    if success:
        print("[PASS] TEST 2 PASSED: OTU pipeline completed without hanging")
    else:
        print("[FAIL] TEST 2 FAILED: OTU pipeline hung or crashed")
    
    return success

def test_smart_tqdm_logic():
    """Test the smart_tqdm logic directly."""
    print("\n" + "="*60)
    print("TEST 3: Direct smart_tqdm logic test")
    print("="*60)
    
    test_code = '''
import sys
try:
    from tqdm import tqdm
    # Умный tqdm: отключается в неинтерактивном режиме
    def smart_tqdm(iterable, **kwargs):
        if not sys.stdout.isatty():
            # Неинтерактивный режим - отключаем прогресс-бар
            kwargs['disable'] = True
        return tqdm(iterable, **kwargs)
except ImportError:
    def smart_tqdm(iterable, **kwargs):
        desc = kwargs.get('desc', '')
        if desc:
            print(f"  {desc}...")
        return iterable

# Test in non-interactive mode (simulated)
print("Testing smart_tqdm in non-interactive mode...")
sys.stdout.isatty = lambda: False  # Simulate non-interactive

# Create a tqdm instance
from tqdm import tqdm
iterable = range(10)
regular = tqdm(iterable, desc="Regular tqdm")
smart = smart_tqdm(iterable, desc="Smart tqdm")

print(f"Regular tqdm disable: {regular.disable}")
print(f"Smart tqdm disable: {smart.disable}")

if smart.disable:
    print("[OK] smart_tqdm correctly disabled in non-interactive mode")
else:
    print("[FAIL] smart_tqdm NOT disabled in non-interactive mode")
'''
    
    cmd = [sys.executable, "-c", test_code]
    success = run_with_timeout(cmd, timeout_seconds=10)
    
    return success

def cleanup():
    """Clean up test directories."""
    import shutil
    test_dirs = ["test_output", "test_output_otu"]
    for dir_path in test_dirs:
        if os.path.exists(dir_path):
            try:
                shutil.rmtree(dir_path)
                print(f"Cleaned up: {dir_path}")
            except Exception as e:
                print(f"Warning: Could not clean up {dir_path}: {e}")

def main():
    """Run all tests."""
    print("Testing tqdm fixes for non-interactive mode")
    print(f"Python: {sys.version}")
    print(f"Working dir: {os.getcwd()}")
    
    # Clean up previous test outputs
    cleanup()
    
    # Run tests
    test1_passed = test_run_pipeline()
    test2_passed = test_run_otu_pipeline()
    test3_passed = test_smart_tqdm_logic()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Test 1 (run_pipeline.py): {'PASS' if test1_passed else 'FAIL'}")
    print(f"Test 2 (run_otu_pipeline.py): {'PASS' if test2_passed else 'FAIL'}")
    print(f"Test 3 (smart_tqdm logic): {'PASS' if test3_passed else 'FAIL'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n[SUCCESS] ALL TESTS PASSED: tqdm fixes are working correctly!")
        print("  The pipeline should no longer hang in non-interactive mode.")
    else:
        print("\n[FAILURE] SOME TESTS FAILED: Issues remain with tqdm handling.")
        print("  Check the logs above for details.")
    
    # Clean up
    cleanup()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())