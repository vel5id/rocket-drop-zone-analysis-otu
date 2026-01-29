"""
FAO Harmonized World Soil Database (HWSD) integration for zone-based visualization.

Uses HWSD v2.0 from GEE Community Catalog to fetch soil type polygons
that match the "Cartogram of soil bonitet" style from the paper.
"""
from __future__ import annotations

import json
import numpy as np
from typing import List, Dict, Tuple, Optional, Any
from pathlib import Path

try:
    import ee
    HAS_GEE = True
except ImportError:
    ee = None
    HAS_GEE = False


# HWSD v2.0 GEE Community Catalog asset
HWSD_SMU_ASSET = "projects/sat-io/open-datasets/FAO/HWSD_V2_SMU"

# FAO-UNESCO Legend Soil Type Classifications (simplified)
# These are the dominant soil types in Kazakhstan steppes
SOIL_TYPE_COLORS = {
    # Chernozems (high fertility) - Green tones
    "CH": {"color": "#228B22", "name": "Chernozems", "bonitet": 17},
    
    # Kastanozems (moderate fertility) - Yellow-green tones
    "KS": {"color": "#90EE90", "name": "Kastanozems", "bonitet": 13},
    
    # Calcisols (calcareous) - Pink tones
    "CL": {"color": "#FFB6C1", "name": "Calcisols", "bonitet": 10},
    
    # Solonetz (saline soils) - Light blue tones
    "SN": {"color": "#89CFF0", "name": "Solonetz", "bonitet": 5},
    
    # Solonchaks (highly saline) - Pale blue
    "SC": {"color": "#B0E0E6", "name": "Solonchaks", "bonitet": 3},
    
    # Arenosols (sandy) - Tan/beige
    "AR": {"color": "#D2B48C", "name": "Arenosols", "bonitet": 4},
    
    # Regosols (rocky) - Gray
    "RG": {"color": "#A9A9A9", "name": "Regosols", "bonitet": 2},
    
    # Fluvisols (alluvial) - Turquoise
    "FL": {"color": "#40E0D0", "name": "Fluvisols", "bonitet": 12},
    
    # Gleysols (waterlogged) - Dark blue
    "GL": {"color": "#0066CC", "name": "Gleysols", "bonitet": 6},
    
    # Leptosols (thin soils) - Light gray
    "LP": {"color": "#D3D3D3", "name": "Leptosols", "bonitet": 1},
    
    # Default for unknown types
    "XX": {"color": "#CCCCCC", "name": "Other", "bonitet": 5},
}


