"""
Economic Damage Assessment Module.

Calculates restoration costs per OTU cell using formulas from paper_content.txt.

Formulas (from paper section 4.3):
- CFi = kF * QFi       — Fire restoration cost
- CQPi = Cp * kn * Qnp — Soil strength damage cost  
- CBi = CBn * kBi * QBn — Soil quality damage cost
- CVi = nVi * QVmi * vri * CnVi — Vegetation restoration cost
- Ci = CSi + CQPi + CQBi + CVi — Total restoration cost

Task 5.1 Implementation (IMPLEMENTATION_ROADMAP.md lines 636-700):
- Added EconomicDamageCalculator class with unit costs in KZT
- Added contamination component (toxic fuel)
- Added mechanical damage component (impact craters)
- Added calculate_total_damage() method
- Maintained backward compatibility with existing functions
"""
import numpy as np
from dataclasses import dataclass
from typing import Union, List, Dict, Any


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


class EconomicDamageCalculator:
    """
    Comprehensive economic damage calculator for OTU impact assessment.
    
    Implements Task 5.1 from IMPLEMENTATION_ROADMAP.md (lines 654-694).
    Calculates damage costs in KZT (Kazakhstani Tenge) with USD conversion.
    
    Methodology:
    1. Unit costs per hectare based on Kazakhstan restoration cost studies
    2. Damage proportional to OTU stability indices (lower stability = higher cost)
    3. Five damage components: vegetation, soil, fire, contamination, mechanical
    4. Currency conversion using average exchange rate (1 USD = 450 KZT)
    """
    
    def __init__(self, usd_to_kzt: float = 450.0):
        """
        Initialize calculator with unit costs in KZT per hectare.
        
        Unit costs based on:
        - vegetation_loss: Forest restoration costs in Kazakhstan (2023)
        - soil_degradation: Soil remediation costs for agricultural land
        - fire_risk: Fire suppression and rehabilitation costs
        - contamination: Toxic fuel cleanup (hydrazine, UDMH)
        - mechanical_damage: Crater restoration and terrain rehabilitation
        
        Sources: Kazakhstan Ministry of Ecology (2023), FAO restoration cost database
        """
        # Unit costs in KZT per hectare (Task 5.1 lines 659-665)
        self.costs_kzt = {
            'vegetation_loss': 50000,      # KZT/ha - Forest restoration
            'soil_degradation': 30000,     # KZT/ha - Soil remediation
            'fire_risk': 20000,           # KZT/ha - Fire suppression
            'contamination': 40000,        # KZT/ha - Toxic fuel cleanup
            'mechanical_damage': 25000,    # KZT/ha - Crater restoration
        }
        self.usd_to_kzt = usd_to_kzt  # Exchange rate
    
    def _calculate_vegetation_cost(self, otu_results: np.ndarray, area_ha: float) -> float:
        """
        Calculate vegetation restoration cost.
        
        Formula: Cost = vegetation_loss * (1 - q_ndvi) * area_ha
        Where q_ndvi is vegetation health index (0-1)
        """
        if len(otu_results) == 0:
            return 0.0
        
        # Extract vegetation health (q_ndvi) from OTU results
        # Assuming otu_results structure: [q_ndvi, q_si, q_bi, q_relief, q_otu, q_fire]
        q_ndvi = otu_results[:, 0] if otu_results.ndim > 1 else otu_results[0]
        
        # Damage factor: lower NDVI = higher damage
        vegetation_damage = 1.0 - q_ndvi
        
        # Total cost
        total_cost = np.sum(self.costs_kzt['vegetation_loss'] * vegetation_damage) * area_ha
        return float(total_cost)
    
    def _calculate_soil_cost(self, otu_results: np.ndarray, area_ha: float) -> float:
        """
        Calculate soil degradation cost.
        
        Formula: Cost = soil_degradation * (1 - avg(q_si, q_bi)) * area_ha
        Where q_si is soil strength, q_bi is soil quality
        """
        if len(otu_results) == 0:
            return 0.0
        
        # Extract soil indices
        q_si = otu_results[:, 1] if otu_results.ndim > 1 else otu_results[1]
        q_bi = otu_results[:, 2] if otu_results.ndim > 1 else otu_results[2]
        
        # Combined soil damage factor
        soil_damage = 1.0 - (q_si + q_bi) / 2.0
        
        # Total cost
        total_cost = np.sum(self.costs_kzt['soil_degradation'] * soil_damage) * area_ha
        return float(total_cost)
    
    def _calculate_fire_cost(self, otu_results: np.ndarray, area_ha: float) -> float:
        """
        Calculate fire risk cost.
        
        Formula: Cost = fire_risk * q_fire * area_ha
        Where q_fire is fire risk index (0-1)
        """
        if len(otu_results) == 0:
            return 0.0
        
        # Extract fire risk (q_fire) - typically last column
        q_fire = otu_results[:, 5] if otu_results.shape[1] > 5 else np.zeros(len(otu_results))
        
        # Fire risk directly proportional to q_fire
        total_cost = np.sum(self.costs_kzt['fire_risk'] * q_fire) * area_ha
        return float(total_cost)
    
    def _calculate_contamination_cost(self, otu_results: np.ndarray, area_ha: float) -> float:
        """
        Calculate contamination cleanup cost (toxic fuel).
        
        Formula: Cost = contamination * contamination_factor * area_ha
        Contamination factor based on soil permeability and vegetation vulnerability.
        Simplified: contamination_factor = (1 - q_bi) * (1 - q_ndvi)
        """
        if len(otu_results) == 0:
            return 0.0
        
        # Extract relevant indices
        q_bi = otu_results[:, 2] if otu_results.ndim > 1 else otu_results[2]
        q_ndvi = otu_results[:, 0] if otu_results.ndim > 1 else otu_results[0]
        
        # Contamination factor: higher for poor soil quality and vegetation
        contamination_factor = (1.0 - q_bi) * (1.0 - q_ndvi)
        
        # Total cost
        total_cost = np.sum(self.costs_kzt['contamination'] * contamination_factor) * area_ha
        return float(total_cost)
    
    def _calculate_mechanical_cost(self, otu_results: np.ndarray, area_ha: float) -> float:
        """
        Calculate mechanical damage cost (impact craters).
        
        Formula: Cost = mechanical_damage * mechanical_factor * area_ha
        Mechanical factor based on relief complexity and soil strength.
        Simplified: mechanical_factor = (1 - q_si) * (1 - q_relief)
        """
        if len(otu_results) == 0:
            return 0.0
        
        # Extract relevant indices
        q_si = otu_results[:, 1] if otu_results.ndim > 1 else otu_results[1]
        q_relief = otu_results[:, 3] if otu_results.shape[1] > 3 else np.ones(len(otu_results))
        
        # Mechanical factor: higher for weak soil and complex relief
        mechanical_factor = (1.0 - q_si) * (1.0 - q_relief)
        
        # Total cost
        total_cost = np.sum(self.costs_kzt['mechanical_damage'] * mechanical_factor) * area_ha
        return float(total_cost)
    
    def calculate_total_damage(self, otu_results: np.ndarray, cell_size_km: float = 1.0) -> Dict[str, Any]:
        """
        Calculate all damage components for OTU cells.
        
        Implements Task 5.1 lines 668-693 from IMPLEMENTATION_ROADMAP.md.
        
        Args:
            otu_results: Array with columns [q_ndvi, q_si, q_bi, q_relief, q_otu, q_fire]
            cell_size_km: Size of each OTU cell in kilometers (default 1.0 km)
            
        Returns:
            Dictionary with all cost components in KZT and USD
        """
        # Calculate total area in hectares
        n_cells = len(otu_results)
        cell_area_ha = cell_size_km ** 2 * 100  # 1 km² = 100 ha
        total_area_ha = n_cells * cell_area_ha
        
        # Calculate all cost components
        veg_cost = self._calculate_vegetation_cost(otu_results, cell_area_ha)
        soil_cost = self._calculate_soil_cost(otu_results, cell_area_ha)
        fire_cost = self._calculate_fire_cost(otu_results, cell_area_ha)
        contam_cost = self._calculate_contamination_cost(otu_results, cell_area_ha)
        mech_cost = self._calculate_mechanical_cost(otu_results, cell_area_ha)
        
        # Total costs
        total_kzt = veg_cost + soil_cost + fire_cost + contam_cost + mech_cost
        total_usd = total_kzt / self.usd_to_kzt
        
        # Component percentages
        total_nonzero = total_kzt if total_kzt > 0 else 1.0
        percentages = {
            'vegetation_pct': (veg_cost / total_nonzero) * 100,
            'soil_pct': (soil_cost / total_nonzero) * 100,
            'fire_pct': (fire_cost / total_nonzero) * 100,
            'contamination_pct': (contam_cost / total_nonzero) * 100,
            'mechanical_pct': (mech_cost / total_nonzero) * 100,
        }
        
        return {
            'total_area_ha': total_area_ha,
            'num_cells': n_cells,
            'cell_area_ha': cell_area_ha,
            'vegetation_cost_kzt': veg_cost,
            'soil_cost_kzt': soil_cost,
            'fire_cost_kzt': fire_cost,
            'contamination_cost_kzt': contam_cost,
            'mechanical_cost_kzt': mech_cost,
            'grand_total_kzt': total_kzt,
            'grand_total_usd': total_usd,
            'percentages': percentages,
            'exchange_rate': self.usd_to_kzt,
        }


# ============================================================================
# LEGACY FUNCTIONS (maintained for backward compatibility)
# ============================================================================

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


# ============================================================================
# CONVENIENCE FUNCTION FOR NEW CALCULATOR
# ============================================================================

def calculate_comprehensive_damage(
    otu_results: np.ndarray,
    cell_size_km: float = 1.0,
    usd_to_kzt: float = 450.0
) -> Dict[str, Any]:
    """
    Convenience function to use the new EconomicDamageCalculator.
    
    Args:
        otu_results: Array with OTU indices
        cell_size_km: Cell size in kilometers
        usd_to_kzt: Exchange rate USD to KZT
        
    Returns:
        Dictionary with comprehensive damage assessment
    """
    calculator = EconomicDamageCalculator(usd_to_kzt=usd_to_kzt)
    return calculator.calculate_total_damage(otu_results, cell_size_km)