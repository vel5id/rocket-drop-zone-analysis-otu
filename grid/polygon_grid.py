"""Generate grid cells inside ellipse polygons."""
from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class GridCell:
    """Represents a 1x1 km grid cell."""
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    center_lat: float
    center_lon: float


def create_ellipse_polygon(ellipse: dict, scale: float = 1.0, num_points: int = 64) -> List[Tuple[float, float]]:
    """
    Create ellipse polygon as list of (lat, lon) points.
    
    Args:
        ellipse: Dict with center_lat, center_lon, semi_major_km, semi_minor_km, angle_deg
        scale: Scale factor (1.0 = full size, 0.85 = 15% smaller)
        num_points: Number of points for polygon approximation
    
    Returns:
        List of (lat, lon) tuples representing polygon vertices
    """
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


def point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """Check if point is inside polygon using ray casting algorithm."""
    inside = False
    n = len(polygon)
    p1_lat, p1_lon = polygon[0]
    
    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        
        if lon > min(p1_lon, p2_lon):
            if lon <= max(p1_lon, p2_lon):
                if lat <= max(p1_lat, p2_lat):
                    if p1_lon != p2_lon:
                        xinters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                    if p1_lat == p2_lat or lat <= xinters:
                        inside = not inside
        
        p1_lat, p1_lon = p2_lat, p2_lon
    
    return inside


def get_polygon_bounds(polygon: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    """Get bounding box of polygon."""
    lats = [p[0] for p in polygon]
    lons = [p[1] for p in polygon]
    return min(lats), max(lats), min(lons), max(lons)


def merge_polygons(polygon1: List[Tuple[float, float]], polygon2: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    """Get bounding box that contains both polygons."""
    min_lat1, max_lat1, min_lon1, max_lon1 = get_polygon_bounds(polygon1)
    min_lat2, max_lat2, min_lon2, max_lon2 = get_polygon_bounds(polygon2)
    
    return (
        min(min_lat1, min_lat2),
        max(max_lat1, max_lat2),
        min(min_lon1, min_lon2),
        max(max_lon1, max_lon2),
    )


def generate_grid_in_polygons(
    polygons: List[List[Tuple[float, float]]],
    cell_size_km: float = 1.0,
) -> List[GridCell]:
    """
    Generate grid cells that fall inside given polygons.
    
    Args:
        polygons: List of polygon vertex lists
        cell_size_km: Grid cell size in km
    
    Returns:
        List of GridCell objects that intersect with polygons
    """
    if not polygons:
        return []
    
    # Get merged bounding box
    if len(polygons) == 1:
        min_lat, max_lat, min_lon, max_lon = get_polygon_bounds(polygons[0])
    else:
        min_lat, max_lat, min_lon, max_lon = merge_polygons(polygons[0], polygons[1])
    
    # Calculate grid parameters
    center_lat = (min_lat + max_lat) / 2
    lat_rad = math.radians(center_lat)
    
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    cell_size_lat = cell_size_km * deg_per_km_lat
    cell_size_lon = cell_size_km * deg_per_km_lon
    
    # Generate grid cells
    cells = []
    
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            # Cell bounds
            cell_min_lat = lat
            cell_max_lat = lat + cell_size_lat
            cell_min_lon = lon
            cell_max_lon = lon + cell_size_lon
            
            # Cell center
            cell_center_lat = (cell_min_lat + cell_max_lat) / 2
            cell_center_lon = (cell_min_lon + cell_max_lon) / 2
            
            # Check if cell center is inside any polygon
            inside_any = False
            for polygon in polygons:
                if point_in_polygon(cell_center_lat, cell_center_lon, polygon):
                    inside_any = True
                    break
            
            if inside_any:
                cells.append(GridCell(
                    min_lat=cell_min_lat,
                    max_lat=cell_max_lat,
                    min_lon=cell_min_lon,
                    max_lon=cell_max_lon,
                    center_lat=cell_center_lat,
                    center_lon=cell_center_lon,
                ))
            
            lon += cell_size_lon
        lat += cell_size_lat
    
    return cells
