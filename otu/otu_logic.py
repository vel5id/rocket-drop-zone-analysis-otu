"""
OTU Logic Module.

Contains pure functions for calculating OTU components using the centralized configuration.
"""
import numpy as np
from typing import Union, Tuple
from config.otu_config import OTUConfig

def normalize_value(value: Union[float, np.ndarray], min_val: float, max_val: float) -> Union[float, np.ndarray]:
    """Normalize value to [0, 1] range with clamping."""
    if isinstance(value, np.ndarray):
        return np.clip((value - min_val) / (max_val - min_val), 0, 1)
    return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

def compute_q_si(
    bulk_density: Union[float, np.ndarray],
    clay: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Compute Soil Mechanical Strength Index (Q_Si).
    
    Q_Si = 0.6 * Norm(BD) + 0.4 * Norm(Clay)
    """
    bd_norm = normalize_value(
        bulk_density, 
        OTUConfig.soil.bd_min, 
        OTUConfig.soil.bd_max
    )
    clay_norm = normalize_value(
        clay, 
        OTUConfig.soil.clay_min, 
        OTUConfig.soil.clay_max
    )
    
    return 0.6 * bd_norm + 0.4 * clay_norm

def compute_q_bi(
    soc: Union[float, np.ndarray],
    nitrogen: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Compute Soil Biological Quality Index (Q_Bi).
    
    Q_Bi = 0.7 * Norm(SOC) + 0.3 * Norm(Nitrogen)
    """
    soc_norm = normalize_value(
        soc, 
        OTUConfig.soil.soc_min, 
        OTUConfig.soil.soc_max
    )
    n_norm = normalize_value(
        nitrogen, 
        OTUConfig.soil.nitrogen_min, 
        OTUConfig.soil.nitrogen_max
    )
    
    return 0.7 * soc_norm + 0.3 * n_norm

def compute_aspect_modifier(aspect_degrees: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate Aspect Modifier based on orientation.
    North (0/360) -> High stability (1.0)
    South (180) -> Low stability (0.6)
    """
    # Convert to radians
    rad = np.radians(aspect_degrees)
    
    # Cosine interpolation:
    # cos(0) = 1 (North) -> should be max weight
    # cos(180) = -1 (South) -> should be min weight
    
    max_w = OTUConfig.aspect.north_weight
    min_w = OTUConfig.aspect.south_weight
    
    avg = (max_w + min_w) / 2.0
    diff = (max_w - min_w) / 2.0
    
    # Note: Aspect 0 is North.
    modifier = avg + diff * np.cos(rad)
    
    return modifier


def compute_fire_risk(ndvi: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate Fire Risk (Q_Fi).
    High NDVI -> High Biomass -> High Risk.
    """
    # Linear mapping from threshold_low (0) to threshold_high (1)
    low = OTUConfig.fire.ndvi_threshold_low
    high = OTUConfig.fire.ndvi_threshold_high
    
    risk = (ndvi - low) / (high - low)
    return np.clip(risk, 0.0, 1.0)


def compute_q_relief(
    slope_degrees: Union[float, np.ndarray],
    is_water: Union[float, np.ndarray],
    aspect_degrees: Union[float, np.ndarray] = None
) -> Union[float, np.ndarray]:
    """
    Calculate Relief Stability Index (Q_Relief).
    
    Combines:
    1. Slope penalty (non-linear)
    2. Water penalty
    3. Aspect (Exposure) penalty (optional)
    """
    # 1. Slope Penalty
    critical = OTUConfig.relief.critical_slope
    
    if isinstance(slope_degrees, np.ndarray):
        # Vectorized implementation
        slope_penalty = np.zeros_like(slope_degrees, dtype=float)
        
        # Mild penalty for gentle slopes
        mask_gentle = slope_degrees <= critical
        slope_penalty[mask_gentle] = slope_degrees[mask_gentle] / (critical * 2.0)
        
        # Severe penalty for steep slopes
        mask_steep = slope_degrees > critical
        excess = slope_degrees[mask_steep] - critical
        steep_penalty = 0.5 + (excess / 20.0) ** 2
        slope_penalty[mask_steep] = np.clip(steep_penalty, 0.5, 1.0)
        
    else:
        # Scalar implementation
        if slope_degrees <= critical:
            slope_penalty = slope_degrees / (critical * 2.0)
        else:
            excess = slope_degrees - critical
            slope_penalty = min(1.0, 0.5 + (excess / 20.0) ** 2)
            
    # Base Q_Relief from slope
    q_relief = 1.0 - slope_penalty
    
    # 2. Water Penalty
    q_relief = q_relief - (is_water * OTUConfig.relief.water_penalty)
    
    # 3. Aspect Penalty (if provided)
    if aspect_degrees is not None:
        aspect_mod = compute_aspect_modifier(aspect_degrees)
        q_relief = q_relief * aspect_mod
    
    return np.clip(q_relief, 0.0, 1.0)

def compute_otu_index(
    q_vi: Union[float, np.ndarray],
    q_si: Union[float, np.ndarray],
    q_bi: Union[float, np.ndarray],
    q_relief: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """
    Compute final OTU Index.
    
    OTU = (k_vi*Q_Vi + k_si*Q_Si + k_bi*Q_Bi) * Q_Relief
    """
    # Normalize weights
    w = OTUConfig.weights
    total_w = w.k_vi + w.k_si + w.k_bi
    k_vi = w.k_vi / total_w
    k_si = w.k_si / total_w
    k_bi = w.k_bi / total_w
    
    linear_part = k_vi * q_vi + k_si * q_si + k_bi * q_bi
    
    return np.clip(linear_part * q_relief, 0, 1)
