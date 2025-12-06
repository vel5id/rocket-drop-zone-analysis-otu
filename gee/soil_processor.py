"""Soil data processing using SoilGrids and local datasets."""
from __future__ import annotations

import ee


def get_soil_strength_index(roi: ee.Geometry) -> ee.Image:
    """
    Calculate Q_Si (soil mechanical strength) from SoilGrids data.
    
    Uses bulk density and clay content as proxies for Protodyakonov hardness.
    Higher bulk density + clay = more cohesive/strong soil.
    
    Protodyakonov scale approximation:
    - f=1-2: Very soft soils (peat, loose sand)
    - f=3-5: Medium soils (clay, loam)
    - f=6-10: Hard soils (compacted clay, gravel)
    
    We normalize to [0, 1] where 1 = strongest.
    """
    # SoilGrids 250m - Bulk Density (cg/cm³) at 0-5cm depth
    bulk_density = ee.Image("projects/soilgrids-isric/bdod_mean").select("bdod_0-5cm_mean")
    
    # SoilGrids 250m - Clay content (g/kg) at 0-5cm depth  
    clay = ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean")
    
    # Normalize bulk density: typical range 800-1800 cg/cm³
    bd_norm = bulk_density.subtract(800).divide(1000).clamp(0, 1)
    
    # Normalize clay: typical range 0-600 g/kg
    clay_norm = clay.divide(600).clamp(0, 1)
    
    # Combined strength index (weighted average)
    # Higher bulk density and clay content = stronger soil
    q_si = bd_norm.multiply(0.6).add(clay_norm.multiply(0.4)).rename("Q_Si")
    
    return q_si.clip(roi)


def get_soil_quality_index(roi: ee.Geometry) -> ee.Image:
    """
    Calculate Q_Bi (soil quality/bonitet) from SoilGrids data.
    
    Uses soil organic carbon and nitrogen as proxies for soil fertility/bonitet.
    Higher organic content = better soil quality.
    
    Bonitet scale (Russian system):
    - 1-20: Poor soils
    - 21-50: Average soils
    - 51-80: Good soils
    - 81-100: Excellent soils
    
    We normalize to [0, 1] where 1 = best quality.
    """
    # SoilGrids 250m - Soil Organic Carbon (dg/kg) at 0-5cm
    soc = ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean")
    
    # SoilGrids 250m - Nitrogen (cg/kg) at 0-5cm
    nitrogen = ee.Image("projects/soilgrids-isric/nitrogen_mean").select("nitrogen_0-5cm_mean")
    
    # Normalize SOC: typical range 0-200 dg/kg (0-20 g/kg)
    soc_norm = soc.divide(200).clamp(0, 1)
    
    # Normalize Nitrogen: typical range 0-20 cg/kg
    n_norm = nitrogen.divide(20).clamp(0, 1)
    
    # Combined quality index
    q_bi = soc_norm.multiply(0.7).add(n_norm.multiply(0.3)).rename("Q_Bi")
    
    return q_bi.clip(roi)


def get_soil_indices(roi: ee.Geometry) -> tuple[ee.Image, ee.Image]:
    """Get both soil indices for a region."""
    return get_soil_strength_index(roi), get_soil_quality_index(roi)
