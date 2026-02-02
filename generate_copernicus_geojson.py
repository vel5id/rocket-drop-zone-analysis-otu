"""
Generate a properly formatted GeoJSON file for visualization in Copernicus Browser or geojson.io
"""
import json
import math

def create_ellipse_geojson(center_lat, center_lon, semi_major_km, semi_minor_km, angle_deg, name="Ellipse", num_points=64):
    """Create a GeoJSON Feature for an ellipse."""
    lat_rad = math.radians(center_lat)
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    math_angle = math.radians(90 - angle_deg)
    
    coordinates = []
    for i in range(num_points):
        t = 2 * math.pi * i / num_points
        x = semi_major_km * deg_per_km_lon * math.cos(t)
        y = semi_minor_km * deg_per_km_lat * math.sin(t)
        
        xr = x * math.cos(math_angle) - y * math.sin(math_angle)
        yr = x * math.sin(math_angle) + y * math.cos(math_angle)
        
        coordinates.append([center_lon + xr, center_lat + yr])
    
    # Close polygon
    coordinates.append(coordinates[0])
    
    return {
        "type": "Feature",
        "properties": {
            "name": name,
            "center_lat": center_lat,
            "center_lon": center_lon,
            "semi_major_km": semi_major_km,
            "semi_minor_km": semi_minor_km,
            "angle_deg": angle_deg,
            "stroke": "#ff0000",
            "stroke-width": 2,
            "stroke-opacity": 1,
            "fill": "#ff0000",
            "fill-opacity": 0.1
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates]
        }
    }

# Create ellipses for YU-24 zones (from config/zones.py)
primary_zone = create_ellipse_geojson(
    center_lat=47.333,
    center_lon=66.775,
    semi_major_km=27.0,
    semi_minor_km=18.0,
    angle_deg=65.0,
    name="YU-24 Zone 15 (Primary)"
)

fragment_zone = create_ellipse_geojson(
    center_lat=47.233,
    center_lon=66.383,
    semi_major_km=60.0,
    semi_minor_km=30.0,
    angle_deg=65.0,
    name="YU-24 Zone 25 (Fragment)"
)

# Create FeatureCollection
geojson = {
    "type": "FeatureCollection",
    "features": [primary_zone, fragment_zone]
}

# Save to file
output_file = "ellipse_boundaries_copernicus.geojson"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(geojson, f, indent=2, ensure_ascii=False)

print(f"✅ GeoJSON created: {output_file}")
print(f"📍 Primary Zone: {primary_zone['properties']['name']}")
print(f"📍 Fragment Zone: {fragment_zone['properties']['name']}")
print("\nYou can:")
print("1. Open in Copernicus Browser: https://browser.dataspace.copernicus.eu/")
print("2. Visualize at: https://geojson.io/")
print("3. Load in QGIS or any GIS software")
