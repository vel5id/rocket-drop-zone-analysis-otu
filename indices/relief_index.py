"""Relief and hydrology driven modifiers."""
from __future__ import annotations


def q_relief_from_metrics(*, slope_deg: float, water_fraction: float) -> float:
    """Combine slope and water presence penalties."""

    slope_penalty = max(0.0, 1.0 - slope_deg / 30.0)
    water_penalty = max(0.0, 1.0 - water_fraction)
    return max(0.0, min(1.0, slope_penalty * water_penalty))
