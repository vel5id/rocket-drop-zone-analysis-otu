"""
GeoJSON conversion utilities for UI.
"""
from __future__ import annotations

from typing import List, Dict, Optional, Any
from dataclasses import dataclass


def points_to_geojson(points: List[Dict]) -> Dict[str, Any]:
    """
    Convert impact points to GeoJSON FeatureCollection.
    
    Args:
        points: List of point dicts with 'lat', 'lon', and optional properties
    
    Returns:
        GeoJSON FeatureCollection
    """
    features = []
    
    for i, p in enumerate(points):
        feature = {
            "type": "Feature",
            "properties": {
                "id": i + 1,
                "is_fragment": p.get("is_fragment", False),
                "velocity": float(p.get("velocity", 0)) if p.get("velocity") else None,
                "fragment_id": p.get("fragment_id"),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [p["lon"], p["lat"]]
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}


def ellipse_to_geojson(
    ellipse: Dict,
    properties: Optional[Dict] = None,
    num_points: int = 64,
) -> Dict[str, Any]:
    """
    Convert ellipse to GeoJSON Polygon Feature.
    
    Args:
        ellipse: Ellipse dict with center_lat, center_lon, semi_major_km, semi_minor_km, angle_deg
        properties: Optional additional properties
        num_points: Number of points for polygon approximation
    
    Returns:
        GeoJSON Feature with Polygon geometry
    """
    import math
    import numpy as np
    
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
    for t in np.linspace(0, 2*np.pi, num_points):
        x = a_km * deg_per_km_lon * np.cos(t)
        y = b_km * deg_per_km_lat * np.sin(t)
        
        xr = x * np.cos(math_angle) - y * np.sin(math_angle)
        yr = x * np.sin(math_angle) + y * np.cos(math_angle)
        
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


def grid_to_geojson(
    grid_cells: List,
    otu_values: Optional[List[Dict]] = None,
) -> Dict[str, Any]:
    """
    Convert grid cells to GeoJSON FeatureCollection.
    
    Args:
        grid_cells: List of GridCell objects
        otu_values: Optional list of OTU value dicts per cell
    
    Returns:
        GeoJSON FeatureCollection
    """
    features = []
    
    for i, cell in enumerate(grid_cells):
        # Build polygon from cell bounds
        coords = [
            [cell.min_lon, cell.min_lat],
            [cell.max_lon, cell.min_lat],
            [cell.max_lon, cell.max_lat],
            [cell.min_lon, cell.max_lat],
            [cell.min_lon, cell.min_lat],  # Close polygon
        ]
        
        props = {
            "id": getattr(cell, "id", f"cell_{i+1}"),  # Use cell.id if available
            "center_lat": cell.center_lat,
            "center_lon": cell.center_lon,
        }
        
        # Add OTU values if provided (Explicit override)
        if otu_values and i < len(otu_values):
            props.update(otu_values[i])
        # Check if values are attached to the cell object (Dynamic attachment)
        elif hasattr(cell, "q_otu"):
            props.update({
                "q_vi": getattr(cell, "q_vi", 0.0),          # ✅ Correct name
                "q_si": getattr(cell, "q_si", 0.0),
                "q_bi": getattr(cell, "q_bi", 0.0),
                "q_relief": getattr(cell, "q_relief", 0.0),
                "q_otu": getattr(cell, "q_otu", 0.0),
                "is_processed": getattr(cell, "is_processed", True),
                "missing_data": getattr(cell, "missing_data", []),
            })
            if i == 0:
                print(f"[GeoJSON] Using attached cell attributes for Cell {i+1}: OTU={props['q_otu']}, NDVI={props['q_vi']}")
        else:
            # Default placeholder values (should not happen if OTU calculation succeeded)
            props.update({
                "q_vi": 0.0,
                "q_si": 0.0,
                "q_bi": 0.0,
                "q_relief": 0.0,
                "q_otu": 0.0,
                "is_processed": False,
                "missing_data": ["ndvi", "soil", "relief"],  # Mark all as missing
            })
            if i == 0:
                print(f"[GeoJSON] WARNING: Using DEFAULT values for Cell {i+1} (No OTU data found)")
        
        feature = {
            "type": "Feature",
            "properties": props,
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords]
            }
        }
        features.append(feature)
    
    return {"type": "FeatureCollection", "features": features}


@dataclass
class SimulationResultGeoJSON:
    """Complete simulation result in GeoJSON format for UI."""
    primary_ellipse: Optional[Dict[str, Any]]
    fragment_ellipse: Optional[Dict[str, Any]]
    impact_points: Dict[str, Any]
    otu_grid: Dict[str, Any]
    stats: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for JSON serialization."""
        return {
            "primary_ellipse": self.primary_ellipse,
            "fragment_ellipse": self.fragment_ellipse,
            "impact_points": self.impact_points,
            "otu_grid": self.otu_grid,
            "stats": self.stats,
        }
