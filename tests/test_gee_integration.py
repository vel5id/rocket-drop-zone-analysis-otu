"""
Comprehensive GEE Integration Test Suite

Tests all aspects of GEE integration:
1. Import checks
2. Authentication
3. Mock data generation
4. Real GEE data fetching
5. Pipeline execution
6. Output validation

Usage:
    python test_gee_integration.py --test all
    python test_gee_integration.py --test imports
    python test_gee_integration.py --test auth
    python test_gee_integration.py --test mock
    python test_gee_integration.py --test gee
    python test_gee_integration.py --test pipeline
"""
import sys
import os
import time
import argparse
import traceback
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Test results storage
test_results = {
    "passed": [],
    "failed": [],
    "warnings": [],
    "start_time": None,
    "end_time": None,
}


class DebugTimeout:
    """Debug timeout tracker to prevent infinite loops."""
    def __init__(self, max_seconds: int = 180, name: str = "Test"):
        self.max_seconds = max_seconds
        self.name = name
        self.start_time = time.time()
        self.iterations = 0
        
    def check(self, step: str = ""):
        """Check if timeout exceeded."""
        self.iterations += 1
        elapsed = time.time() - self.start_time
        
        if elapsed > self.max_seconds:
            raise TimeoutError(
                f"{self.name} exceeded {self.max_seconds}s timeout at step: {step} "
                f"(iteration {self.iterations}, elapsed {elapsed:.1f}s)"
            )
        
        if self.iterations % 100 == 0:
            print(f"  [{self.name}] Iteration {self.iterations}, elapsed {elapsed:.1f}s")


def log_test(name: str, status: str, message: str = ""):
    """Log test result."""
    timestamp = time.strftime("%H:%M:%S")
    if status == "PASS":
        test_results["passed"].append({"name": name, "message": message})
        print(f"[{timestamp}] [PASS] {name}: {message}")
    elif status == "FAIL":
        test_results["failed"].append({"name": name, "message": message})
        print(f"[{timestamp}] [FAIL] {name}: {message}")
    elif status == "WARN":
        test_results["warnings"].append({"name": name, "message": message})
        print(f"[{timestamp}] [WARN] {name}: {message}")


def test_imports() -> bool:
    """Test 1: Check all required imports."""
    print("\n" + "="*60)
    print("TEST 1: IMPORT CHECKS")
    print("="*60)
    
    timeout = DebugTimeout(60, "Import Test")
    
    required_modules = [
        ("numpy", "NumPy"),
        ("scipy", "SciPy"),
        ("pandas", "Pandas"),
        ("matplotlib", "Matplotlib"),
        ("folium", "Folium"),
        ("plotly", "Plotly"),
        ("rasterio", "Rasterio"),
        ("geopandas", "GeoPandas"),
        ("shapely", "Shapely"),
    ]
    
    optional_modules = [
        ("ee", "Google Earth Engine API"),
        ("numba", "Numba (GPU acceleration)"),
        ("tqdm", "TQDM (progress bars)"),
    ]
    
    all_passed = True
    
    # Test required modules
    for module_name, display_name in required_modules:
        timeout.check(f"import {module_name}")
        try:
            __import__(module_name)
            log_test(f"Import {display_name}", "PASS", f"{module_name} available")
        except ImportError as e:
            log_test(f"Import {display_name}", "FAIL", f"{module_name} not found: {e}")
            all_passed = False
    
    # Test optional modules
    for module_name, display_name in optional_modules:
        timeout.check(f"import {module_name}")
        try:
            __import__(module_name)
            log_test(f"Import {display_name}", "PASS", f"{module_name} available")
        except ImportError:
            log_test(f"Import {display_name}", "WARN", f"{module_name} not available (optional)")
    
    # Test project modules
    project_modules = [
        ("config.otu_config", "OTU Config"),
        ("otu.otu_logic", "OTU Logic"),
        ("gee.authenticator", "GEE Authenticator"),
        ("gee.local_processor", "GEE Local Processor"),
        ("grid.polygon_grid", "Grid Generator"),
        ("visualization.satellite_overlay", "Visualization"),
    ]
    
    for module_name, display_name in project_modules:
        timeout.check(f"import {module_name}")
        try:
            __import__(module_name)
            log_test(f"Import {display_name}", "PASS", f"{module_name} loaded")
        except ImportError as e:
            log_test(f"Import {display_name}", "FAIL", f"{module_name} failed: {e}")
            all_passed = False
    
    return all_passed


