"""Global Monte Carlo simulation parameters with realistic perturbations."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Tuple


@dataclass(frozen=True)
class Perturbation:
    """Definition of a random perturbation."""
    distribution: str
    args: Tuple[float, ...]


@dataclass
class SimulationConfig:
    """Container that groups all simulation knobs."""
    iterations: int = 10_000
    random_seed: int = 42
    max_time_s: float = 600.0
    time_step_s: float = 0.5
    output_directory: str = "output/data"
    perturbations: Dict[str, Perturbation] = field(default_factory=dict)


# =============================================================================
# REALISTIC PERTURBATIONS FOR PROTON FIRST STAGE
# =============================================================================
# Based on open-source ballistic analysis and engineering estimates:
# - Thrust cutoff timing: ±2-3 seconds → velocity variation ±150-200 m/s
# - Propellant loading: ±0.5% → mass variation
# - Guidance errors: ±2-5° in angular quantities
# - High-altitude winds: 30-100 m/s jet streams at 10-40 km
# - Atmospheric density: ±10-15% due to seasonal/diurnal variations
#
# The 3σ dispersion ellipse for Proton stage 1:
# - Downrange: ~70-80 km (driven by velocity/thrust cutoff variations)
# - Crossrange: ~40-50 km (driven by azimuth/crosswind variations)
# =============================================================================

DEFAULT_PERTURBATIONS: Dict[str, Perturbation] = {
    # STANDARD ENGINEERING TOLERANCES (Inertial Guidance System Active)
    # ------------------------------------------------------------------
    # "Tight" ellipses representing nominal dispersion (High Precision)
    "initial_velocity": Perturbation("normal", (1_738.0, 5.0)),        # σ=5 m/s (Very precise cutoff)
    "initial_altitude": Perturbation("normal", (43_000.0, 200.0)),     # σ=200 m
    "flight_path_angle": Perturbation("normal", (25.0, 0.2)),          # σ=0.2° (High precision guidance)
    "azimuth": Perturbation("normal", (45.0, 0.3)),                    # σ=0.3° (Standard IGS accuracy)
    
    # Aerodynamics
    "drag_coefficient": Perturbation("uniform", (0.95, 1.05)),         # ±5% Cd
    "air_density_factor": Perturbation("normal", (1.0, 0.03)),         # σ=3% density (Standard Atmo)
    
    # Wind (Nominal)
    "wind_u": Perturbation("normal", (0.0, 10.0)),                     # σ=10 m/s along-track
    "wind_v": Perturbation("normal", (0.0, 5.0)),                      # σ=5 m/s cross-track (Reduced for thinner ellipses)
    
    # Mass
    "initial_mass": Perturbation("normal", (30_600.0, 100.0)),         # σ=100 kg
}

HURRICANE_PERTURBATIONS: Dict[str, Perturbation] = {
    # HIGH ENTROPY / FAILURE MODE (Tumbling / Hurricane)
    # ------------------------------------------------------------------
    # "Wide" ellipses representing worst-case scenarios
    "initial_velocity": Perturbation("normal", (1_738.0, 80.0)),       # σ=80 m/s
    "initial_altitude": Perturbation("normal", (43_000.0, 1_500.0)),   # σ=1.5 km
    "flight_path_angle": Perturbation("normal", (25.0, 3.0)),          # σ=3°
    "azimuth": Perturbation("normal", (45.0, 6.0)),                    # σ=6° (Large deviation)
    
    # Aerodynamics
    "drag_coefficient": Perturbation("uniform", (0.7, 1.5)),           # Wide Cd (Tumbling)
    "air_density_factor": Perturbation("normal", (1.0, 0.12)),         # σ=12% density
    
    # Wind (Extreme Weather)
    "wind_u": Perturbation("normal", (0.0, 30.0)),                     # σ=30 m/s
    "wind_v": Perturbation("normal", (0.0, 60.0)),                     # σ=60 m/s (Hurricane gusts)
    
    # Mass
    "initial_mass": Perturbation("normal", (30_600.0, 500.0)),         # σ=500 kg
}


def build_default_config() -> SimulationConfig:
    """Return a ready-to-use baseline configuration."""
    return SimulationConfig(perturbations=DEFAULT_PERTURBATIONS.copy())


# =============================================================================
# FRAGMENTATION MODEL PARAMETERS
# =============================================================================
# First stage can break up during reentry, creating secondary debris field
# Breakup typically occurs at 20-40 km altitude due to aerodynamic loads

@dataclass(frozen=True)
class FragmentationParams:
    """Parameters for modeling stage breakup during reentry."""
    # Breakup altitude range
    breakup_altitude_min_m: float = 20_000.0
    breakup_altitude_max_m: float = 40_000.0
    breakup_probability: float = 0.7  # 70% of cases have some breakup
    
    # Number of major fragments (engine blocks, tank sections)
    num_fragments_mean: int = 6
    num_fragments_sigma: int = 2
    
    # Fragment mass distribution (fraction of total mass)
    fragment_mass_fractions: Tuple[float, ...] = (0.25, 0.20, 0.15, 0.15, 0.12, 0.08, 0.05)
    
    # Additional velocity imparted during breakup (m/s)
    breakup_delta_v_mean: float = 50.0
    breakup_delta_v_sigma: float = 30.0
    
    # Angular spread during breakup (degrees)
    breakup_angle_sigma: float = 15.0


PROTON_FRAGMENTATION = FragmentationParams()
