"""Vegetation-specific helpers (Q_V)."""
from __future__ import annotations


def q_vi_from_ndvi(ndvi: float) -> float:
    """Transform NDVI [-1, 1] to Q_V [0, 1]."""

    return max(0.0, min(1.0, (ndvi + 1.0) * 0.5))