def test_authentication() -> bool:
    """Test 2: Check GEE authentication."""
    print("\n" + "="*60)
    print("TEST 2: GEE AUTHENTICATION")
    print("="*60)
    
    timeout = DebugTimeout(120, "Auth Test")
    
    try:
        import ee
        from gee.authenticator import initialize_ee
        
        timeout.check("initialize_ee")
        initialize_ee()
        
        timeout.check("ee.Number test")
        # Simple test to verify connection
        test_val = ee.Number(42).getInfo()
        
        if test_val == 42:
            log_test("GEE Authentication", "PASS", "Successfully authenticated and connected")
            return True
        else:
            log_test("GEE Authentication", "FAIL", f"Unexpected test value: {test_val}")
            return False
            
    except ImportError:
        log_test("GEE Authentication", "WARN", "earthengine-api not installed")
        return False
    except Exception as e:
        log_test("GEE Authentication", "FAIL", f"Authentication failed: {e}")
        return False


def test_mock_data() -> bool:
    """Test 3: Test mock data generation."""
    print("\n" + "="*60)
    print("TEST 3: MOCK DATA GENERATION")
    print("="*60)
    
    timeout = DebugTimeout(180, "Mock Data Test")
    
    try:
        from run_otu_pipeline import OTUBatchCalculator
        from grid.polygon_grid import GridCell
        import numpy as np
        
        # Create small test grid
        timeout.check("create test grid")
        test_cells = [
            GridCell(
                min_lat=47.0 + i*0.01,
                max_lat=47.0 + (i+1)*0.01,
                min_lon=66.0 + i*0.01,
                max_lon=66.0 + (i+1)*0.01,
                center_lat=47.0 + i*0.01 + 0.005,
                center_lon=66.0 + i*0.01 + 0.005,
            )
            for i in range(10)
        ]
        
        timeout.check("create calculator")
        calculator = OTUBatchCalculator(output_dir="output/test")
        
        timeout.check("generate mock data")
        results = calculator._generate_mock_batch(test_cells)
        
        # Validate results
        timeout.check("validate results")
        if results.shape != (10, 6):
            log_test("Mock Data Shape", "FAIL", f"Expected (10, 6), got {results.shape}")
            return False
        
        log_test("Mock Data Shape", "PASS", f"Correct shape: {results.shape}")
        
        # Check value ranges
        timeout.check("check value ranges")
        ndvi = results[:, 0]
        q_otu = results[:, 4]
        
        if not (0 <= ndvi.min() <= ndvi.max() <= 1):
            log_test("Mock NDVI Range", "FAIL", f"NDVI out of range: [{ndvi.min():.3f}, {ndvi.max():.3f}]")
            return False
        
        log_test("Mock NDVI Range", "PASS", f"NDVI in [0, 1]: [{ndvi.min():.3f}, {ndvi.max():.3f}]")
        
        if not (0 <= q_otu.min() <= q_otu.max() <= 1):
            log_test("Mock OTU Range", "FAIL", f"OTU out of range: [{q_otu.min():.3f}, {q_otu.max():.3f}]")
            return False
        
        log_test("Mock OTU Range", "PASS", f"OTU in [0, 1]: [{q_otu.min():.3f}, {q_otu.max():.3f}]")
        
        # Check for NaN values
        timeout.check("check for NaN")
        if np.isnan(results).any():
            log_test("Mock Data NaN Check", "WARN", "Some NaN values present")
        else:
            log_test("Mock Data NaN Check", "PASS", "No NaN values")
        
        return True
        
    except Exception as e:
        log_test("Mock Data Generation", "FAIL", f"Error: {e}\n{traceback.format_exc()}")
        return False


