"""
Loader for real zone polygons from shapefiles.

Loads the actual 15.SHP and 25.SHP polygon files from KARTA folder
instead of using synthetic ellipses.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any

try:
    import geopandas as gpd
    from shapely.geometry import Polygon, MultiPolygon
    HAS_GEOPANDAS = True
except ImportError:
    gpd = None
    HAS_GEOPANDAS = False

# Default paths relative to project root
DEFAULT_ZONE_15_PATH = "KARTA/bagdat/25/15.SHP"
DEFAULT_ZONE_25_PATH = "KARTA/bagdat/25/25.SHP"


def load_zone_polygon(
    shapefile_path: str,
    target_crs: str = "EPSG:4326",
) -> Optional[List[Tuple[float, float]]]:
    """
    Load a polygon from shapefile and convert to lat/lon coordinates.
    
    Args:
        shapefile_path: Path to .SHP file
        target_crs: Target coordinate reference system (default WGS84)
        
    Returns:
        List of (lat, lon) tuples forming the polygon boundary,
        or None if loading fails
    """
    if not HAS_GEOPANDAS:
        print(f"  [WARN] geopandas not available, cannot load {shapefile_path}")
        return None
    
    if not os.path.exists(shapefile_path):
        print(f"  [WARN] Shapefile not found: {shapefile_path}")
        return None
    
    try:
        gdf = gpd.read_file(shapefile_path)
        
        # Reproject to WGS84 if needed
        if gdf.crs and gdf.crs.to_string() != target_crs:
            gdf = gdf.to_crs(target_crs)
        
        # Get the first geometry (assuming single polygon per file)
        geom = gdf.geometry.iloc[0]
        
        # Handle MultiPolygon - take the largest
        if isinstance(geom, MultiPolygon):
            geom = max(geom.geoms, key=lambda g: g.area)
        
        # Extract exterior coordinates
        coords = list(geom.exterior.coords)
        
        # Convert to (lat, lon) format - shapefiles are typically (lon, lat)
        points = [(lat, lon) for lon, lat in coords]
        
        print(f"  [OK] Loaded polygon with {len(points)} vertices from {Path(shapefile_path).name}")
        return points
        
    except Exception as e:
        print(f"  [ERROR] Failed to load {shapefile_path}: {e}")
        return None


def load_yu24_zones(
    project_root: str = ".",
) -> Tuple[Optional[List[Tuple[float, float]]], Optional[List[Tuple[float, float]]]]:
    """
    Load both Zone 15 and Zone 25 polygons for Ю-24.
    
    Args:
        project_root: Path to project root directory
        
    Returns:
        Tuple of (zone_15_polygon, zone_25_polygon)
    """
    zone_15_path = os.path.join(project_root, DEFAULT_ZONE_15_PATH)
    zone_25_path = os.path.join(project_root, DEFAULT_ZONE_25_PATH)
    
    print("[Loading Ю-24 Zone Polygons from Shapefiles]")
    
    zone_15 = load_zone_polygon(zone_15_path)
    zone_25 = load_zone_polygon(zone_25_path)
    
    return zone_15, zone_25


def polygon_to_ellipse_approx(
    polygon: List[Tuple[float, float]],
) -> Dict[str, float]:
    """
    Approximate a polygon as an ellipse for compatibility with existing code.
    
    Uses PCA-like approach to find major/minor axes.
    
    Args:
        polygon: List of (lat, lon) points
        
    Returns:
        Dict with center_lat, center_lon, semi_major_km, semi_minor_km, angle_deg
    """
    import numpy as np
    
    lats = np.array([p[0] for p in polygon])
    lons = np.array([p[1] for p in polygon])
    
    # Center
    center_lat = np.mean(lats)
    center_lon = np.mean(lons)
    
    # Convert to km relative to center
    km_per_deg_lat = 111.0
    km_per_deg_lon = 111.0 * np.cos(np.radians(center_lat))
    
    x_km = (lons - center_lon) * km_per_deg_lon
    y_km = (lats - center_lat) * km_per_deg_lat
    
    # Covariance matrix
    cov = np.cov(x_km, y_km)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    
    # Sort by eigenvalue (largest first)
    idx = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    
    # Semi-axes (use 2-sigma for approximate coverage)
    semi_major_km = 2 * np.sqrt(eigenvalues[0])
    semi_minor_km = 2 * np.sqrt(eigenvalues[1])
    
    # Angle from major eigenvector
    angle_rad = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])
    angle_deg = 90 - np.degrees(angle_rad)  # Convert to North-based
    
    return {
        "center_lat": float(center_lat),
        "center_lon": float(center_lon),
        "semi_major_km": float(semi_major_km),
        "semi_minor_km": float(semi_minor_km),
        "angle_deg": float(angle_deg),
    }


def get_polygon_bounds(
    polygon: List[Tuple[float, float]],
) -> Tuple[float, float, float, float]:
    """Get bounding box of polygon as (min_lat, min_lon, max_lat, max_lon)."""
    lats = [p[0] for p in polygon]
    lons = [p[1] for p in polygon]
    return min(lats), min(lons), max(lats), max(lons)
