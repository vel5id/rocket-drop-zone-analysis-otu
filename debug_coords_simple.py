from __future__ import annotations
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.zones import YU24_ZONES
from grid.polygon_grid import create_ellipse_polygon

def debug_preview_logic():
    print("--- 1. PREVIEW LOGIC ---")
    zone_id = "yu24_25"
    if zone_id in YU24_ZONES:
        zone_def = YU24_ZONES[zone_id]
        print(f"Zone Config: {zone_def.center_lat}, {zone_def.center_lon}")
        
        ellipse_params = {
            "center_lat": zone_def.center_lat,
            "center_lon": zone_def.center_lon,
            "semi_major_km": zone_def.semi_major_km,
            "semi_minor_km": zone_def.semi_minor_km,
            "angle_deg": zone_def.angle_deg
        }
        
        poly = create_ellipse_polygon(ellipse_params, scale=1.0)
        coords = poly  # List of (lat, lon)
        print(f"Preview Polygon Points: {len(coords)}")
        print(f"Preview Sample (Lat, Lon): {coords[0]}")
        
        lats = [p[0] for p in coords]
        lons = [p[1] for p in coords]
        
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        print(f"Preview Bounds: Lat [{min_lat:.4f}, {max_lat:.4f}], Lon [{min_lon:.4f}, {max_lon:.4f}]")
    else:
        print("Zone not found")

def debug_simulation_logic():
    print("\n--- 2. SIMULATION LOGIC (MOCKED) ---")
    zone_id = "yu24_25"
    
    # Mocking run_simulation_safe logic for Preset
    if zone_id in YU24_ZONES:
        zone_def = YU24_ZONES[zone_id]
        print(f"Sim Config: {zone_def.center_lat}, {zone_def.center_lon}")
        
        primary_ellipse = {
            "center_lat": zone_def.center_lat,
            "center_lon": zone_def.center_lon,
            "semi_major_km": zone_def.semi_major_km,
            "semi_minor_km": zone_def.semi_minor_km,
            "angle_deg": zone_def.angle_deg,
        }
        
        # Calling create_ellipse_polygons from grid_generator
        # But importing create_ellipse_polygon directly to avoid heavy imports
        poly = create_ellipse_polygon(primary_ellipse, scale=1.0)
        
        # Grid Generation Logic (simplified)
        lats = [p[0] for p in poly]
        lons = [p[1] for p in poly]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        
        print(f"Sim Polygon Points: {len(poly)}")
        print(f"Sim Sample (Lat, Lon): {poly[0]}")
        print(f"Sim Bounds: Lat [{min_lat:.4f}, {max_lat:.4f}], Lon [{min_lon:.4f}, {max_lon:.4f}]")
        
        # Check GeoJSON conversion logic
        # grid_to_geojson expects GridCell objects
        # Simulating a cell
        cell_min_lat = min_lat
        cell_max_lat = min_lat + 0.01
        cell_min_lon = min_lon
        cell_max_lon = min_lon + 0.01
        
        geojson_coords = [
            [cell_min_lon, cell_min_lat],
            [cell_max_lon, cell_min_lat],
            [cell_max_lon, cell_max_lat],
            [cell_min_lon, cell_max_lat],
            [cell_min_lon, cell_min_lat],
        ]
        
        print(f"\nGeoJSON Sample Cell: {geojson_coords[0]} (Lon, Lat)")
        
    else:
        print("Zone not found")

if __name__ == "__main__":
    debug_preview_logic()
    debug_simulation_logic()
