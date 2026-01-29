#!/usr/bin/env python
"""
Test script for server_pipeline module.
Run: python test_server_pipeline.py
"""
import sys
import os
import time

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def main():
    print("=" * 60)
    print("SERVER PIPELINE TEST")
    print("=" * 60)
    
    # Import the module
    print("\n[1] Importing server_pipeline...")
    try:
        from server_pipeline.simulation import run_simulation_safe
        print("  ✅ Import successful")
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Run simulation
    print("\n[2] Running simulation (100 iterations)...")
    start = time.time()
    
    try:
        result = run_simulation_safe(
            iterations=100,
            use_gpu=True,
            cell_size_km=2.0,  # Larger cells for faster test
        )
        elapsed = time.time() - start
        print(f"\n  ✅ Completed in {elapsed:.1f}s")
        
        # Print results
        print("\n[3] Results:")
        print(f"  Primary Ellipse: {result.primary_ellipse}")
        print(f"  Fragment Ellipse: {result.fragment_ellipse}")
        print(f"  Impact Points: {len(result.impact_points.get('features', []))} features")
        print(f"  Grid Cells: {len(result.otu_grid.get('features', []))} features")
        print(f"  Stats: {result.stats}")
        
        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n  ❌ Simulation failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
