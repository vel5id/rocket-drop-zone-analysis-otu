"""
Test script to verify grid generation produces ellipse shape, not rectangle.
"""
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from server_pipeline.grid_generator import generate_grid_safe
from grid.polygon_grid import create_ellipse_polygon
import json

# Test ellipse (YU-24 Zone 15)
ellipse = {
    "center_lat": 47.333,
    "center_lon": 66.775,
    "semi_major_km": 27.0,
    "semi_minor_km": 18.0,
    "angle_deg": 65.0
}

print("Creating ellipse polygon...")
polygon = create_ellipse_polygon(ellipse)
print(f"Polygon has {len(polygon)} points")

print("\nGenerating grid...")
# Use generate_grid_safe instead of generate_grid_optimized directly
grid_cells = generate_grid_safe([polygon], cell_size_km=1.0)

print(f"\n✅ Generated {len(grid_cells)} cells")

# Check if grid forms ellipse or rectangle
lats = [cell.center_lat for cell in grid_cells]
lons = [cell.center_lon for cell in grid_cells]

min_lat, max_lat = min(lats), max(lats)
min_lon, max_lon = min(lons), max(lons)

# Calculate bounding box area
bbox_width = max_lon - min_lon
bbox_height = max_lat - min_lat

print(f"\nBounding Box:")
print(f"  Lat range: {min_lat:.3f} to {max_lat:.3f} (height: {bbox_height:.3f}°)")
print(f"  Lon range: {min_lon:.3f} to {max_lon:.3f} (width: {bbox_width:.3f}°)")

# Estimate expected cells for rectangle vs ellipse
bbox_cells = int((bbox_height / (1/111.0)) * (bbox_width / (1/(111.0 * 0.7))))
ellipse_cells_approx = int(bbox_cells * 0.785)  # π/4 ≈ 0.785

print(f"\nExpected cells:")
print(f"  Rectangle (bbox): ~{bbox_cells}")
print(f"  Ellipse (π/4 * bbox): ~{ellipse_cells_approx}")
print(f"  Actual: {len(grid_cells)}")

# Verdict
ratio = len(grid_cells) / bbox_cells if bbox_cells > 0 else 0
print(f"\nFill ratio: {ratio:.2%}")

if ratio > 0.95:
    print("❌ FAIL: Grid is RECTANGULAR (ratio > 95%)")
elif ratio < 0.85:
    print("✅ PASS: Grid is ELLIPTICAL (ratio < 85%)")
else:
    print("⚠️  UNCERTAIN: Ratio is borderline")

# Save grid as GeoJSON for visual inspection
from server_pipeline.geojson import grid_to_geojson

grid_geojson = grid_to_geojson(grid_cells)
with open("test_grid_output.geojson", "w") as f:
    json.dump(grid_geojson, f, indent=2)

print("\n📁 Saved grid to test_grid_output.geojson")
print("   Open in geojson.io to verify shape")
