
import sys
import os
import json
from dataclasses import dataclass

# Add parent dir to path to allow imports
sys.path.insert(0, os.path.abspath("."))

from server_pipeline.grid_generator import create_ellipse_polygons
from server_pipeline.geojson import grid_to_geojson
from grid.polygon_grid import GridCell

def run_inspection():
    # 1. Define sample ellipse parameters
    primary_ellipse = {
        "center_lat": 47.0,
        "center_lon": 67.0,
        "semi_major_km": 10.0,
        "semi_minor_km": 5.0,
        "angle_deg": 30.0
    }

    # 2. Generate 'polygons' variable (Line 225 in simulation.py)
    print("--- GENERATING POLYGONS ---")
    polygons = create_ellipse_polygons(primary_ellipse)
    
    # Check structure
    print(f"Type of polygons: {type(polygons)}")
    print(f"Number of polygons: {len(polygons)}")
    print(f"Type of first polygon: {type(polygons[0])}")
    print(f"Number of points in first polygon: {len(polygons[0])}")
    print("\nSample points (First 3):")
    for p in polygons[0][:3]:
        print(f"  {p}")
    
    # 3. Create dummy GridCells (simulating result of generate_grid)
    grid_cells = [
        GridCell(
            min_lat=46.95, max_lat=47.05,
            min_lon=66.95, max_lon=67.05,
            center_lat=47.0, center_lon=67.0
        ),
         GridCell(
            min_lat=47.05, max_lat=47.15,
            min_lon=67.05, max_lon=67.15,
            center_lat=47.1, center_lon=67.1
        )
    ]
    
    # 4. Generate 'grid_geojson' (Line 309 in simulation.py)
    # Note: adding dummy OTU values as simulation.py does in Step 4.5 via mapping
    # But strictly speaking, grid_to_geojson handles cells without OTU too.
    
    # Let's verify what simulation.py passes. It passes 'grid_cells' which might have attributes added dynamically.
    # Let's add attributes to the first cell to simulate processed data.
    grid_cells[0].q_otu = 0.85
    grid_cells[0].q_vi = 0.5
    grid_cells[0].missing_data = []
    
    print("\n--- GENERATING GRID GEOJSON ---")
    grid_geojson = grid_to_geojson(grid_cells)
    
    print(f"Type of grid_geojson: {type(grid_geojson)}")
    print(f"GeoJSON Type: {grid_geojson.get('type')}")
    print(f"Number of features: {len(grid_geojson['features'])}")
    
    print("\nSample Feature 1 (With OTU data):")
    print(json.dumps(grid_geojson['features'][0], indent=2))
    
    print("\nSample Feature 2 (Without OTU data):")
    print(json.dumps(grid_geojson['features'][1], indent=2))

if __name__ == "__main__":
    run_inspection()
