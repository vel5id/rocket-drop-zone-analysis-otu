#!/usr/bin/env python
"""
Diagnostic script to catch errors in the simulation pipeline.
Run this from the project root: python debug_simulation.py
"""
import sys
import os
import time
import traceback

# Ensure project root is in path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

def log(msg: str):
    """Print with timestamp."""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")
    sys.stdout.flush()  # Force immediate output

def main():
    log("=" * 60)
    log("DIAGNOSTIC SIMULATION SCRIPT")
    log("=" * 60)
    
    # =========================================
    # STEP 1: Import modules
    # =========================================
    log("\n[STEP 1] Importing run_pipeline...")
    try:
        from run_pipeline import run_simulation_gpu, run_simulation_standard, compute_ellipse_from_geo
        log("  ✅ run_pipeline imported successfully")
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return
    
    log("\n[STEP 1b] Importing grid.polygon_grid...")
    try:
        from grid.polygon_grid import create_ellipse_polygon, generate_grid_in_polygons, HAS_MATPLOTLIB
        log(f"  ✅ polygon_grid imported successfully")
        log(f"  📊 HAS_MATPLOTLIB = {HAS_MATPLOTLIB}")
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return

    # =========================================
    # STEP 2: Run Monte Carlo simulation
    # =========================================
    log("\n[STEP 2] Running Monte Carlo simulation (100 iterations)...")
    try:
        start_time = time.time()
        primary_geo, fragment_geo, sim_time = run_simulation_standard(100, show_progress=True)
        elapsed = time.time() - start_time
        log(f"  ✅ Simulation completed in {elapsed:.2f}s (internal: {sim_time:.2f}s)")
        log(f"  📊 Primary points: {len(primary_geo)}")
        log(f"  📊 Fragment points: {len(fragment_geo)}")
        
        if primary_geo:
            log(f"  📍 Sample primary point: {primary_geo[0]}")
        if fragment_geo:
            log(f"  📍 Sample fragment point: {fragment_geo[0]}")
            
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return

    # =========================================
    # STEP 3: Compute dispersion ellipses
    # =========================================
    log("\n[STEP 3] Computing primary ellipse...")
    try:
        start_time = time.time()
        primary_ellipse = compute_ellipse_from_geo(primary_geo)
        elapsed = time.time() - start_time
        log(f"  ✅ Primary ellipse computed in {elapsed:.2f}s")
        log(f"  📊 Ellipse: {primary_ellipse}")
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return

    log("\n[STEP 3b] Computing fragment ellipse...")
    try:
        start_time = time.time()
        fragment_ellipse = compute_ellipse_from_geo(fragment_geo) if fragment_geo else None
        elapsed = time.time() - start_time
        log(f"  ✅ Fragment ellipse computed in {elapsed:.2f}s")
        log(f"  📊 Ellipse: {fragment_ellipse}")
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return

    # =========================================
    # STEP 4: Create ellipse polygons
    # =========================================
    log("\n[STEP 4] Creating ellipse polygons...")
    polygons = []
    try:
        if primary_ellipse:
            start_time = time.time()
            poly = create_ellipse_polygon(primary_ellipse, scale=1.0)
            elapsed = time.time() - start_time
            log(f"  ✅ Primary polygon created in {elapsed:.2f}s ({len(poly)} points)")
            polygons.append(poly)
            
        if fragment_ellipse:
            start_time = time.time()
            poly = create_ellipse_polygon(fragment_ellipse, scale=1.0)
            elapsed = time.time() - start_time
            log(f"  ✅ Fragment polygon created in {elapsed:.2f}s ({len(poly)} points)")
            polygons.append(poly)
            
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return

    # =========================================
    # STEP 5: Generate grid (THIS IS LIKELY THE PROBLEM AREA)
    # =========================================
    log("\n[STEP 5] Generating ecological grid...")
    log(f"  📊 Number of polygons: {len(polygons)}")
    
    try:
        start_time = time.time()
        
        # Add verbose logging inside the function
        log("  ⏳ Calling generate_grid_in_polygons(cell_size_km=1.0)...")
        grid = generate_grid_in_polygons(polygons, cell_size_km=1.0)
        
        elapsed = time.time() - start_time
        log(f"  ✅ Grid generated in {elapsed:.2f}s")
        log(f"  📊 Total cells: {len(grid)}")
        
        if grid:
            log(f"  📍 Sample cell: lat={grid[0].center_lat:.4f}, lon={grid[0].center_lon:.4f}")
            
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return

    # =========================================
    # STEP 6: Convert to GeoJSON
    # =========================================
    log("\n[STEP 6] Converting impact points to GeoJSON...")
    try:
        start_time = time.time()
        all_points = primary_geo + fragment_geo
        features = []
        for i, p in enumerate(all_points):
            features.append({
                "type": "Feature",
                "properties": {"id": i + 1},
                "geometry": {"type": "Point", "coordinates": [p["lon"], p["lat"]]}
            })
        elapsed = time.time() - start_time
        log(f"  ✅ GeoJSON created in {elapsed:.2f}s ({len(features)} features)")
    except Exception as e:
        log(f"  ❌ FAILED: {e}")
        traceback.print_exc()
        return

    # =========================================
    # SUMMARY
    # =========================================
    log("\n" + "=" * 60)
    log("🎉 ALL STEPS COMPLETED SUCCESSFULLY!")
    log("=" * 60)
    log(f"  Primary impacts: {len(primary_geo)}")
    log(f"  Fragment impacts: {len(fragment_geo)}")
    log(f"  Grid cells: {len(grid)}")
    log(f"  Primary ellipse: {primary_ellipse['semi_major_km']:.2f} x {primary_ellipse['semi_minor_km']:.2f} km")
    if fragment_ellipse:
        log(f"  Fragment ellipse: {fragment_ellipse['semi_major_km']:.2f} x {fragment_ellipse['semi_minor_km']:.2f} km")

if __name__ == "__main__":
    main()
