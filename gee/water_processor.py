"""Water body detection and hydrological analysis using GEE."""
from __future__ import annotations

import ee


def get_water_mask(roi: ee.Geometry, threshold: int = 50) -> ee.Image:
    """
    Get water body mask from JRC Global Surface Water.
    
    Args:
        roi: Region of interest
        threshold: Minimum water occurrence percentage (0-100)
    
    Returns:
        Binary mask where 1 = water body
    """
    water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
    is_water = water.gt(threshold).unmask(0).rename("water_mask")
    return is_water.clip(roi)


def get_river_network(roi: ee.Geometry, min_upstream_km2: float = 10.0) -> ee.Image:
    """
    Get river/stream network from HydroSHEDS.
    
    Args:
        roi: Region of interest
        min_upstream_km2: Minimum upstream drainage area to include
    
    Returns:
        Raster with upstream drainage area values
    """
    # HydroSHEDS - Flow Accumulation (upstream area in km²)
    hydro = ee.Image("WWF/HydroSHEDS/15ACC")
    
    # Filter to significant streams
    rivers = hydro.gt(min_upstream_km2 * 100).selfMask().rename("rivers")
    
    return rivers.clip(roi)


def get_flood_risk(roi: ee.Geometry) -> ee.Image:
    """
    Estimate flood risk based on distance to water and elevation.
    
    Returns:
        Flood risk index [0, 1] where 1 = highest risk
    """
    # Get water bodies
    water = get_water_mask(roi, threshold=30)
    
    # Distance to water (in meters)
    distance = water.distance(kernel=ee.Kernel.euclidean(radius=5000, units="meters"))
    
    # Normalize: closer to water = higher risk
    # 0m -> risk=1, 5000m+ -> risk=0
    flood_risk = ee.Image.constant(1).subtract(distance.divide(5000)).clamp(0, 1)
    
    return flood_risk.rename("flood_risk").clip(roi)
