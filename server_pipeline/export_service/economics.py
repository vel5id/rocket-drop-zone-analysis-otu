"""
Economic Cost Calculation Module.

Implements the cost estimation logic for ecological restoration.
Formulas derived from methodology V2.1.
"""
import numpy as np
from typing import Dict, Any
from .models import CostBreakdown

# -----------------------------------------------------------------------------
# CONSTANTS (Base Costs per Hectare in USD)
# -----------------------------------------------------------------------------
BASE_COST_FIRE = 1000.0        # $/ha for fire prevention/suppression
BASE_COST_SOIL_STRENGTH = 500.0  # $/ha for soil reinforcement
BASE_COST_SOIL_QUALITY = 800.0   # $/ha for biological remediation
BASE_COST_VEGETATION = 1200.0    # $/ha for replanting

def calculate_costs(
    q_fi: float,
    q_si: float,
    q_bi: float,
    q_vi: float,
    q_relief: float,
    area_ha: float = 1.0
) -> CostBreakdown:
    """
    Calculate economic costs for restoration based on ecological risks.
    
    Formulas:
    C_Fire = Base * Q_Fi
    C_SoilStrength = Base * (Weight_Si * Q_Si)
    C_SoilQuality = Base * (Weight_Bi * Q_Bi)
    C_Vegetation = Base * (Weight_Vi * Q_Vi * Uncertainty_Factor)
    
    Args:
        q_fi: Fire Risk Index [0-1]
        q_si: Soil Strength Index [0-1]
        q_bi: Soil Quality Index [0-1]
        q_vi: Vegetation/NDVI Index [0-1]
        q_relief: Relief Stability Index [0-1]
        area_ha: Area in hectares
    
    Returns:
        CostBreakdown object
    """
    # Weights from methodology (Hardcoded for now, ideally from config)
    w_si = 0.4
    w_bi = 0.3
    w_vi = 0.3
    uncertainty_factor = 0.65  # Empirical factor for vegetation success
    
    # 1. Fire Risk Cost
    # Proportional to fire hazard
    c_fire = BASE_COST_FIRE * q_fi * area_ha
    
    # 2. Soil Strength Cost
    # Proportional to soil instability (Inverse of strength? No, methodology says proportional to index for maintenance)
    # *Assumption*: Higher Q_Si (better soil) -> Lower Cost? 
    # *Correction*: Request says: "500 * (0.40 * 0.1567)" -> So it scales WITH the index. 
    # This implies these are "Opportunity Costs" or "Value at Risk", not "Restoration Cost".
    # Or, it's a "Maintenance Cost" where higher quality = higher value to protect.
    # We follow the User's formula exactly: Base * (Weight * Index)
    c_si = BASE_COST_SOIL_STRENGTH * (w_si * q_si) * area_ha
    
    # 3. Soil Quality Cost
    c_bi = BASE_COST_SOIL_QUALITY * (w_bi * q_bi) * area_ha
    
    # 4. Vegetation Cost
    c_vi = BASE_COST_VEGETATION * (w_vi * q_vi * uncertainty_factor) * area_ha
    
    # Total
    c_total = c_fire + c_si + c_bi + c_vi
    
    return CostBreakdown(
        c_fire=round(c_fire, 2),
        c_soil_strength=round(c_si, 2),
        c_soil_quality=round(c_bi, 2),
        c_vegetation=round(c_vi, 2),
        c_total=round(c_total, 2)
    )

def estimate_restoration_difficulty(q_otu: float) -> str:
    """Classify difficulty based on OTU."""
    if q_otu > 0.7: return "Low"
    if q_otu > 0.4: return "Moderate"
    return "High"
