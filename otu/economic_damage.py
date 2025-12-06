"""
Economic Damage Assessment Module.

Calculates restoration costs per OTU cell using formulas from paper_content.txt.

Formulas (from paper section 4.3):
- CFi = kF * QFi       — Fire restoration cost
- CQPi = Cp * kn * Qnp — Soil strength damage cost  
- CBi = CBn * kBi * QBn — Soil quality damage cost
- CVi = nVi * QVmi * vri * CnVi — Vegetation restoration cost
- Ci = CSi + CQPi + CQBi + CVi — Total restoration cost
"""
import numpy as np
from dataclasses import dataclass
from typing import Union


@dataclass
class EconomicConfig:
    """Default cost coefficients (in conventional units, e.g., USD/ha)."""
    # Fire restoration base cost per ha
    fire_base_cost: float = 5000.0
    
    # Soil restoration base costs
    soil_strength_base: float = 3000.0  # Mechanical restoration
    soil_quality_base: float = 4000.0   # Biological restoration
    
    # Vegetation restoration base cost
    vegetation_base: float = 8000.0
    
    # Vegetation recovery rate (inverse of OTU stability)
    vegetation_recovery_factor: float = 2.0


def compute_fire_damage_cost(
    q_fire: Union[float, np.ndarray],
    area_ha: float = 1.0,
    config: EconomicConfig = None,
) -> Union[float, np.ndarray]:
    """
    Calculate fire restoration cost: CFi = kF * QFi * Area.
    
    Higher fire risk = higher restoration cost.
    """
    if config is None:
        config = EconomicConfig()
    
    return config.fire_base_cost * q_fire * area_ha


def compute_soil_damage_cost(
    q_si: Union[float, np.ndarray],
    q_bi: Union[float, np.ndarray],
    area_ha: float = 1.0,
    config: EconomicConfig = None,
) -> tuple:
    """
    Calculate soil restoration costs.
    
    Returns: (strength_cost, quality_cost)
    
    Logic: Lower stability = Higher damage = Higher cost
    """
    if config is None:
        config = EconomicConfig()
    
    # Invert: high stability (1.0) = low cost, low stability (0.0) = high cost
    strength_damage = (1.0 - q_si)
    quality_damage = (1.0 - q_bi)
    
    c_strength = config.soil_strength_base * strength_damage * area_ha
    c_quality = config.soil_quality_base * quality_damage * area_ha
    
    return c_strength, c_quality


def compute_vegetation_damage_cost(
    q_vi: Union[float, np.ndarray],
    area_ha: float = 1.0,
    config: EconomicConfig = None,
) -> Union[float, np.ndarray]:
    """
    Calculate vegetation restoration cost: CVi = nVi * QVmi * vri * CnVi.
    
    Simplification: cost inversely proportional to vegetation health.
    High NDVI (healthy) = lower restoration need.
    """
    if config is None:
        config = EconomicConfig()
    
    # Damage factor based on vegetation state
    veg_damage = 1.0 - q_vi
    
    return config.vegetation_base * veg_damage * config.vegetation_recovery_factor * area_ha


def compute_total_restoration_cost(
    q_vi: Union[float, np.ndarray],
    q_si: Union[float, np.ndarray],
    q_bi: Union[float, np.ndarray],
    q_fire: Union[float, np.ndarray],
    area_ha: float = 1.0,
    config: EconomicConfig = None,
) -> dict:
    """
    Calculate total restoration cost for OTU cell(s).
    
    Ci = CSi + CQPi + CQBi + CVi
    
    Returns dict with all cost components.
    """
    if config is None:
        config = EconomicConfig()
    
    c_fire = compute_fire_damage_cost(q_fire, area_ha, config)
    c_strength, c_quality = compute_soil_damage_cost(q_si, q_bi, area_ha, config)
    c_vegetation = compute_vegetation_damage_cost(q_vi, area_ha, config)
    
    total = c_fire + c_strength + c_quality + c_vegetation
    
    return {
        "fire_cost": c_fire,
        "soil_strength_cost": c_strength,
        "soil_quality_cost": c_quality,
        "vegetation_cost": c_vegetation,
        "total_cost": total,
    }


def compute_impact_zone_cost(
    otu_results: np.ndarray,
    cell_size_km: float = 1.0,
    config: EconomicConfig = None,
) -> dict:
    """
    Calculate total economic damage for entire impact zone.
    
    otu_results: Array with columns [q_ndvi, q_si, q_bi, q_relief, q_otu, q_fire]
    
    Returns summary statistics.
    """
    if config is None:
        config = EconomicConfig()
    
    # Cell area in hectares (1 km² = 100 ha)
    cell_area_ha = cell_size_km ** 2 * 100
    
    n_cells = len(otu_results)
    
    # Extract components
    q_vi = otu_results[:, 0]
    q_si = otu_results[:, 1]
    q_bi = otu_results[:, 2]
    q_fire = otu_results[:, 5] if otu_results.shape[1] > 5 else np.zeros(n_cells)
    
    # Compute per-cell costs
    costs = compute_total_restoration_cost(q_vi, q_si, q_bi, q_fire, cell_area_ha, config)
    
    return {
        "num_cells": n_cells,
        "cell_area_ha": cell_area_ha,
        "total_area_ha": n_cells * cell_area_ha,
        "fire_cost_total": float(np.sum(costs["fire_cost"])),
        "soil_cost_total": float(np.sum(costs["soil_strength_cost"]) + np.sum(costs["soil_quality_cost"])),
        "vegetation_cost_total": float(np.sum(costs["vegetation_cost"])),
        "grand_total": float(np.sum(costs["total_cost"])),
        "cost_per_cell_mean": float(np.mean(costs["total_cost"])),
        "cost_per_cell_min": float(np.min(costs["total_cost"])),
        "cost_per_cell_max": float(np.max(costs["total_cost"])),
    }