def test_gee_data() -> bool:
    """Test 4: Test real GEE data fetching (small area)."""
    print("\n" + "="*60)
    print("TEST 4: GEE DATA FETCHING")
    print("="*60)
    
    timeout = DebugTimeout(300, "GEE Data Test")
    
    try:
        import ee
        from gee.authenticator import initialize_ee
        from run_otu_pipeline import OTUBatchCalculator
        from grid.polygon_grid import GridCell
        import numpy as np
        
        timeout.check("initialize GEE")
        initialize_ee()
        
        # Create tiny test grid (2x2 cells)
        timeout.check("create test grid")
        test_cells = [
            GridCell(
                min_lat=47.3 + i*0.01,
                max_lat=47.3 + (i+1)*0.01,
                min_lon=66.7 + i*0.01,
                max_lon=66.7 + (i+1)*0.01,
                center_lat=47.3 + i*0.01 + 0.005,
                center_lon=66.7 + i*0.01 + 0.005,
            )
            for i in range(4)
        ]
        
        timeout.check("create calculator")
        calculator = OTUBatchCalculator(output_dir="output/test")
        
        timeout.check("fetch NDVI")
        try:
            ndvi_arr = calculator._fetch_ndvi_batch(test_cells, "2024-09-09")
            log_test("GEE NDVI Fetch", "PASS", f"Fetched {len(ndvi_arr)} values")
        except Exception as e:
            log_test("GEE NDVI Fetch", "FAIL", f"NDVI fetch failed: {e}")
            return False
        
        timeout.check("fetch soil")
        try:
            soil_arr = calculator._fetch_soil_batch(test_cells)
            log_test("GEE Soil Fetch", "PASS", f"Fetched {soil_arr.shape} values")
        except Exception as e:
            log_test("GEE Soil Fetch", "FAIL", f"Soil fetch failed: {e}")
            return False
        
        timeout.check("fetch relief")
        try:
            relief_arr = calculator._fetch_relief_batch(test_cells)
            log_test("GEE Relief Fetch", "PASS", f"Fetched {relief_arr.shape} values")
        except Exception as e:
            log_test("GEE Relief Fetch", "FAIL", f"Relief fetch failed: {e}")
            return False
        
        return True
        
    except ImportError:
        log_test("GEE Data Fetching", "WARN", "GEE not available, skipping")
        return False
    except Exception as e:
        log_test("GEE Data Fetching", "FAIL", f"Error: {e}\n{traceback.format_exc()}")
        return False


def test_pipeline_mock() -> bool:
    """Test 5: Test full pipeline with mock data."""
    print("\n" + "="*60)
    print("TEST 5: FULL PIPELINE (MOCK DATA)")
    print("="*60)
    
    timeout = DebugTimeout(300, "Pipeline Mock Test")
    
    try:
        # Run pipeline with mock data
        timeout.check("import run_otu_pipeline")
        import run_otu_pipeline
        
        # Override sys.argv for testing
        timeout.check("setup test args")
        original_argv = sys.argv
        sys.argv = [
            "run_otu_pipeline.py",
            "--mock",
            "--zone-preset", "yu24",
            "--output", "output/test_mock",
            "-n", "10",  # Small number of iterations
        ]
        
        try:
            timeout.check("run main")
            run_otu_pipeline.main()
            log_test("Pipeline Mock Execution", "PASS", "Pipeline completed successfully")
            
            # Check outputs
            timeout.check("check outputs")
            output_dir = Path("output/test_mock")
            
            if not output_dir.exists():
                log_test("Pipeline Mock Outputs", "FAIL", "Output directory not created")
                return False
            
            # Check for key files
            expected_files = [
                "otu_visualization.html",
                "otu/otu_2024-09-09.geojson",
            ]
            
            missing_files = []
            for file_path in expected_files:
                full_path = output_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
            
            if missing_files:
                log_test("Pipeline Mock Outputs", "WARN", f"Missing files: {missing_files}")
            else:
                log_test("Pipeline Mock Outputs", "PASS", "All expected files created")
            
            return True
            
        finally:
            sys.argv = original_argv
            
    except Exception as e:
        log_test("Pipeline Mock Execution", "FAIL", f"Error: {e}\n{traceback.format_exc()}")
        return False


