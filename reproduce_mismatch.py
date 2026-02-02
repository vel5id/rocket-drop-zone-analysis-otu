from __future__ import annotations
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.models import SimulationRequest
from api.zone_preview_logic import get_zone_preview
from server_pipeline.simulation import run_simulation_safe
from config.zones import YU24_ZONES

def verify_coordinates():
    zone_id = "yu24_25"
    
    # 1. Get Preview
    req = SimulationRequest(
        zone_id=zone_id,
        # Dummy required fields
        iterations=1,
        use_gpu=False,
        launch_lat=0, launch_lon=0, azimuth=0,
        sep_altitude=0, sep_velocity=0, sep_fp_angle=0, sep_azimuth=0,
    )
    
    print("--- PREVIEW ---")
    try:
        preview = get_zone_preview(req)
        if preview.primary_polygon:
            coords = preview.primary_polygon.geometry["coordinates"][0]
            print(f"Preview Polygon Points: {len(coords)}")
            print(f"Preview Sample (Lat/Lon?): {coords[0]}")
            # Identify if Lat/Lon or Lon/Lat
            # Kazakhstan is Lat ~47, Lon ~66
            c = coords[0]
            if 40 < c[1] < 55 and 60 < c[0] < 80:
                print("Preview Format: [Lon, Lat] (GeoJSON Standard)")
            else:
                print("Preview Format: [Lat, Lon] (Non-Standard?)")
                
            # Get center
            lons = [p[0] for p in coords]
            lats = [p[1] for p in coords]
            center_lon = sum(lons) / len(lons)
            center_lat = sum(lats) / len(lats)
            print(f"Preview Center: {center_lat:.4f}, {center_lon:.4f}")
        else:
            print("No primary polygon in preview")
    except Exception as e:
        print(f"Preview Failed: {e}")

    # 2. Run Simulation
    print("\n--- SIMULATION ---")
    try:
        result = run_simulation_safe(
            iterations=1,
            zone_id=zone_id,
            # Minimize computation
            cell_size_km=5.0
        )
        
        # Check Grid
        grid_json = result.otu_grid
        if grid_json and grid_json["features"]:
            first_feat = grid_json["features"][0]
            coords = first_feat["geometry"]["coordinates"][0]
            print(f"Grid Cell 0 Points: {len(coords)}")
            print(f"Grid Cell 0 Sample: {coords[0]}")
            
            # Get bounds of whole grid
            all_lons = []
            all_lats = []
            for f in grid_json["features"]:
                c = f["geometry"]["coordinates"][0]
                all_lons.extend([p[0] for p in c])
                all_lats.extend([p[1] for p in c])
            
            min_lon, max_lon = min(all_lons), max(all_lons)
            min_lat, max_lat = min(all_lats), max(all_lats)
            
            grid_center_lat = (min_lat + max_lat) / 2
            grid_center_lon = (min_lon + max_lon) / 2
            
            print(f"Grid Center: {grid_center_lat:.4f}, {grid_center_lon:.4f}")
            print(f"Grid Bounds: Lat [{min_lat:.4f}, {max_lat:.4f}], Lon [{min_lon:.4f}, {max_lon:.4f}]")
        else:
            print("No grid generated")

        # Check Ellipse in Result
        if result.primary_ellipse:
            print(f"Result Ellipse Center: {result.primary_ellipse['center_lat']:.4f}, {result.primary_ellipse['center_lon']:.4f}")

    except Exception as e:
        print(f"Simulation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    verify_coordinates()
