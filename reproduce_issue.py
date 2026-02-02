
import sys
import os
import numpy as np
import math

# Mock imports/functions to isolate logic

def create_ellipse_polygon(ellipse, scale=1.0, num_points=64):
    """Copied from grid/polygon_grid.py"""
    clat = ellipse["center_lat"]
    clon = ellipse["center_lon"]
    a_km = ellipse["semi_major_km"] * scale
    b_km = ellipse["semi_minor_km"] * scale
    angle_north = ellipse.get("angle_deg", 0)
    
    # Convert km to degrees
    lat_rad = math.radians(clat)
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    # Angle from North to math angle (East=0, CCW)
    math_angle = math.radians(90 - angle_north)
    
    points = []
    for t in np.linspace(0, 2*np.pi, num_points):
        # Ellipse in local coords
        x = a_km * deg_per_km_lon * np.cos(t)
        y = b_km * deg_per_km_lat * np.sin(t)
        
        # Rotate
        xr = x * np.cos(math_angle) - y * np.sin(math_angle)
        yr = x * np.sin(math_angle) + y * np.cos(math_angle)
        
        points.append((clat + yr, clon + xr))
    
    return points

def point_in_polygon(lat, lon, polygon):
    """Copied from grid_generator.py (fallback)"""
    inside = False
    n = len(polygon)
    p1_lat, p1_lon = polygon[0]
    
    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        
        # Ray casting along longitude axis
        if lon > min(p1_lon, p2_lon):
            if lon <= max(p1_lon, p2_lon):
                if lat <= max(p1_lat, p2_lat):
                    if p1_lon != p2_lon:
                        lat_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                    # Potential BUG: xinters (lat_inters) variable scope
                    # In python, lat_inters leaks, but if p1_lon == p2_lon, it might use old value?
                    # The logic is: if p1_lon != p2_lon, calculate.
                    # if p1_lat == p2_lat OR lat <= lat_inters.
                    
                    # If p1_lon == p2_lon:
                    # lat_inters is NOT calculated.
                    # Then we check (p1_lat == p2_lat) OR (lat <= lat_inters).
                    # If p1_lat != p2_lat AND lat_inters is undefined -> UnboundLocalError!
                    
                    # FIX ATTEMPT LOGIC simulation:
                    # In original code:
                    # if p1_lon != p2_lon:
                    #    lat_inters = ...
                    # if p1_lat == p2_lat or lat <= lat_inters:
                    
                    # If this runs in Python and p1_lon == p2_lon (vertical segment),
                    # lat_inters is not assigned.
                    # If it was assigned in previous loop iteration, it uses THAT value.
                    # correctness -> catastrophic failure.
                    
                    # Let's verify this behavior in this script.
                    try:
                         if p1_lon != p2_lon:
                             lat_inters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                         
                         if p1_lat == p2_lat or lat <= lat_inters:
                             inside = not inside
                    except UnboundLocalError:
                        print(f"CRASH: UnboundLocalError at i={i}")
                        return False
            
        p1_lat, p1_lon = p2_lat, p2_lon
    
    return inside

def run_test():
    # Define an ellipse
    ellipse = {
        "center_lat": 10.0,
        "center_lon": 10.0,
        "semi_major_km": 50.0,
        "semi_minor_km": 10.0,
        "angle_deg": 45.0
    }
    
    poly = create_ellipse_polygon(ellipse)
    
    # Define a bounding box grid
    lat_min, lat_max = 9.0, 11.0
    lon_min, lon_max = 9.0, 11.0
    
    lats = np.linspace(lat_min, lat_max, 40)
    lons = np.linspace(lon_min, lon_max, 40)
    
    print("Generating grid...")
    grid_str = ""
    count_inside = 0
    total = 0
    
    for lat in lats:
        row_str = ""
        for lon in lons:
            is_in = point_in_polygon(lat, lon, poly)
            if is_in:
                row_str += "X"
                count_inside += 1
            else:
                row_str += "."
            total += 1
        grid_str = row_str + "\n" + grid_str # Lat goes up, so prepend lines
        
    print(grid_str)
    print(f"Inside: {count_inside}/{total}")

if __name__ == "__main__":
    run_test()