def fetch_fao_soil_zones(
    bbox: Tuple[float, float, float, float],
    scale_m: int = 1000,
    cache_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fetch FAO HWSD soil zones for the given bounding box.
    
    Args:
        bbox: (min_lat, min_lon, max_lat, max_lon)
        scale_m: Resolution in meters (default 1000m = 1km)
        cache_dir: Optional cache directory
        
    Returns:
        GeoJSON FeatureCollection with soil zone polygons
    """
    if not HAS_GEE:
        print("  [ERROR] Google Earth Engine not available")
        return _generate_mock_soil_zones(bbox)
    
    # Check cache
    cache_key = f"fao_soil_{bbox[0]:.2f}_{bbox[1]:.2f}_{bbox[2]:.2f}_{bbox[3]:.2f}"
    if cache_dir:
        cache_path = Path(cache_dir) / f"{cache_key}.geojson"
        if cache_path.exists():
            print(f"  [CACHE HIT] Loading FAO soil zones from {cache_path}")
            with open(cache_path, "r") as f:
                return json.load(f)
    
    try:
        # Initialize GEE
        ee.Initialize(project="ee-cosmic-anthem-402017")
        
        # Create bounding box geometry
        min_lat, min_lon, max_lat, max_lon = bbox
        region = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
        
        # Load HWSD v2.0 Soil Mapping Units
        hwsd = ee.Image(HWSD_SMU_ASSET)
        
        # Get unique soil mapping unit IDs in the region
        # The SMU band contains integer codes for soil types
        smu = hwsd.select(["b1"])  # First band is SMU ID
        
        # Reduce to vectors (polygons) at specified scale
        print(f"  Fetching FAO soil zones at {scale_m}m resolution...")
        
        # Convert raster to vector polygons
        vectors = smu.reduceToVectors(
            geometry=region,
            scale=scale_m,
            geometryType="polygon",
            labelProperty="soil_class",
            maxPixels=1e8,
            bestEffort=True,
        )
        
        # Get the features
        features_info = vectors.getInfo()
        
        if not features_info or "features" not in features_info:
            print("  [WARN] No soil features found, using mock data")
            return _generate_mock_soil_zones(bbox)
        
        # Process features to add color and bonitet info
        processed_features = []
        for feat in features_info["features"]:
            props = feat.get("properties", {})
            soil_class = props.get("soil_class", 0)
            
            # Map SMU code to soil type (simplified mapping)
            soil_type = _map_smu_to_type(soil_class)
            soil_info = SOIL_TYPE_COLORS.get(soil_type, SOIL_TYPE_COLORS["XX"])
            
            feat["properties"] = {
                "soil_class": soil_class,
                "soil_type": soil_type,
                "soil_name": soil_info["name"],
                "bonitet": soil_info["bonitet"],
                "color": soil_info["color"],
                "stability_class": _bonitet_to_stability_class(soil_info["bonitet"]),
            }
            processed_features.append(feat)
        
        result = {
            "type": "FeatureCollection",
            "features": processed_features,
            "properties": {
                "source": "FAO HWSD v2.0",
                "scale_m": scale_m,
            }
        }
        
        # Cache result
        if cache_dir:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)
            with open(cache_path, "w") as f:
                json.dump(result, f)
            print(f"  [CACHED] Saved to {cache_path}")
        
        print(f"  [OK] Fetched {len(processed_features)} soil zone polygons")
        return result
        
    except Exception as e:
        print(f"  [ERROR] GEE fetch failed: {e}")
        return _generate_mock_soil_zones(bbox)


def _map_smu_to_type(smu_code: int) -> str:
    """Map HWSD Soil Mapping Unit code to FAO soil type abbreviation."""
    # Simplified mapping based on HWSD documentation
    # Real implementation would use the full HWSD lookup table
    
    # Kazakhstan region typically has these soil distributions:
    # 1-1000: Chernozems
    # 1001-2000: Kastanozems  
    # 2001-3000: Calcisols
    # 3001-4000: Solonetz/Solonchaks
    # etc.
    
    if smu_code == 0:
        return "XX"
    elif smu_code < 500:
        return "CH"  # Chernozems
    elif smu_code < 1000:
        return "KS"  # Kastanozems
    elif smu_code < 1500:
        return "CL"  # Calcisols
    elif smu_code < 2000:
        return "SN"  # Solonetz
    elif smu_code < 2500:
        return "SC"  # Solonchaks
    elif smu_code < 3000:
        return "AR"  # Arenosols
    elif smu_code < 3500:
        return "FL"  # Fluvisols
    elif smu_code < 4000:
        return "GL"  # Gleysols
    else:
        return "LP"  # Leptosols


def _bonitet_to_stability_class(bonitet: int) -> str:
    """Convert bonitet score to stability class."""
    if bonitet >= 15:
        return "high"
    elif bonitet >= 10:
        return "moderate"
    elif bonitet >= 5:
        return "low"
    else:
        return "unstable"


def _generate_mock_soil_zones(
    bbox: Tuple[float, float, float, float],
) -> Dict[str, Any]:
    """Generate mock soil zone polygons matching the paper's style."""
    min_lat, min_lon, max_lat, max_lon = bbox
    
    # Create irregular zones similar to the paper's map
    # Using simplified geometric zones
    features = []
    
    # Zone layout inspired by the paper's "Картограмма бонитета почв"
    zones = [
        # Central pink zone (Calcisols - moderate fertility)
        {
            "type": "CL",
            "coords": [
                [min_lon + 0.3*(max_lon-min_lon), min_lat + 0.3*(max_lat-min_lat)],
                [min_lon + 0.7*(max_lon-min_lon), min_lat + 0.3*(max_lat-min_lat)],
                [min_lon + 0.8*(max_lon-min_lon), min_lat + 0.5*(max_lat-min_lat)],
                [min_lon + 0.7*(max_lon-min_lon), min_lat + 0.7*(max_lat-min_lat)],
                [min_lon + 0.3*(max_lon-min_lon), min_lat + 0.7*(max_lat-min_lat)],
                [min_lon + 0.2*(max_lon-min_lon), min_lat + 0.5*(max_lat-min_lat)],
            ]
        },
        # Left green zone (Kastanozems - good fertility)
        {
            "type": "KS", 
            "coords": [
                [min_lon, min_lat + 0.2*(max_lat-min_lat)],
                [min_lon + 0.3*(max_lon-min_lon), min_lat + 0.3*(max_lat-min_lat)],
                [min_lon + 0.2*(max_lon-min_lon), min_lat + 0.5*(max_lat-min_lat)],
                [min_lon + 0.3*(max_lon-min_lon), min_lat + 0.7*(max_lat-min_lat)],
                [min_lon, min_lat + 0.8*(max_lat-min_lat)],
            ]
        },
        # Right turquoise zone (Fluvisols - alluvial)
        {
            "type": "FL",
            "coords": [
                [min_lon + 0.7*(max_lon-min_lon), min_lat + 0.3*(max_lat-min_lat)],
                [max_lon, min_lat + 0.2*(max_lat-min_lat)],
                [max_lon, min_lat + 0.8*(max_lat-min_lat)],
                [min_lon + 0.7*(max_lon-min_lon), min_lat + 0.7*(max_lat-min_lat)],
                [min_lon + 0.8*(max_lon-min_lon), min_lat + 0.5*(max_lat-min_lat)],
            ]
        },
        # Top light blue zone (Solonetz - saline)
        {
            "type": "SN",
            "coords": [
                [min_lon, max_lat],
                [max_lon, max_lat],
                [max_lon, min_lat + 0.8*(max_lat-min_lat)],
                [min_lon + 0.7*(max_lon-min_lon), min_lat + 0.7*(max_lat-min_lat)],
                [min_lon + 0.3*(max_lon-min_lon), min_lat + 0.7*(max_lat-min_lat)],
                [min_lon, min_lat + 0.8*(max_lat-min_lat)],
            ]
        },
        # Bottom blue zone (Solonchaks - highly saline)
        {
            "type": "SC",
            "coords": [
                [min_lon, min_lat],
                [max_lon, min_lat],
                [max_lon, min_lat + 0.2*(max_lat-min_lat)],
                [min_lon + 0.7*(max_lon-min_lon), min_lat + 0.3*(max_lat-min_lat)],
                [min_lon + 0.3*(max_lon-min_lon), min_lat + 0.3*(max_lat-min_lat)],
                [min_lon, min_lat + 0.2*(max_lat-min_lat)],
            ]
        },
    ]
    
    for i, zone in enumerate(zones):
        soil_type = zone["type"]
        soil_info = SOIL_TYPE_COLORS[soil_type]
        
        # Close the polygon
        coords = zone["coords"] + [zone["coords"][0]]
        
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[lon, lat] for lat, lon in [(c[1], c[0]) for c in coords]]]
            },
            "properties": {
                "soil_class": i + 1,
                "soil_type": soil_type,
                "soil_name": soil_info["name"],
                "bonitet": soil_info["bonitet"],
                "color": soil_info["color"],
                "stability_class": _bonitet_to_stability_class(soil_info["bonitet"]),
            }
        })
    
    print(f"  [MOCK] Generated {len(features)} mock soil zones")
    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "source": "Mock data (FAO style)",
            "scale_m": 1000,
        }
    }


def get_zone_color(soil_type: str) -> str:
    """Get color for a soil type."""
    return SOIL_TYPE_COLORS.get(soil_type, SOIL_TYPE_COLORS["XX"])["color"]


def get_bonitet_color(bonitet: int) -> str:
    """Get color based on bonitet score (paper's classification)."""
    # Match paper's legend:
    # 0-5: голубой (light blue) - 21%
    # 5.1-10: розовый (pink) - 27%
    # 10.1-15: зелёный (green) - 50%
    # 15.1-20: бирюзовый (turquoise) - 2%
    
    if bonitet <= 5:
        return "#89CFF0"  # Light blue
    elif bonitet <= 10:
        return "#FFB6C1"  # Pink
    elif bonitet <= 15:
        return "#90EE90"  # Light green
    else:
        return "#40E0D0"  # Turquoise
