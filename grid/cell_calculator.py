"""Utilities that evaluate environmental layers for each grid cell."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass
class CellIndicators:
    """Normalized indicators consumed by the Q_OTU equation."""

    ndvi: float
    soil_strength: float
    soil_quality: float
    relief_factor: float


def build_cell_payload(raw_metrics: Dict[str, float]) -> CellIndicators:
    """Normalize raw measurements into the canonical indicator structure."""

    return CellIndicators(
        ndvi=raw_metrics.get("ndvi", 0.5),
        soil_strength=raw_metrics.get("soil_strength", 1.0),
        soil_quality=raw_metrics.get("soil_quality", 50.0) / 100.0,
        relief_factor=raw_metrics.get("relief_factor", 1.0),
    )
