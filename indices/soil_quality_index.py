"""Soil bonitet conversions."""
from __future__ import annotations


def q_bi_from_bonitet(bonitet_score: float) -> float:
    """Normalize soil bonitet (0..100) to [0, 1]."""

    clamped = max(0.0, min(100.0, bonitet_score))
    return clamped / 100.0
