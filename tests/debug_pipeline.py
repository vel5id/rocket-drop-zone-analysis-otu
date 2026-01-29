#!/usr/bin/env python3
"""
Debug script for OTU pipeline with detailed logging.
"""
import sys
import time
import traceback
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def debug_compute_ellipse():
    """Debug ellipse computation with detailed logging."""
    print("DEBUG: Starting ellipse computation test")
    
    # Create simple test data
    import numpy as np
    test_points = [
        {"lat": 47.0, "lon": 66.0, "is_fragment": False},
        {"lat": 47.1, "lon": 66.1, "is_fragment": False},
        {"lat": 46.9, "lon": 65.9, "is_fragment": False},
    ]
    
    print(f"DEBUG: Test points: {test_points}")
    
    try:
        from run_pipeline import compute_ellipse_from_geo
        print("DEBUG: Imported compute_ellipse_from_geo")
        
        start = time.time()
        result = compute_ellipse_from_geo(test_points)
        elapsed = time.time() - start
        
        print(f"DEBUG: Ellipse computed in {elapsed:.3f}s")
        print(f"DEBUG: Result: {result}")
        return True
    except Exception as e:
        print(f"DEBUG: Error in compute_ellipse_from_geo: {e}")
        traceback.print_exc()
        return False

def debug_grid_generation():
    """Debug grid generation with detailed logging."""
    print("\nDEBUG: Testing grid generation")
    
    try:
        from grid.polygon_grid import create_ellipse_polygon
        print("DEBUG: Imported create_ellipse_polygon")
        
        # Create test ellipse
        test_ellipse = {
            "center_lat": 47.0,
            "center_lon": 66.0,
            "semi_major_km": 10.0,
            "semi_minor_km": 5.0,
            "angle_deg": 45.0
        }
        
        start = time.time()
        polygon = create_ellipse_polygon(test_ellipse)
        elapsed = time.time() - start
        
        print(f"DEBUG: Polygon created in {elapsed:.3f}s")
        print(f"DEBUG: Polygon has {len(polygon)} points")
        print(f"DEBUG: First 3 points: {polygon[:3]}")
        return True
    except Exception as e:
        print(f"DEBUG: Error in grid generation: {e}")
        traceback.print_exc()
        return False

def debug_imports():
    """Debug all imports."""
    print("DEBUG: Testing imports")
    
    modules = [
        "numpy",
        "pandas",
        "config.otu_config",
        "otu.otu_logic",
        "grid.ellipse_calculator",
        "grid.polygon_grid",
        "visualization.satellite_overlay",
    ]
    
    all_ok = True
    for module in modules:
        try:
            if module == "numpy":
                import numpy as np
                print(f"  {module}: OK (v{np.__version__})")
            elif module == "pandas":
                import pandas as pd
                print(f"  {module}: OK (v{pd.__version__})")
            else:
                __import__(module)
                print(f"  {module}: OK")
        except Exception as e:
            print(f"  {module}: FAIL - {e}")
            all_ok = False
    
    return all_ok

def debug_simulation():
    """Debug Monte Carlo simulation."""
    print("\nDEBUG: Testing Monte Carlo simulation")
    
    try:
        from run_pipeline import run_simulation_standard
        print("DEBUG: Imported run_simulation_standard")
        
        start = time.time()
        primary, fragments, elapsed = run_simulation_standard(iterations=5, show_progress=False)
        total_time = time.time() - start
        
        print(f"DEBUG: Simulation completed in {total_time:.3f}s")
        print(f"DEBUG: Primary points: {len(primary)}")
        print(f"DEBUG: Fragment points: {len(fragments)}")
        
        if primary:
            print(f"DEBUG: First primary point: {primary[0]}")
        
        # Try to compute ellipse
        if primary:
            from run_pipeline import compute_ellipse_from_geo
            ellipse = compute_ellipse_from_geo(primary)
            print(f"DEBUG: Primary ellipse: {ellipse}")
        
        return True
    except Exception as e:
        print(f"DEBUG: Error in simulation: {e}")
        traceback.print_exc()
        return False

def debug_full_pipeline():
    """Debug full pipeline with timeout protection."""
    print("\n" + "="*60)
    print("DEBUG: FULL PIPELINE TEST (with timeout)")
    print("="*60)
    
    import subprocess
    import threading
    
    def run_with_timeout(cmd, timeout=30):
        """Run command with timeout."""
        print(f"DEBUG: Running: {cmd}")
        print(f"DEBUG: Timeout: {timeout}s")
        
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
            
            print(f"DEBUG: Command completed in {elapsed:.3f}s")
            print(f"DEBUG: Exit code: {result.returncode}")
            
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                print(f"DEBUG: Output (last 10 lines):")
                for line in lines[-10:]:
                    print(f"  {line}")
            
            if result.returncode != 0 and result.stderr:
                print(f"DEBUG: Error output:")
                print(f"  {result.stderr[:500]}")
            
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            print(f"DEBUG: Command timed out after {timeout}s")
            return False
        except Exception as e:
            print(f"DEBUG: Command failed: {e}")
            return False
    
    # Test with minimal parameters
    cmd = "venv_311\\Scripts\\python.exe run_otu_pipeline.py --date 2024-09-09 --iterations 5 --mock --no-gpu --output output/debug_test"
    
    # Clean output directory
    output_dir = Path("output/debug_test")
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir)
    
    return run_with_timeout(cmd, timeout=60)

def main():
    """Main debug function."""
    print("="*60)
    print("OTU PIPELINE DEBUG SESSION")
    print("="*60)
    
    tests = [
        ("Imports", debug_imports),
        ("Ellipse Computation", debug_compute_ellipse),
        ("Grid Generation", debug_grid_generation),
        ("Simulation", debug_simulation),
        ("Full Pipeline", debug_full_pipeline),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n>>> DEBUG TEST: {test_name}")
        try:
            success = test_func()
            results.append((test_name, success))
            status = "PASS" if success else "FAIL"
            print(f"DEBUG: {test_name}: {status}")
        except Exception as e:
            print(f"DEBUG: Test crashed: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("DEBUG SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"  {test_name}: {status}")
        if not success:
            all_passed = False
    
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    # Additional diagnostics
    print("\n" + "="*60)
    print("SYSTEM DIAGNOSTICS")
    print("="*60)
    
    import platform
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.platform()}")
    
    # Check memory
    import psutil
    memory = psutil.virtual_memory()
    print(f"Memory: {memory.available / (1024**3):.1f} GB available of {memory.total / (1024**3):.1f} GB")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)