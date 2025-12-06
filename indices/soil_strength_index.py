"""Protodyakonov strength conversion utilities."""
from __future__ import annotations


def q_si_from_strength(protodyakonov_value: float) -> float:
    """Convert Protodyakonov scale (0.3..20) to normalized [0, 1]."""

    value = max(0.3, min(20.0, protodyakonov_value))
    return (value - 0.3) / (20.0 - 0.3)
