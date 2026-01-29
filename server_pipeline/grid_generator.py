"""
Grid generation with safety limits.

Reuses generate_grid_optimized from run_otu_pipeline.py with additional safety caps.
"""
from __future__ import annotations

import sys
import os
from typing import List, Tuple, Callable, Optional

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grid.polygon_grid import GridCell, create_ellipse_polygon

# Safety limits
MAX_GRID_CELLS = 50000  # Maximum number of grid cells
DEFAULT_CELL_SIZE_KM = 1.0


def generate_grid_safe(
    polygons: List[List[Tuple[float, float]]],
    cell_size_km: float = DEFAULT_CELL_SIZE_KM,
    max_cells: int = MAX_GRID_CELLS,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> List[GridCell]:
    """
    Generate grid cells inside polygons with safety limits.
    
    Uses GPU-accelerated version from run_otu_pipeline if available,
    otherwise falls back to optimized numpy version.
    
    Args:
        polygons: List of polygon vertex lists [(lat, lon), ...]
        cell_size_km: Grid cell size in km
        max_cells: Maximum number of cells to generate
        progress_callback: Optional callback(progress_pct, message)
    
    Returns:
        List of GridCell objects
    """
    if not polygons:
        return []
    
    if progress_callback:
        progress_callback(81, "Generating grid...")
    
    # Try to use optimized version from run_otu_pipeline
    try:
        from run_otu_pipeline import generate_grid_optimized
        print("  [GRID] Using GPU-optimized generator")
        grid = generate_grid_optimized(polygons, cell_size_km)
    except ImportError:
        print("  [GRID] Using numpy fallback")
        grid = _generate_grid_numpy(polygons, cell_size_km)
    
    # Apply safety cap
    if len(grid) > max_cells:
        print(f"  [GRID] Capped from {len(grid)} to {max_cells} cells")
        grid = grid[:max_cells]
    
    if progress_callback:
        progress_callback(85, f"Generated {len(grid)} grid cells")
    
    print(f"  [GRID] Generated {len(grid)} cells")
    return grid


def _generate_grid_numpy(
    polygons: List[List[Tuple[float, float]]],
    cell_size_km: float,
) -> List[GridCell]:
    """
    NumPy-based grid generation (faster than pure Python).
    
    Uses matplotlib.path if available, otherwise uses vectorized numpy.
    """
    import math
    import numpy as np
    
    # Get merged bounding box
    all_lats = []
    all_lons = []
    for poly in polygons:
        all_lats.extend([p[0] for p in poly])
        all_lons.extend([p[1] for p in poly])
    
    min_lat, max_lat = min(all_lats), max(all_lats)
    min_lon, max_lon = min(all_lons), max(all_lons)
    
    # Grid parameters
    center_lat = (min_lat + max_lat) / 2
    lat_rad = math.radians(center_lat)
    
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    cell_size_lat = cell_size_km * deg_per_km_lat
    cell_size_lon = cell_size_km * deg_per_km_lon
    
    # Safety check: estimate grid size
    lat_steps = int((max_lat - min_lat) / cell_size_lat) + 1
    lon_steps = int((max_lon - min_lon) / cell_size_lon) + 1
    estimated_cells = lat_steps * lon_steps
    
    if estimated_cells > 1000000:
        print(f"  [GRID] WARNING: Estimated {estimated_cells} cells, increasing cell size")
        # Increase cell size to reduce count
        scale = (estimated_cells / MAX_GRID_CELLS) ** 0.5
        cell_size_km *= scale
        cell_size_lat = cell_size_km * deg_per_km_lat
        cell_size_lon = cell_size_km * deg_per_km_lon
    
    # Try matplotlib path (fastest)
    try:
        from matplotlib.path import Path
        
        paths = [Path(poly) for poly in polygons]
        
        lat_range = np.arange(min_lat + cell_size_lat/2, max_lat, cell_size_lat)
        lon_range = np.arange(min_lon + cell_size_lon/2, max_lon, cell_size_lon)
        
        lon_grid, lat_grid = np.meshgrid(lon_range, lat_range)
        center_lats = lat_grid.flatten()
        center_lons = lon_grid.flatten()
        
        # Check containment
        points = np.column_stack((center_lats, center_lons))
        inside = np.zeros(len(points), dtype=bool)
        
        for path in paths:
            inside |= path.contains_points(points)
        
        valid_indices = np.where(inside)[0]
        
        cells = []
        for idx in valid_indices:
            c_lat = center_lats[idx]
            c_lon = center_lons[idx]
            cells.append(GridCell(
                min_lat=c_lat - cell_size_lat/2,
                max_lat=c_lat + cell_size_lat/2,
                min_lon=c_lon - cell_size_lon/2,
                max_lon=c_lon + cell_size_lon/2,
                center_lat=c_lat,
                center_lon=c_lon,
            ))
        
        return cells
        
    except ImportError:
        # Fallback: simple bounding box grid (no polygon check)
        print("  [GRID] matplotlib not available, using simple grid")
        cells = []
        
        lat = min_lat + cell_size_lat/2
        while lat < max_lat and len(cells) < MAX_GRID_CELLS:
            lon = min_lon + cell_size_lon/2
            while lon < max_lon and len(cells) < MAX_GRID_CELLS:
                cells.append(GridCell(
                    min_lat=lat - cell_size_lat/2,
                    max_lat=lat + cell_size_lat/2,
                    min_lon=lon - cell_size_lon/2,
                    max_lon=lon + cell_size_lon/2,
                    center_lat=lat,
                    center_lon=lon,
                ))
                lon += cell_size_lon
            lat += cell_size_lat
        
        return cells


def create_ellipse_polygons(
    primary_ellipse: dict,
    fragment_ellipse: dict = None,
    scale: float = 1.0,
) -> List[List[Tuple[float, float]]]:
    """
    Create polygon representations of ellipses.
    
    Args:
        primary_ellipse: Primary impact ellipse dict
        fragment_ellipse: Optional fragment ellipse dict
        scale: Scale factor (1.0 = full size)
    
    Returns:
        List of polygon vertex lists
    """
    polygons = []
    
    if primary_ellipse:
        polygons.append(create_ellipse_polygon(primary_ellipse, scale=scale))
    
    if fragment_ellipse:
        polygons.append(create_ellipse_polygon(fragment_ellipse, scale=scale))
    
    return polygons
