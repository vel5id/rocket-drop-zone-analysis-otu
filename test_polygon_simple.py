"""
Simple test to verify point-in-polygon works correctly.
"""

def point_in_polygon(lat: float, lon: float, polygon):
    """Ray casting algorithm."""
    inside = False
    n = len(polygon)
    p1_lat, p1_lon = polygon[0]
    
    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        
        if lon > min(p1_lon, p2_lon):
            if lon <= max(p1_lon, p2_lon):
                if lat <= max(p1_lat, p2_lat):
                    if p1_lon != p2_lon:
                        lat_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                    if p1_lat == p2_lat or lat <= lat_inters:
                        inside = not inside
        
        p1_lat, p1_lon = p2_lat, p2_lon
    
    return inside

# Simple square polygon (lat, lon)
square = [
    (47.0, 66.0),  # SW
    (48.0, 66.0),  # NW
    (48.0, 67.0),  # NE
    (47.0, 67.0),  # SE
]

print("Testing point-in-polygon:")
print(f"  Center (47.5, 66.5): {point_in_polygon(47.5, 66.5, square)} (should be True)")
print(f"  Outside (46.5, 66.5): {point_in_polygon(46.5, 66.5, square)} (should be False)")
print(f"  Outside (47.5, 68.0): {point_in_polygon(47.5, 68.0, square)} (should be False)")
print(f"  Edge (47.0, 66.0): {point_in_polygon(47.0, 66.0, square)} (should be True)")
