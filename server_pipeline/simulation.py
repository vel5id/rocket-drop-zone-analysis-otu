"""
Main simulation runner for UI/Backend.

Adapts run_otu_pipeline.py workflow for UI with:
1. Safety limits on ellipse sizes
2. Grid cell caps
3. Progress callbacks
4. GeoJSON output format
"""
from __future__ import annotations

import sys
import os
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server_pipeline.ellipse import compute_ellipse_safe, filter_outliers_iqr
from server_pipeline.grid_generator import generate_grid_safe, create_ellipse_polygons
from server_pipeline.geojson import points_to_geojson, grid_to_geojson


@dataclass
class SimulationResult:
    """Complete simulation result for API response."""
    primary_ellipse: Optional[Dict] = None
    fragment_ellipse: Optional[Dict] = None
    impact_points: Dict = field(default_factory=dict)
    otu_grid: Dict = field(default_factory=dict)
    stats: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_ellipse": self.primary_ellipse,
            "fragment_ellipse": self.fragment_ellipse,
            "impact_points": self.impact_points,
            "otu_grid": self.otu_grid,
            "stats": self.stats,
        }


def run_simulation_safe(
    iterations: int = 100,
    use_gpu: bool = True,
    launch_lat: float = 45.72341,
    launch_lon: float = 63.32275,
    azimuth: float = 45.0,
    cell_size_km: float = 1.0,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> SimulationResult:
    """
    Run complete simulation pipeline with safety limits.
    
    This is the main entry point for the UI backend.
    
    Steps:
        1. Monte Carlo simulation (run_pipeline.py)
        2. Filter outliers from fragments
        3. Compute ellipses with size limits
        4. Generate grid with cell cap
        5. Convert to GeoJSON
    
    Args:
        iterations: Number of Monte Carlo iterations
        use_gpu: Use GPU/parallel acceleration
        launch_lat: Launch site latitude
        launch_lon: Launch site longitude
        azimuth: Launch azimuth in degrees
        cell_size_km: Grid cell size in km
        progress_callback: Optional callback(progress_pct, message)
    
    Returns:
        SimulationResult with all data in GeoJSON format
    """
    def update(pct: int, msg: str):
        if progress_callback:
            progress_callback(pct, msg)
        print(f"  [{pct:3d}%] {msg}")
    
    start_time = time.time()
    
    # =========================================================================
    # STEP 1: Monte Carlo Simulation
    # =========================================================================
    update(5, "Importing simulation modules...")
    
    from run_pipeline import run_simulation_gpu, run_simulation_standard
    
    update(10, f"Running Monte Carlo ({iterations} iterations)...")
    
    if use_gpu:
        try:
            from core.gpu_ballistics import HAS_NUMBA
            mode = "GPU" if HAS_NUMBA else "CPU (Parallel)"
            update(15, f"Running {mode} Monte Carlo...")
        except ImportError:
            update(15, "Running Monte Carlo...")
        
        primary_geo, fragment_geo, sim_time = run_simulation_gpu(iterations, show_progress=False)
    else:
        update(15, "Running Standard Monte Carlo...")
        primary_geo, fragment_geo, sim_time = run_simulation_standard(iterations, show_progress=False)
    
    update(50, f"Simulation complete: {len(primary_geo)} primary, {len(fragment_geo)} fragments")
    
    # =========================================================================
    # STEP 2: Filter Outliers (CRITICAL for fragments!)
    # =========================================================================
    update(55, "Filtering fragment outliers...")
    
    # Only filter fragments, not primary impacts
    filtered_fragments = filter_outliers_iqr(fragment_geo, factor=1.5)
    
    # =========================================================================
    # STEP 3: Compute Ellipses with Safety Limits
    # =========================================================================
    update(60, "Computing dispersion ellipses...")
    
    primary_ellipse = compute_ellipse_safe(primary_geo, filter_outliers=False, clamp=True)
    fragment_ellipse = compute_ellipse_safe(filtered_fragments, filter_outliers=False, clamp=True)
    
    if primary_ellipse:
        update(65, f"Primary: {primary_ellipse['semi_major_km']:.1f}x{primary_ellipse['semi_minor_km']:.1f} km")
    if fragment_ellipse:
        update(70, f"Fragment: {fragment_ellipse['semi_major_km']:.1f}x{fragment_ellipse['semi_minor_km']:.1f} km")
    
    # =========================================================================
    # STEP 4: Generate Grid
    # =========================================================================
    update(75, "Creating ellipse polygons...")
    
    polygons = create_ellipse_polygons(primary_ellipse, fragment_ellipse)
    
    update(80, "Generating ecological grid...")
    
    grid_cells = generate_grid_safe(
        polygons, 
        cell_size_km=cell_size_km,
        progress_callback=progress_callback,
    )
    
    update(88, f"Generated {len(grid_cells)} grid cells")
    
    # =========================================================================
    # STEP 5: Convert to GeoJSON
    # =========================================================================
    update(90, "Converting to GeoJSON...")
    
    # Combine all impact points
    all_points = primary_geo + fragment_geo
    impact_points_geojson = points_to_geojson(all_points)
    
    # Grid to GeoJSON (without OTU values for now - can be added later)
    grid_geojson = grid_to_geojson(grid_cells)
    
    # =========================================================================
    # STEP 6: Build Result
    # =========================================================================
    update(95, "Finalizing results...")
    
    elapsed = time.time() - start_time
    
    result = SimulationResult(
        primary_ellipse=primary_ellipse,
        fragment_ellipse=fragment_ellipse,
        impact_points=impact_points_geojson,
        otu_grid=grid_geojson,
        stats={
            "iterations": iterations,
            "simulation_time_s": round(sim_time, 2),
            "total_time_s": round(elapsed, 2),
            "primary_impacts": len(primary_geo),
            "fragment_impacts": len(fragment_geo),
            "filtered_fragments": len(filtered_fragments),
            "grid_cells": len(grid_cells),
        }
    )
    
    update(100, f"Done in {elapsed:.1f}s")
    
    return result


# For backwards compatibility with existing API
def run_simulation_async_wrapper(
    job_id: str,
    update_job: Callable,
    **kwargs,
) -> None:
    """
    Wrapper for async execution in API.
    
    Converts progress callbacks to job updates.
    """
    def progress_callback(pct: int, msg: str):
        update_job(job_id, progress=pct, message=msg)
    
    try:
        update_job(job_id, status="running", progress=0, message="Starting...")
        
        result = run_simulation_safe(
            progress_callback=progress_callback,
            **kwargs,
        )
        
        update_job(
            job_id, 
            status="completed", 
            progress=100, 
            message="Done",
            result=result.to_dict(),
        )
        
    except Exception as e:
        import traceback
        error_details = f"{str(e)}\nTraceback:\n{traceback.format_exc()}"
        print(f"JOB FAILED: {error_details}")
        update_job(job_id, status="failed", error=error_details, message="Failed")
