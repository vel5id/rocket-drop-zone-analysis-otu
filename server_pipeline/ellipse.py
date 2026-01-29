"""
Ellipse computation with safety limits and outlier filtering.
"""
from __future__ import annotations

import numpy as np
from typing import List, Dict, Optional, Tuple

# Safety limits
MAX_SEMI_MAJOR_KM = 500.0  # Maximum ellipse semi-major axis
MAX_SEMI_MINOR_KM = 300.0  # Maximum ellipse semi-minor axis
IQR_FACTOR = 1.5  # Factor for IQR outlier detection


def filter_outliers_iqr(
    points: List[Dict],
    factor: float = IQR_FACTOR,
) -> List[Dict]:
    """
    Remove spatial outliers using IQR (Interquartile Range) method.
    
    This is critical for fragment impacts which can have extreme outliers
    that would otherwise create giant ellipses (5000+ km).
    
    Args:
        points: List of point dicts with 'lat' and 'lon' keys
        factor: IQR multiplier (1.5 = standard, 3.0 = lenient)
    
    Returns:
        Filtered list of points
    """
    if not points or len(points) < 4:
        return points
    
    lats = np.array([p["lat"] for p in points])
    lons = np.array([p["lon"] for p in points])
    
    # Calculate IQR for latitudes
    q1_lat, q3_lat = np.percentile(lats, [25, 75])
    iqr_lat = q3_lat - q1_lat
    
    # Calculate IQR for longitudes
    q1_lon, q3_lon = np.percentile(lons, [25, 75])
    iqr_lon = q3_lon - q1_lon
    
    # Define bounds
    lat_lower = q1_lat - factor * iqr_lat
    lat_upper = q3_lat + factor * iqr_lat
    lon_lower = q1_lon - factor * iqr_lon
    lon_upper = q3_lon + factor * iqr_lon
    
    # Filter points
    filtered = []
    for p in points:
        if (lat_lower <= p["lat"] <= lat_upper and 
            lon_lower <= p["lon"] <= lon_upper):
            filtered.append(p)
    
    removed = len(points) - len(filtered)
    if removed > 0:
        print(f"    [FILTER] Removed {removed} outlier points ({removed/len(points)*100:.1f}%)")
    
    return filtered if filtered else points  # Return original if all filtered


def clamp_ellipse(
    ellipse: Dict,
    max_semi_major: float = MAX_SEMI_MAJOR_KM,
    max_semi_minor: float = MAX_SEMI_MINOR_KM,
) -> Dict:
    """
    Clamp ellipse axes to reasonable size.
    
    This prevents giant ellipses from crashing the grid generator.
    """
    if not ellipse:
        return ellipse
    
    original_major = ellipse["semi_major_km"]
    original_minor = ellipse["semi_minor_km"]
    
    # Clamp major axis
    if ellipse["semi_major_km"] > max_semi_major:
        scale = max_semi_major / ellipse["semi_major_km"]
        ellipse["semi_major_km"] = max_semi_major
        ellipse["semi_minor_km"] *= scale
        print(f"    [CLAMP] Ellipse clamped: {original_major:.1f}x{original_minor:.1f} -> "
              f"{ellipse['semi_major_km']:.1f}x{ellipse['semi_minor_km']:.1f} km")
    
    # Clamp minor axis independently if still too large
    if ellipse["semi_minor_km"] > max_semi_minor:
        ellipse["semi_minor_km"] = max_semi_minor
    
    return ellipse


def compute_ellipse_safe(
    points: List[Dict],
    filter_outliers: bool = True,
    clamp: bool = True,
) -> Optional[Dict]:
    """
    Compute dispersion ellipse with safety measures.
    
    1. Filter outliers using IQR method
    2. Compute ellipse using standard algorithm
    3. Clamp to max size
    
    Args:
        points: List of impact point dicts with 'lat' and 'lon'
        filter_outliers: Whether to apply IQR filtering
        clamp: Whether to clamp ellipse size
    
    Returns:
        Ellipse dict or None if insufficient points
    """
    if not points or len(points) < 3:
        return None
    
    # Step 1: Filter outliers
    if filter_outliers:
        points = filter_outliers_iqr(points)
    
    if len(points) < 3:
        return None
    
    # Step 2: Compute ellipse using existing algorithm
    # Import here to avoid circular imports
    from run_pipeline import compute_ellipse_from_geo
    
    try:
        ellipse = compute_ellipse_from_geo(points)
    except Exception as e:
        print(f"    [ERROR] Ellipse computation failed: {e}")
        return None
    
    if not ellipse:
        return None
    
    # Step 3: Clamp size
    if clamp:
        ellipse = clamp_ellipse(ellipse)
    
    return ellipse


def compute_combined_bounds(
    primary_ellipse: Optional[Dict],
    fragment_ellipse: Optional[Dict],
) -> Tuple[float, float, float, float]:
    """
    Compute combined bounding box for both ellipses.
    
    Returns:
        (min_lat, max_lat, min_lon, max_lon)
    """
    import math
    
    bounds_list = []
    
    for ellipse in [primary_ellipse, fragment_ellipse]:
        if not ellipse:
            continue
        
        clat = ellipse["center_lat"]
        clon = ellipse["center_lon"]
        a_km = ellipse["semi_major_km"]
        b_km = ellipse["semi_minor_km"]
        
        # Approximate bounds (ignoring rotation for simplicity)
        lat_extent = max(a_km, b_km) / 111.0
        lon_extent = max(a_km, b_km) / (111.0 * math.cos(math.radians(clat)))
        
        bounds_list.append((
            clat - lat_extent,
            clat + lat_extent,
            clon - lon_extent,
            clon + lon_extent,
        ))
    
    if not bounds_list:
        return (0, 0, 0, 0)
    
    min_lat = min(b[0] for b in bounds_list)
    max_lat = max(b[1] for b in bounds_list)
    min_lon = min(b[2] for b in bounds_list)
    max_lon = max(b[3] for b in bounds_list)
    
    return (min_lat, max_lat, min_lon, max_lon)
