"""Temporal Analyzer for multi-year OTU analysis.

!!! PHASE 2 - DO NOT RUN WITHOUT USER CONFIRMATION !!!

This module provides functions for calculating OTU time series
from 2017 to 2025, computing weighted means, and analyzing dynamics.

These functions are STUBS that raise NotImplementedError.
They will be implemented in Phase 2 with user approval.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple, Generator
from pathlib import Path

import numpy as np


# ============================================================================
# PHASE 2 STUBS - DO NOT RUN WITHOUT USER CONFIRMATION
# ============================================================================


class Phase2NotImplementedError(NotImplementedError):
    """Custom error for Phase 2 functions."""
    
    def __init__(self, func_name: str):
        super().__init__(
            f"\n{'='*60}\n"
            f"PHASE 2 FUNCTION: {func_name}\n"
            f"{'='*60}\n"
            f"This function is a stub for Phase 2 implementation.\n"
            f"\n"
            f"Running multi-year analysis (2017-2025) will:\n"
            f"  - Make 500+ requests to Google Earth Engine\n"
            f"  - Take several hours to complete\n"
            f"  - Use significant GEE quota\n"
            f"\n"
            f"!!! DO NOT RUN WITHOUT EXPLICIT USER CONFIRMATION !!!\n"
            f"{'='*60}"
        )


@dataclass
class TemporalConfig:
    """Configuration for temporal analysis."""
    start_year: int = 2017
    end_year: int = 2025
    frequency: str = "monthly"  # "daily", "weekly", "monthly", "seasonal", "annual"
    
    # Season definitions (month ranges)
    seasons: Dict[str, Tuple[int, int]] = None
    
    def __post_init__(self):
        if self.seasons is None:
            self.seasons = {
                "spring": (3, 5),   # March-May
                "summer": (6, 8),   # June-August
                "autumn": (9, 11),  # September-November
                "winter": (12, 2),  # December-February
            }


def generate_date_range(
    start_year: int = 2017,
    end_year: int = 2025,
    frequency: str = "monthly",
) -> Generator[str, None, None]:
    """
    [PHASE 2 STUB] Generate date range for temporal analysis.
    
    Args:
        start_year: Starting year
        end_year: Ending year (inclusive)
        frequency: One of "daily", "weekly", "monthly", "seasonal", "annual"
    
    Yields:
        Date strings in YYYY-MM-DD format
    
    Example:
        >>> list(generate_date_range(2023, 2023, "monthly"))
        ['2023-01-15', '2023-02-15', ..., '2023-12-15']
    """
    # This is a preview of the function - it works but the full pipeline doesn't
    if frequency == "monthly":
        for year in range(start_year, end_year + 1):
            for month in range(1, 13):
                yield f"{year}-{month:02d}-15"
    
    elif frequency == "seasonal":
        for year in range(start_year, end_year + 1):
            for season, (start_month, _) in [
                ("spring", 4), ("summer", 7), ("autumn", 10), ("winter", 1)
            ]:
                m = start_month if isinstance(start_month, int) else 1
                yield f"{year}-{m:02d}-15"
    
    elif frequency == "annual":
        for year in range(start_year, end_year + 1):
            yield f"{year}-07-15"  # Mid-year for vegetation peak
    
    else:
        raise ValueError(f"Unknown frequency: {frequency}")


def calculate_otu_time_series(
    grid_cells: List,
    start_year: int = 2017,
    end_year: int = 2025,
    frequency: str = "monthly",
    cache_dir: str = "output/otu_cache",
) -> Dict[str, np.ndarray]:
    """
    [PHASE 2] Calculate OTU for a time series of dates.
    
    !!! DO NOT RUN WITHOUT USER CONFIRMATION !!!
    
    This will make 500+ requests to GEE and take several hours.
    
    Args:
        grid_cells: List of GridCell objects
        start_year: Starting year (default 2017)
        end_year: Ending year (default 2025)
        frequency: Temporal frequency
        cache_dir: Cache directory
    
    Returns:
        Dictionary with:
        - "dates": List of date strings
        - "otu_matrix": (n_cells, n_dates) array of OTU values
        - "cell_ids": List of cell IDs
    
    Raises:
        Phase2NotImplementedError: Always, until Phase 2 is implemented
    """
    raise Phase2NotImplementedError("calculate_otu_time_series")


def calculate_weighted_rms(
    otu_matrix: np.ndarray,
    weights: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    [PHASE 2] Calculate weighted Root Mean Square of OTU values.
    
    Formula: RMS_i = sqrt(sum(w_t * OTU_it^2) / sum(w_t))
    
    For each grid cell i, computes the weighted RMS across all time steps t.
    
    Args:
        otu_matrix: (n_cells, n_dates) array of OTU values
        weights: Optional (n_dates,) array of temporal weights
                 If None, uses uniform weights
    
    Returns:
        (n_cells,) array of weighted RMS values
    
    Raises:
        Phase2NotImplementedError: Always, until Phase 2 is implemented
    """
    raise Phase2NotImplementedError("calculate_weighted_rms")


