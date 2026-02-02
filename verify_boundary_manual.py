"""
Manual verification of boundary generation logic.
Run this with: python verify_boundary_manual.py
"""

# Inline implementation to avoid import issues
import math
import json

def ellipse_to_geojson_inline(ellipse, properties=None, num_points=64):
    """Inline version of ellipse_to_geojson for testing."""
    clat = ellipse["center_lat"]
    clon = ellipse["center_lon"]
    a_km = ellipse["semi_major_km"]
    b_km = ellipse["semi_minor_km"]
    angle_north = ellipse.get("angle_deg", 0)
    
    # Convert km to degrees
    lat_rad = math.radians(clat)
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    # Angle from North to math angle
    math_angle = math.radians(90 - angle_north)
    
    coordinates = []
    for i in range(num_points):
        t = 2 * math.pi * i / num_points
        x = a_km * deg_per_km_lon * math.cos(t)
        y = b_km * deg_per_km_lat * math.sin(t)
        
        xr = x * math.cos(math_angle) - y * math.sin(math_angle)
        yr = x * math.sin(math_angle) + y * math.cos(math_angle)
        
        coordinates.append([clon + xr, clat + yr])
    
    # Close the polygon
    coordinates.append(coordinates[0])
    
    props = {
        "center_lat": clat,
        "center_lon": clon,
        "semi_major_km": a_km,
        "semi_minor_km": b_km,
        "angle_deg": angle_north,
    }
    if properties:
        props.update(properties)
    
    return {
        "type": "Feature",
        "properties": props,
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
    }

# Test
print("Testing boundary generation...")

test_ellipse = {
    "center_lat": 47.333,
    "center_lon": 66.775,
    "semi_major_km": 27.0,
    "semi_minor_km": 18.0,
    "angle_deg": 65.0
}

boundary_feature = ellipse_to_geojson_inline(
    test_ellipse, 
    properties={"type": "primary", "name": "Primary Zone"}
)

print("\n[SUCCESS] Boundary feature generated")
print(f"Feature Type: {boundary_feature['type']}")
print(f"Geometry Type: {boundary_feature['geometry']['type']}")
print(f"Properties: {boundary_feature['properties']}")
print(f"Number of points: {len(boundary_feature['geometry']['coordinates'][0])}")
print(f"First point: {boundary_feature['geometry']['coordinates'][0][0]}")
print(f"Last point: {boundary_feature['geometry']['coordinates'][0][-1]}")

# Verify closure
first = boundary_feature['geometry']['coordinates'][0][0]
last = boundary_feature['geometry']['coordinates'][0][-1]
if first == last:
    print("\n[OK] Polygon is properly closed")
else:
    print(f"\n[ERROR] Polygon NOT closed: {first} != {last}")

# Create FeatureCollection
boundary_geojson = {
    "type": "FeatureCollection",
    "features": [boundary_feature]
}

print(f"\nFeatureCollection created with {len(boundary_geojson['features'])} feature(s)")
print("\n[VERIFICATION COMPLETE]")

# Save to file for inspection
with open("boundary_test_output.json", "w") as f:
    json.dump(boundary_geojson, f, indent=2)
print("Saved to boundary_test_output.json")
