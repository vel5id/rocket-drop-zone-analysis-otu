"""Generate grid cells inside ellipse polygons."""
from __future__ import annotations

import math
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple

try:
    from matplotlib.path import Path
    HAS_MATPLOTLIB = True
except ImportError as e:
    print(f"[GRID-WARNING] Matplotlib import failed: {e}")
    HAS_MATPLOTLIB = False

import json

def dump_debug_polygons(polygons: List[List[Tuple[float, float]]]):
    """Dump polygons to GeoJSON for debug."""
    features = []
    for i, poly in enumerate(polygons):
        # Convert (lat, lon) to (lon, lat)
        coords = [[lon, lat] for lat, lon in poly]
        # Close loop
        if coords[0] != coords[-1]:
            coords.append(coords[0])
            
        features.append({
            "type": "Feature",
            "properties": {"id": f"poly_{i}"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        })
    
    geojson = {"type": "FeatureCollection", "features": features}
    try:
        with open("server_debug_polygons.geojson", "w") as f:
            json.dump(geojson, f)
        print("[GRID-DEBUG] Dumped server_debug_polygons.geojson")
    except Exception as e:
        print(f"[GRID-DEBUG] Failed to dump polygons: {e}")



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
    """Create ellipse polygon as list of (lat, lon) points."""
    clat = ellipse["center_lat"]
    clon = ellipse["center_lon"]
    a_km = ellipse["semi_major_km"] * scale
    b_km = ellipse["semi_minor_km"] * scale
    angle_north = ellipse.get("angle_deg", 0)
    
    # Convert km to degrees coefficients
    lat_rad = math.radians(clat)
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    # Angle from North to math angle (East=0, CCW)
    math_angle = math.radians(90 - angle_north)
    
    points = []
    for t in np.linspace(0, 2*np.pi, num_points):
        # Ellipse in local coords (km)
        x_km = a_km * np.cos(t)
        y_km = b_km * np.sin(t)
        
        # Rotate in km space
        xr_km = x_km * np.cos(math_angle) - y_km * np.sin(math_angle)
        yr_km = x_km * np.sin(math_angle) + y_km * np.cos(math_angle)
        
        # Convert to degrees
        dlat = yr_km * deg_per_km_lat
        dlon = xr_km * deg_per_km_lon
        
        points.append((clat + dlat, clon + dlon))
    
    return points


def point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """Check if point is inside polygon using ray casting algorithm (Fallback)."""
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
    Generate grid cells inside polygons using vectorized operations if available.
    """
    if not polygons:
        return []

    # Proactive debug dump
    dump_debug_polygons(polygons)

    # Get merged bounding box
    if len(polygons) == 1:
        min_lat, max_lat, min_lon, max_lon = get_polygon_bounds(polygons[0])
    else:
        min_lat, max_lat, min_lon, max_lon = merge_polygons(polygons[0], polygons[1])

    # Grid params
    center_lat = (min_lat + max_lat) / 2
    lat_rad = math.radians(center_lat)
    
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    cell_size_lat = cell_size_km * deg_per_km_lat
    cell_size_lon = cell_size_km * deg_per_km_lon
    
    # ---------------------------------------------------------
    # OPTIMIZED VECTORIZED PATH (Matplotlib)
    # ---------------------------------------------------------
    if HAS_MATPLOTLIB:
        # Convert polygons from (lat, lon) to (x, y) = (lon, lat) for matplotlib
        # matplotlib.path.Path expects (x, y) coordinates
        paths = [Path([(lon, lat) for lat, lon in p]) for p in polygons]
        
        # Determine strict grid steps
        lat_steps = int(np.ceil((max_lat - min_lat) / cell_size_lat))
        lon_steps = int(np.ceil((max_lon - min_lon) / cell_size_lon))
        
        # Create coordinates
        lats = np.linspace(min_lat, min_lat + lat_steps * cell_size_lat, lat_steps + 1)
        lons = np.linspace(min_lon, min_lon + lon_steps * cell_size_lon, lon_steps + 1)
        
        # We need centers of cells for point-in-polygon check
        # Centers are (lat[i] + lat[i+1])/2
        lats_c = (lats[:-1] + lats[1:]) / 2
        lons_c = (lons[:-1] + lons[1:]) / 2
        
        # Meshgrid of centers
        lon_grid_c, lat_grid_c = np.meshgrid(lons_c, lats_c)
        
        # Flatten and convert to (x, y) = (lon, lat) for matplotlib
        points_flat = np.column_stack((lon_grid_c.flatten(), lat_grid_c.flatten()))
        
        # Check containment
        inside_mask = np.zeros(len(points_flat), dtype=bool)
        for path in paths:
            # path.contains_points expects (N, 2) array in (x, y) format
            inside_mask |= path.contains_points(points_flat)
            
        valid_indices = np.where(inside_mask)[0]
        
        cells = []
        
        # Reconstruct cell bounds from center
        # HACK: Using fixed cell size from center
        d_lat = cell_size_lat
        d_lon = cell_size_lon
        
        for idx in valid_indices:
            # points_flat is now (lon, lat) format
            c_lon = points_flat[idx, 0]  # x = lon
            c_lat = points_flat[idx, 1]  # y = lat
            
            cells.append(GridCell(
                min_lat=c_lat - d_lat/2,
                max_lat=c_lat + d_lat/2,
                min_lon=c_lon - d_lon/2,
                max_lon=c_lon + d_lon/2,
                center_lat=c_lat,
                center_lon=c_lon,
            ))
            
        return cells

    # ---------------------------------------------------------
    # SLOW FALLBACK
    # ---------------------------------------------------------
    cells = []
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            cell_min_lat = lat
            cell_max_lat = lat + cell_size_lat
            cell_min_lon = lon
            cell_max_lon = lon + cell_size_lon
            
            cell_center_lat = (cell_min_lat + cell_max_lat) / 2
            cell_center_lon = (cell_min_lon + cell_max_lon) / 2
            
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
