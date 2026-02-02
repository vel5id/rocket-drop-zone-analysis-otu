"""
Reproduce server logic for grid generation.
Simulates the import struggle and fallback mechanism.
"""
import sys
import os
import numpy as np
from typing import List, Tuple

# Add current dir to path
sys.path.insert(0, os.path.abspath("."))

def reproduction_test():
    print("🔬 STARTING REPRODUCTION TEST")
    
    # 1. Create a dummy polygon (Ellipse)
    # Using small ellipse for readable output
    center_lat, center_lon = 47.333, 66.775
    # Simple diamond
    polygon = [
        (center_lat + 0.1, center_lon),
        (center_lat, center_lon + 0.1),
        (center_lat - 0.1, center_lon),
        (center_lat, center_lon - 0.1),
        (center_lat + 0.1, center_lon) # Close
    ]
    polygons = [polygon]
    cell_size_km = 5.0 # Large cells for speed
    
    print(f"\n1. Testing 'server_pipeline.grid_generator.generate_grid_safe'...")
    try:
        from server_pipeline.grid_generator import generate_grid_safe
        
        # This calls the function that has our debug prints
        grid = generate_grid_safe(polygons, cell_size_km=cell_size_km)
        
        print(f"\n✅ Result: Generated {len(grid)} cells")
        
        # Check coordinates range to see if it matches polygon or bbox
        lats = [c.center_lat for c in grid]
        lons = [c.center_lon for c in grid]
        if lats:
            print(f"   Lat range: {min(lats):.4f} - {max(lats):.4f}")
            print(f"   Lon range: {min(lons):.4f} - {max(lons):.4f}")
            
    except Exception as e:
        print(f"❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduction_test()
