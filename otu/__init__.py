"""OTU (Ecological Resilience Index) calculation module.

This module provides efficient calculation of Q_OTUi index for impact zones,
using chunked processing and local data caching for optimal performance.

Phase 1: Single day calculation
Phase 2: Multi-year temporal analysis (2017-2025) - stubs prepared
"""
from __future__ import annotations

from otu.calculator import OTUCalculator, calculate_otu_for_grid
from otu.chunk_manager import ChunkManager, Chunk

__all__ = [
    "OTUCalculator",
    "calculate_otu_for_grid",
    "ChunkManager",
    "Chunk",
]