def test_pipeline_gee() -> bool:
    """Test 6: Test full pipeline with real GEE data (small area)."""
    print("\n" + "="*60)
    print("TEST 6: FULL PIPELINE (REAL GEE DATA)")
    print("="*60)
    
    timeout = DebugTimeout(600, "Pipeline GEE Test")
    
    try:
        import ee
        from gee.authenticator import initialize_ee
        
        timeout.check("initialize GEE")
        initialize_ee()
        
        # Run pipeline with real GEE data
        timeout.check("import run_otu_pipeline")
        import run_otu_pipeline
        
        # Override sys.argv for testing
        timeout.check("setup test args")
        original_argv = sys.argv
        sys.argv = [
            "run_otu_pipeline.py",
            "--zone-preset", "yu24",
            "--output", "output/test_gee",
            "--date", "2024-09-09",
        ]
        
        try:
            timeout.check("run main")
            run_otu_pipeline.main()
            log_test("Pipeline GEE Execution", "PASS", "Pipeline completed successfully")
            
            # Check outputs
            timeout.check("check outputs")
            output_dir = Path("output/test_gee")
            
            if not output_dir.exists():
                log_test("Pipeline GEE Outputs", "FAIL", "Output directory not created")
                return False
            
            # Check for key files
            expected_files = [
                "otu_visualization.html",
                "otu/otu_2024-09-09.geojson",
            ]
            
            missing_files = []
            for file_path in expected_files:
                full_path = output_dir / file_path
                if not full_path.exists():
                    missing_files.append(file_path)
            
            if missing_files:
                log_test("Pipeline GEE Outputs", "WARN", f"Missing files: {missing_files}")
            else:
                log_test("Pipeline GEE Outputs", "PASS", "All expected files created")
            
            # Validate GeoJSON
            timeout.check("validate GeoJSON")
            geojson_path = output_dir / "otu/otu_2024-09-09.geojson"
            if geojson_path.exists():
                with open(geojson_path) as f:
                    data = json.load(f)
                    
                if "features" in data and len(data["features"]) > 0:
                    log_test("GeoJSON Validation", "PASS", f"GeoJSON has {len(data['features'])} features")
                else:
                    log_test("GeoJSON Validation", "FAIL", "GeoJSON has no features")
                    return False
            
            return True
            
        finally:
            sys.argv = original_argv
            
    except ImportError:
        log_test("Pipeline GEE Execution", "WARN", "GEE not available, skipping")
        return False
    except Exception as e:
        log_test("Pipeline GEE Execution", "FAIL", f"Error: {e}\n{traceback.format_exc()}")
        return False


def generate_report():
    """Generate test report."""
    print("\n" + "="*60)
    print("TEST REPORT")
    print("="*60)
    
    total_tests = len(test_results["passed"]) + len(test_results["failed"])
    passed = len(test_results["passed"])
    failed = len(test_results["failed"])
    warnings = len(test_results["warnings"])
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed} ({100*passed/max(total_tests, 1):.1f}%)")
    print(f"Failed: {failed}")
    print(f"Warnings: {warnings}")
    
    if test_results["failed"]:
        print("\nFailed Tests:")
        for test in test_results["failed"]:
            print(f"  ✗ {test['name']}: {test['message']}")
    
    if test_results["warnings"]:
        print("\nWarnings:")
        for test in test_results["warnings"]:
            print(f"  ⚠ {test['name']}: {test['message']}")
    
    # Save report to file
    report_path = Path("output/test_report.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    return failed == 0


def main():
    parser = argparse.ArgumentParser(description="GEE Integration Test Suite")
    parser.add_argument(
        "--test",
        choices=["all", "imports", "auth", "mock", "gee", "pipeline"],
        default="all",
        help="Which test to run"
    )
    
    args = parser.parse_args()
    
    test_results["start_time"] = time.time()
    
    print("\n" + "="*60)
    print("GEE INTEGRATION TEST SUITE")
    print("="*60)
    print(f"Test Mode: {args.test}")
    print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = True
    
    if args.test in ["all", "imports"]:
        success = test_imports() and success
    
    if args.test in ["all", "auth"]:
        success = test_authentication() and success
    
    if args.test in ["all", "mock"]:
        success = test_mock_data() and success
    
    if args.test in ["all", "gee"]:
        success = test_gee_data() and success
    
    if args.test in ["all", "pipeline"]:
        success = test_pipeline_mock() and success
        if args.test == "all":
            success = test_pipeline_gee() and success
    
    test_results["end_time"] = time.time()
    elapsed = test_results["end_time"] - test_results["start_time"]
    
    print(f"\nTotal Execution Time: {elapsed:.1f}s")
    
    success = generate_report() and success
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
