"""
Test script to debug grid generation with ellipse from frontend.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server_pipeline.grid_generator import create_ellipse_polygons, generate_grid_safe
from server_pipeline.ellipse import compute_ellipse_safe

# Simulate ellipses from frontend (typical values)
primary_ellipse = {
    "center_lat": 47.5,
    "center_lon": 66.0,
    "semi_major_km": 30.0,
    "semi_minor_km": 15.0,
    "angle_deg": 45.0,
}

fragment_ellipse = {
    "center_lat": 47.6,
    "center_lon": 66.1,
    "semi_major_km": 20.0,
    "semi_minor_km": 10.0,
    "angle_deg": 50.0,
}

print("="*70)
print("GRID GENERATION DEBUG")
print("="*70)

print("\n1. Creating ellipse polygons...")
polygons = create_ellipse_polygons(primary_ellipse, fragment_ellipse)
print(f"   Created {len(polygons)} polygons")
for i, poly in enumerate(polygons):
    print(f"   Polygon {i+1}: {len(poly)} vertices")
    # Show first few vertices
    print(f"     First vertex: {poly[0]}")
    print(f"     Last vertex: {poly[-1]}")

print("\n2. Generating grid (1km cells)...")
try:
    grid = generate_grid_safe(polygons, cell_size_km=1.0)
    print(f"   ✅ Generated {len(grid)} cells")
    
    if grid:
        print(f"\n3. Grid statistics:")
        lats = [cell.center_lat for cell in grid]
        lons = [cell.center_lon for cell in grid]
        print(f"   Latitude range: {min(lats):.4f} to {max(lats):.4f}")
        print(f"   Longitude range: {min(lons):.4f} to {max(lons):.4f}")
        
        # Check if grid is rectangular (bad) or elliptical (good)
        lat_span = max(lats) - min(lats)
        lon_span = max(lons) - min(lons)
        aspect_ratio = lat_span / lon_span if lon_span > 0 else 0
        
        print(f"   Aspect ratio: {aspect_ratio:.2f}")
        if abs(aspect_ratio - 1.0) < 0.1:
            print("   ⚠️  WARNING: Grid is nearly square (might be rectangular artifact)")
        else:
            print("   ✅ Grid has elliptical shape")
        
        # Sample a few cells
        print(f"\n4. Sample cells:")
        for i in [0, len(grid)//2, -1]:
            cell = grid[i]
            print(f"   Cell {i}: ({cell.center_lat:.4f}, {cell.center_lon:.4f})")
    
except Exception as e:
    print(f"   ❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)

print("""
If grid is rectangular:
- Check if matplotlib is installed
- Check if point_in_polygon is working correctly
- Verify polygon coordinates are (lat, lon) not (lon, lat)

If grid is elliptical:
- Grid generation is working correctly
- Problem might be in OTU calculation or data fetching
""")
