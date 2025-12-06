"""Simplified atmosphere model based on an exponential profile."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Protocol


@dataclass(frozen=True)
class AtmosphericProfile:
    """Parameters describing a single-layer exponential atmosphere."""

    scale_height_m: float
    surface_density_kg_m3: float
    surface_temperature_k: float


class Atmosphere(Protocol):
    """Interface for atmosphere models."""

    def density(self, altitude_m: float, *, density_factor: float = 1.0) -> float:
        """Return air density at a specific altitude."""

    def temperature(self, altitude_m: float) -> float:
        """Return temperature at a specific altitude."""


class ExponentialAtmosphere:
    """One-layer exponential atmosphere good enough for early prototyping."""

    def __init__(self, profile: AtmosphericProfile | None = None) -> None:
        self._profile = profile or AtmosphericProfile(
            scale_height_m=8_500.0,
            surface_density_kg_m3=1.225,
            surface_temperature_k=288.15,
        )

    def density(self, altitude_m: float, *, density_factor: float = 1.0) -> float:
        altitude = max(altitude_m, 0.0)
        decay = math.exp(-altitude / self._profile.scale_height_m)
        return self._profile.surface_density_kg_m3 * decay * density_factor

    def temperature(self, altitude_m: float) -> float:
        lapse_rate = -0.0065  # K/m up to 11 km (ISA assumption)
        sea_level = self._profile.surface_temperature_k
        capped_altitude = min(max(altitude_m, 0.0), 11_000.0)
        return sea_level + lapse_rate * capped_altitude
