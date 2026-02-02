"""
Debug script to verify generate_grid_in_polygons logic.
"""
import sys
import os
import json
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.abspath("."))

from grid.polygon_grid import generate_grid_in_polygons, create_ellipse_polygon, HAS_MATPLOTLIB

    with open("debug_result.txt", "w", encoding="utf-8") as f:
        def log(msg):
            print(msg)
            f.write(msg + "\n")
            
        log(f"DEBUG: HAS_MATPLOTLIB = {HAS_MATPLOTLIB}")
        
        # Define an ellipse (Zone 15 approx)
        ellipse = {
            "center_lat": 47.333,
            "center_lon": 66.775,
            "semi_major_km": 27.0,
            "semi_minor_km": 18.0,
            "angle_deg": 65.0
        }
        
        log("\n1. Creating Polygon...")
        poly = create_ellipse_polygon(ellipse, num_points=64)
        log(f"   Points: {len(poly)}")
        
        # Check if points vary in both axes
        lats = [p[0] for p in poly]
        lons = [p[1] for p in poly]
        log(f"   Lat range: {min(lats):.4f} to {max(lats):.4f}")
        log(f"   Lon range: {min(lons):.4f} to {max(lons):.4f}")
        
        log("\n2. Generating Grid...")
        grid = generate_grid_in_polygons([poly], cell_size_km=1.0)
        log(f"   Generated {len(grid)} cells")
        
        # Analyze Grid Shape
        if not grid:
            log("❌ FAIL: Grid is EMPTY")
            return

        g_lats = [c.center_lat for c in grid]
        g_lons = [c.center_lon for c in grid]
        
        g_min_lat, g_max_lat = min(g_lats), max(g_lats)
        g_min_lon, g_max_lon = min(g_lons), max(g_lons)
        
        log("\n3. Grid Analysis:")
        log(f"   Grid Lat Bounds: {g_min_lat:.4f} - {g_max_lat:.4f}")
        log(f"   Grid Lon Bounds: {g_min_lon:.4f} - {g_max_lon:.4f}")
        
        # Calculate bounding box area (approx cells)
        bbox_cells = (g_max_lat - g_min_lat) * (g_max_lon - g_min_lon) / ( (1/111) * (1/(111*0.7)))
        log(f"   Approx BBox Area (cells): {bbox_cells:.0f}")
        log(f"   Actual Cells: {len(grid)}")
        ratio = len(grid) / bbox_cells if bbox_cells else 0
        log(f"   Ratio: {ratio:.2f}")

        if ratio > 0.9:
            log("\n❌ FAIL: Grid is RECTANGULAR (ratio > 0.9)")
        else:
            log("\n✅ PASS: Grid is ELLIPTICAL (ratio < 0.9)")


    # Save to GeoJSON for sanity check
    from server_pipeline.geojson import grid_to_geojson
    with open("debug_grid_v2.geojson", "w") as f:
        json.dump(grid_to_geojson(grid), f)
    print("\nSaved debug_grid_v2.geojson")

if __name__ == "__main__":
    test_logic()
