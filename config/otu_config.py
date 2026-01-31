"""
OTU Configuration Module.

Centralizes all parameters, weights, and constants for OTU calculation.
"""
from dataclasses import dataclass

@dataclass
class OTUWeights:
    """Weights for OTU index components."""
    k_vi: float = 0.35   # Vegetation index weight
    k_si: float = 0.35   # Soil strength weight
    k_bi: float = 0.30   # Soil quality/bonitet weight

@dataclass
class SoilNormalization:
    """Normalization ranges for soil parameters."""
    # Bulk density (kg/m3)
    bd_min: float = 800.0
    bd_max: float = 1800.0
    
    # Clay content (g/kg)
    clay_min: float = 0.0
    clay_max: float = 600.0
    
    # Soil Organic Carbon (g/kg)
    soc_min: float = 0.0
    soc_max: float = 200.0
    
    # Nitrogen (g/kg)
    nitrogen_min: float = 0.0
    nitrogen_max: float = 20.0

@dataclass
class ReliefConfig:
    """Configuration for relief penalty calculation."""
    # Critical slope angle in degrees where penalty becomes severe
    critical_slope: float = 20.0
    
    # Maximum slope for normalization (used in linear part)
    max_slope: float = 75.0
    
    # Penalty weight for water bodies (0.0 to 1.0)
    water_penalty: float = 0.5

@dataclass
class AspectConfig:
    """
    Multipliers for slope aspect (exposure).
    North (cool, moist) is most stable (1.0).
    South (hot, dry) is least stable.
    """
    north_weight: float = 1.0
    east_weight: float = 0.9
    west_weight: float = 0.7
    south_weight: float = 0.6

@dataclass
class FireConfig:
    """
    Configuration for Fire Risk (Q_Fi).
    High NDVI = High Biomass = High Fire Risk.
    """
    ndvi_threshold_low: float = 0.2  # Below this, risk is 0
    ndvi_threshold_high: float = 0.8 # Above this, risk is 1

@dataclass
class GEEConfig:
    """Google Earth Engine configuration."""
    project_id: str = "qgis-forest-vladimirfominov49"
    ndvi_window_days: int = 14
    cloud_threshold: int = 30
    
    # If True, raise error when GEE is unavailable instead of using mock data
    strict_mode: bool = True

@dataclass
class PipelineConfig:
    """Pipeline execution defaults."""
    # Use GPU acceleration by default (Numba JIT)
    use_gpu: bool = True
    
    # Cache is opt-in (not default) to avoid unexpected DB creation
    use_cache: bool = False
    
    # Default Monte Carlo iterations
    default_iterations: int = 100
    
    # Grid cell size in km
    cell_size_km: float = 1.0

class OTUConfig:
    """Main configuration container."""
    weights = OTUWeights()
    soil = SoilNormalization()
    relief = ReliefConfig()
    aspect = AspectConfig()
    fire = FireConfig()
    gee = GEEConfig()
    pipeline = PipelineConfig()

