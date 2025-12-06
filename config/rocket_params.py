"""Canonical Proton launch vehicle parameters used across the project."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RocketStageParameters:
    """Geometric and mass properties for a single stage."""

    diameter_m: float
    length_m: float
    dry_mass_kg: float
    propellant_mass_kg: float
    reference_area_m2: float


@dataclass(frozen=True)
class EngineParameters:
    """Aggregate engine block characteristics."""

    thrust_kN: float
    isp_sea_level_s: float
    isp_vacuum_s: float
    burn_time_s: float
    mass_flow_rate_kg_s: float


@dataclass(frozen=True)
class SeparationParameters:
    """Conditions at the moment the first stage separates."""

    altitude_mean_m: float
    altitude_sigma_m: float
    velocity_mean_m_s: float
    velocity_sigma_m_s: float
    flight_path_angle_mean_deg: float
    flight_path_angle_sigma_deg: float
    azimuth_mean_deg: float
    azimuth_sigma_deg: float
    range_to_impact_km: float


PROTON_STAGE_ONE = RocketStageParameters(
    diameter_m=7.4,
    length_m=21.18,
    dry_mass_kg=30_600.0,
    propellant_mass_kg=428_300.0,
    reference_area_m2=43.0,
)

PROTON_ENGINE_BLOCK = EngineParameters(
    thrust_kN=10_026.0,
    isp_sea_level_s=288.0,
    isp_vacuum_s=316.0,
    burn_time_s=123.0,
    mass_flow_rate_kg_s=10_026_000.0 / (9.80665 * 288.0),
)

PROTON_SEPARATION = SeparationParameters(
    altitude_mean_m=43_000.0,
    altitude_sigma_m=500.0,
    velocity_mean_m_s=1_738.0,
    velocity_sigma_m_s=30.0,
    flight_path_angle_mean_deg=25.0,
    flight_path_angle_sigma_deg=1.0,
    azimuth_mean_deg=45.0,
    azimuth_sigma_deg=0.5,
    range_to_impact_km=306.0,
)
