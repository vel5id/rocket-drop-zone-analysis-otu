"""
Test script to verify grid generation and CSV export with ellipse polygons.
Simulates the full pipeline without GEE data fetching.
"""
import sys
import os
import json
import csv
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server_pipeline.grid_generator import create_ellipse_polygons, generate_grid_safe
from grid.polygon_grid import GridCell

print("="*70)
print("GRID GENERATION & CSV EXPORT TEST")
print("="*70)

# Simulate ellipses from frontend (typical values from Monte Carlo)
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

print("\n1. Creating ellipse polygons...")
print(f"   Primary: {primary_ellipse['semi_major_km']}x{primary_ellipse['semi_minor_km']} km @ {primary_ellipse['angle_deg']}°")
print(f"   Fragment: {fragment_ellipse['semi_major_km']}x{fragment_ellipse['semi_minor_km']} km @ {fragment_ellipse['angle_deg']}°")

polygons = create_ellipse_polygons(primary_ellipse, fragment_ellipse)
print(f"   ✅ Created {len(polygons)} polygons")

print("\n2. Generating grid (1km cells)...")
grid = generate_grid_safe(polygons, cell_size_km=1.0, max_cells=5000)
print(f"   ✅ Generated {len(grid)} cells")

if not grid:
    print("   ❌ ERROR: No cells generated!")
    sys.exit(1)

print(f"\n3. Grid statistics:")
lats = [cell.center_lat for cell in grid]
lons = [cell.center_lon for cell in grid]
print(f"   Latitude range: {min(lats):.4f}° to {max(lats):.4f}°")
print(f"   Longitude range: {min(lons):.4f}° to {max(lons):.4f}°")
print(f"   Lat span: {max(lats) - min(lats):.4f}° ({(max(lats) - min(lats)) * 111:.1f} km)")
print(f"   Lon span: {max(lons) - min(lons):.4f}° ({(max(lons) - min(lons)) * 111:.1f} km)")

# Check if grid is rectangular (bad) or elliptical (good)
lat_span = max(lats) - min(lats)
lon_span = max(lons) - min(lons)
aspect_ratio = lat_span / lon_span if lon_span > 0 else 0

print(f"   Aspect ratio: {aspect_ratio:.2f}")
if abs(aspect_ratio - 1.0) < 0.1:
    print("   ⚠️  WARNING: Grid is nearly square (might be rectangular artifact)")
else:
    print("   ✅ Grid has elliptical shape")

print(f"\n4. Simulating OTU data (mock values)...")
# Add mock OTU data to cells
import random
for i, cell in enumerate(grid):
    # Simulate some missing data (10% chance)
    has_missing_ndvi = random.random() < 0.1
    
    cell.id = f"cell_{i+1}"
    cell.q_vi = 0.0 if has_missing_ndvi else random.uniform(0.1, 0.8)
    cell.q_si = random.uniform(0.3, 0.9)
    cell.q_bi = random.uniform(0.2, 0.9)
    cell.q_relief = random.uniform(0.5, 1.0)
    cell.q_otu = (cell.q_vi + cell.q_si + cell.q_bi + cell.q_relief) / 4
    cell.is_processed = True
    cell.missing_data = ["ndvi"] if has_missing_ndvi else []

missing_count = sum(1 for c in grid if "ndvi" in c.missing_data)
print(f"   ✅ Added mock data to {len(grid)} cells")
print(f"   Missing NDVI: {missing_count} cells ({missing_count/len(grid)*100:.1f}%)")

print(f"\n5. Creating GeoJSON...")
# Convert to GeoJSON format
features = []
for cell in grid:
    coords = [
        [cell.min_lon, cell.min_lat],
        [cell.max_lon, cell.min_lat],
        [cell.max_lon, cell.max_lat],
        [cell.min_lon, cell.max_lat],
        [cell.min_lon, cell.min_lat],
    ]
    
    feature = {
        "type": "Feature",
        "properties": {
            "id": cell.id,
            "q_vi": cell.q_vi,
            "q_si": cell.q_si,
            "q_bi": cell.q_bi,
            "q_relief": cell.q_relief,
            "q_otu": cell.q_otu,
            "is_processed": cell.is_processed,
            "missing_data": cell.missing_data,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [coords]
        }
    }
    features.append(feature)

geojson = {
    "type": "FeatureCollection",
    "features": features
}

# Save GeoJSON
geojson_path = "output/otu/test_grid_ellipse.geojson"
os.makedirs(os.path.dirname(geojson_path), exist_ok=True)
with open(geojson_path, 'w') as f:
    json.dump(geojson, f, indent=2)
print(f"   ✅ Saved GeoJSON: {geojson_path}")

print(f"\n6. Creating CSV export...")
# Generate CSV (simulating frontend export)
csv_path = "output/otu/test_grid_ellipse.csv"
with open(csv_path, 'w', newline='') as f:
    writer = csv.writer(f)
    
    # Header
    writer.writerow([
        'ID',
        'Latitude',
        'Longitude',
        'NDVI (Q_Vi)',
        'Soil Strength (Q_Si)',
        'Soil Quality (Q_Bi)',
        'Relief Factor (Q_Relief)',
        'OTU Index (Q_OTU)',
        'Missing Data'
    ])
    
    # Rows
    for cell in grid:
        missing = ', '.join(cell.missing_data) if cell.missing_data else 'None'
        writer.writerow([
            cell.id,
            f"{cell.center_lat:.6f}",
            f"{cell.center_lon:.6f}",
            f"{cell.q_vi:.4f}",
            f"{cell.q_si:.4f}",
            f"{cell.q_bi:.4f}",
            f"{cell.q_relief:.4f}",
            f"{cell.q_otu:.4f}",
            missing
        ])

print(f"   ✅ Saved CSV: {csv_path}")

print(f"\n7. Verification:")
# Read back and verify
with open(csv_path, 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    
print(f"   CSV rows: {len(rows)}")
print(f"   Expected: {len(grid)}")
print(f"   Match: {'✅ YES' if len(rows) == len(grid) else '❌ NO'}")

# Check for non-zero NDVI
ndvi_values = [float(row['NDVI (Q_Vi)']) for row in rows]
non_zero_ndvi = sum(1 for v in ndvi_values if v > 0)
print(f"   Non-zero NDVI: {non_zero_ndvi}/{len(rows)} ({non_zero_ndvi/len(rows)*100:.1f}%)")

# Sample rows
print(f"\n8. Sample CSV rows:")
for i in [0, len(rows)//2, -1]:
    row = rows[i]
    print(f"   Row {i+1}: {row['ID']}")
    print(f"     Location: ({row['Latitude']}, {row['Longitude']})")
    print(f"     NDVI: {row['NDVI (Q_Vi)']}, OTU: {row['OTU Index (Q_OTU)']}")
    print(f"     Missing: {row['Missing Data']}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"✅ Grid generation: {len(grid)} cells")
print(f"✅ GeoJSON export: {geojson_path}")
print(f"✅ CSV export: {csv_path}")
print(f"✅ Grid shape: {'Elliptical' if aspect_ratio > 1.2 or aspect_ratio < 0.8 else 'Square (check!)'}")
print(f"✅ Data integrity: {non_zero_ndvi}/{len(rows)} cells with valid NDVI")
print("\nTest complete! Check the output files to verify correctness.")
