"""DEM and terrain analysis using GEE."""
from __future__ import annotations

import ee


def get_terrain_analysis(roi: ee.Geometry) -> dict[str, ee.Image]:
    """
    Perform comprehensive terrain analysis.
    
    Returns:
        Dictionary with terrain layers: elevation, slope, aspect, hillshade
    """
    # SRTM 30m DEM
    dem = ee.Image("USGS/SRTMGL1_003").clip(roi)
    
    # Compute terrain derivatives
    terrain = ee.Terrain.products(dem)
    
    return {
        "elevation": dem.rename("elevation"),
        "slope": terrain.select("slope"),
        "aspect": terrain.select("aspect"),
        "hillshade": terrain.select("hillshade"),
    }


def get_relief_factor(roi: ee.Geometry) -> ee.Image:
    """
    Calculate Q_relief factor based on terrain and water.
    
    The relief factor penalizes:
    1. Steep slopes (fuel runoff risk)
    2. Water bodies (contamination risk)
    3. Low-lying areas near water (flood risk)
    
    Formula: Q_relief = 1 - (slope_penalty + water_penalty + flood_penalty)
    """
    from gee.water_processor import get_water_mask, get_flood_risk
    
    terrain = get_terrain_analysis(roi)
    slope = terrain["slope"]
    elevation = terrain["elevation"]
    
    # Slope penalty: steep slopes increase runoff risk
    # 0° -> 0, 30°+ -> 0.4 max penalty
    slope_penalty = slope.divide(75.0).clamp(0, 0.4)
    
    # Water body penalty: direct water = high contamination risk
    water_mask = get_water_mask(roi, threshold=50)
    water_penalty = water_mask.multiply(0.5)
    
    # Flood risk penalty
    flood_risk = get_flood_risk(roi)
    flood_penalty = flood_risk.multiply(0.3)
    
    # Combined relief factor
    q_relief = (
        ee.Image.constant(1.0)
        .subtract(slope_penalty)
        .subtract(water_penalty)
        .subtract(flood_penalty)
        .clamp(0, 1)
        .rename("Q_relief")
    )
    
    return q_relief