def calculate_weighted_mean(
    otu_matrix: np.ndarray,
    weights: Optional[np.ndarray] = None,
) -> np.ndarray:
    """
    [PHASE 2] Calculate weighted mean of OTU values.
    
    Formula: Mean_i = sum(w_t * OTU_it) / sum(w_t)
    
    Args:
        otu_matrix: (n_cells, n_dates) array
        weights: Optional (n_dates,) array of temporal weights
    
    Returns:
        (n_cells,) array of weighted means
    
    Raises:
        Phase2NotImplementedError: Always, until Phase 2 is implemented
    """
    raise Phase2NotImplementedError("calculate_weighted_mean")


def analyze_otu_dynamics(
    otu_matrix: np.ndarray,
    dates: List[str],
    method: str = "trend",
) -> Dict[str, Any]:
    """
    [PHASE 2] Analyze temporal dynamics of OTU values.
    
    Methods:
    - "trend": Linear trend analysis (slope, significance)
    - "seasonal": Seasonal decomposition (trend + seasonal + residual)
    - "anomaly": Detect anomalies (values outside 2σ)
    - "change": Change point detection
    
    Args:
        otu_matrix: (n_cells, n_dates) array
        dates: List of date strings
        method: Analysis method
    
    Returns:
        Dictionary with analysis results:
        - For "trend": slopes, p_values, r_squared
        - For "seasonal": seasonal_component, trend_component, residuals
        - For "anomaly": anomaly_mask, z_scores
        - For "change": change_points, magnitudes
    
    Raises:
        Phase2NotImplementedError: Always, until Phase 2 is implemented
    """
    raise Phase2NotImplementedError("analyze_otu_dynamics")


def generate_temporal_report(
    otu_time_series: Dict[str, np.ndarray],
    dynamics_analysis: Dict[str, Any],
    output_path: str = "output/otu_temporal_report.html",
) -> str:
    """
    [PHASE 2] Generate HTML report with temporal analysis results.
    
    Includes:
    - Time series plots for each cell
    - Trend maps
    - Seasonal patterns
    - Anomaly detection results
    
    Args:
        otu_time_series: Output from calculate_otu_time_series
        dynamics_analysis: Output from analyze_otu_dynamics
        output_path: Output HTML file path
    
    Returns:
        Path to generated report
    
    Raises:
        Phase2NotImplementedError: Always, until Phase 2 is implemented
    """
    raise Phase2NotImplementedError("generate_temporal_report")


# ============================================================================
# HELPER FUNCTIONS (These work, but the main functions don't)
# ============================================================================


def estimate_gee_requests(
    n_cells: int,
    start_year: int = 2017,
    end_year: int = 2025,
    frequency: str = "monthly",
) -> Dict[str, Any]:
    """
    Estimate the number of GEE requests for a temporal analysis.
    
    This function DOES work - use it to plan your analysis.
    
    Args:
        n_cells: Number of grid cells
        start_year: Starting year
        end_year: Ending year
        frequency: Temporal frequency
    
    Returns:
        Dictionary with estimates:
        - n_dates: Number of dates
        - n_requests: Total API requests
        - estimated_time_hours: Rough time estimate
        - gee_quota_warning: Whether quota may be exceeded
    """
    # Count dates
    n_dates = len(list(generate_date_range(start_year, end_year, frequency)))
    
    # Each cell needs 3 requests (NDVI, soil, relief) per date
    # But soil and relief are static, so only 1 request per cell
    n_ndvi_requests = n_cells * n_dates
    n_static_requests = n_cells * 2  # soil + relief
    n_total_requests = n_ndvi_requests + n_static_requests
    
    # Estimate time (rough: 0.5 sec per request)
    estimated_time_sec = n_total_requests * 0.5
    estimated_time_hours = estimated_time_sec / 3600
    
    # GEE quota: ~10,000 requests per day for free tier
    gee_quota_warning = n_total_requests > 10000
    
    return {
        "n_cells": n_cells,
        "n_dates": n_dates,
        "n_ndvi_requests": n_ndvi_requests,
        "n_static_requests": n_static_requests,
        "n_total_requests": n_total_requests,
        "estimated_time_hours": round(estimated_time_hours, 2),
        "gee_quota_warning": gee_quota_warning,
        "frequency": frequency,
        "date_range": f"{start_year}-{end_year}",
    }


def print_phase2_estimate(n_cells: int) -> None:
    """Print an estimate for Phase 2 analysis."""
    estimate = estimate_gee_requests(n_cells)
    
    print("\n" + "="*60)
    print("PHASE 2 ESTIMATE - Multi-Year OTU Analysis")
    print("="*60)
    print(f"  Grid cells:        {estimate['n_cells']}")
    print(f"  Date range:        {estimate['date_range']}")
    print(f"  Frequency:         {estimate['frequency']}")
    print(f"  Number of dates:   {estimate['n_dates']}")
    print(f"  Total API calls:   {estimate['n_total_requests']:,}")
    print(f"  Estimated time:    {estimate['estimated_time_hours']:.1f} hours")
    
    if estimate['gee_quota_warning']:
        print("\n  ⚠️  WARNING: May exceed GEE daily quota!")
        print("     Consider splitting into multiple days.")
    
    print("="*60)
    print("  !!! DO NOT RUN WITHOUT USER CONFIRMATION !!!")
    print("="*60)


if __name__ == "__main__":
    # Example: estimate for 1000 cells
    print_phase2_estimate(1000)
    
    # Try to run a phase 2 function (will fail)
    try:
        calculate_otu_time_series([], 2017, 2025)
    except Phase2NotImplementedError as e:
        print(f"\nExpected error:\n{e}")
