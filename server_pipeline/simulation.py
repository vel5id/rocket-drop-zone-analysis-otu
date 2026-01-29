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
    date_config: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_ellipse": self.primary_ellipse,
            "fragment_ellipse": self.fragment_ellipse,
            "impact_points": self.impact_points,
            "otu_grid": self.otu_grid,
            "stats": self.stats,
            "date_config": self.date_config,
        }


def run_simulation_safe(
    iterations: int = 100,
    use_gpu: bool = True,
    launch_lat: float = 45.72341,
    launch_lon: float = 63.32275,
    azimuth: float = 45.0,
    target_date: str = "2024-09-09",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    sep_altitude: float = 43000.0,
    sep_velocity: float = 1738.0,
    sep_fp_angle: float = 25.0,
    sep_azimuth: float = 0.0,
    zone_id: Optional[str] = None,
    rocket_dry_mass: float = 30600.0,
    rocket_ref_area: float = 43.0,
    cell_size_km: float = 1.0,
    hurricane_mode: bool = False,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> SimulationResult:
    """
    Run complete simulation pipeline with safety limits.
    
    This is the main entry point for the UI backend.
    
    Steps:
        1. Monte Carlo simulation (run_pipeline.py) OR Zone Preset Lookup
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
    
    # Init variables
    primary_geo = []
    fragment_geo = []
    sim_time = 0
    filtered_fragments = []
    
    # =========================================================================
    # STEP 1: Monte Carlo Simulation OR Zone Preset
    # =========================================================================
    
    # CHECK FOR ZONE ID OVERRIDE
    if zone_id and zone_id.startswith("yu24_"):
        update(10, f"Using Zone Preset: {zone_id}...")
        from config.zones import YU24_ZONES
        
        # Determine which zones to use based on selection
        # Logic: If specific zone selected (e.g. 15), make it primary. 
        # If "all" or general, use both. 
        # For this implementation, we map specific IDs to the 15/25 split
        
        # Default behavior for now: Load both Zone 15 and 25 as Primary/Fragment
        # strict mapping implies:
        z15 = YU24_ZONES["yu24_15"]
        z25 = YU24_ZONES["yu24_25"]
        
        # Construct ellipse dicts directly
        primary_ellipse = {
            "center_lat": z15.center_lat,
            "center_lon": z15.center_lon,
            "semi_major_km": z15.semi_major_km,
            "semi_minor_km": z15.semi_minor_km,
            "angle_deg": z15.angle_deg,
        }
        
        fragment_ellipse = {
            "center_lat": z25.center_lat,
            "center_lon": z25.center_lon,
            "semi_major_km": z25.semi_major_km,
            "semi_minor_km": z25.semi_minor_km,
            "angle_deg": z25.angle_deg,
        }
        
        update(50, "Zone parameters loaded (Monte Carlo skipped)")
        
        # Skip straight to Grid Generation
        # (filtered_fragments remain empty as we don't have points)
        
    else:
        # NORMAL MONTE CARLO FLOW
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
            
            primary_geo, fragment_geo, sim_time = run_simulation_gpu(
                iterations, 
                show_progress=False,
                launch_lat=launch_lat,
                launch_lon=launch_lon,
                azimuth=azimuth,
                sep_altitude=sep_altitude,
                sep_velocity=sep_velocity,
                sep_fp_angle=sep_fp_angle,
                sep_azimuth=sep_azimuth,
                dry_mass_kg=rocket_dry_mass,
                reference_area_m2=rocket_ref_area,
                hurricane_mode=hurricane_mode,
            )
        else:
            update(15, "Running Standard Monte Carlo...")
            primary_geo, fragment_geo, sim_time = run_simulation_standard(
                iterations, 
                show_progress=False,
                launch_lat=launch_lat,
                launch_lon=launch_lon,
                azimuth=azimuth,
                sep_altitude=sep_altitude,
                sep_velocity=sep_velocity,
                sep_fp_angle=sep_fp_angle,
                sep_azimuth=sep_azimuth,
                dry_mass_kg=rocket_dry_mass,
                reference_area_m2=rocket_ref_area,
                hurricane_mode=hurricane_mode,
            )
        
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
    # STEP 4.5: Calculate OTU (NDVI/Relief)
    # =========================================================================
    update(89, "Calculating Ecological Indices (GEE)...")
    
    # We call the calculator logic here to populate properties in grid_cells
    try:
        from otu.calculator import calculate_otu_for_grid
        
        # We need to map our GridCell objects to the format expected by calculator 
        # or have calculator update them in place. 
        # calculate_otu_for_grid expects List[GridCell] (duck typed or actual objects)
        # and returns a dict with 'output_path' etc.
        # Ideally, it UPDATES the objects in place so they have .q_otu, .q_vi etc.
        
        # Let's inspect calculate_otu_for_grid -> creates ChunkManager -> runs calculation -> updates chunks (objects).
        # We need to ensure that the properties are preserved when converting to GeoJSON.
        # grid_to_geojson reads .q_otu etc from the objects.
        
        # Define callback to update UI with OTU sub-steps
        def otu_progress(msg: str):
            update(89, f"OTU: {msg}")

        calc_result = calculate_otu_for_grid(
            grid_cells=grid_cells,
            target_date=target_date,  # Use date from request
            output_dir="output/otu",  # Temporary or configured path
            show_progress=False,      # We handle progress here
            progress_callback=otu_progress
        )
        
        # CRITICAL FIX: Map calculated chunks back to grid_cells
        # ChunkManager.from_grid_cells preserves order, so we can zip them.
        processed_chunks = calc_result.get('chunks', [])
        if processed_chunks and len(processed_chunks) == len(grid_cells):
             for cell, chunk in zip(grid_cells, processed_chunks):
                 if chunk.is_processed:
                     cell.q_vi = chunk.q_vi
                     cell.q_si = chunk.q_si
                     cell.q_bi = chunk.q_bi
                     cell.q_relief = chunk.q_relief
                     cell.q_otu = chunk.q_otu
        
        # Verification Log
        if grid_cells:
            first_cell = grid_cells[0]
            if hasattr(first_cell, 'q_otu'):
                print(f"[Simulation] Verification: Cell 1 has OTU={first_cell.q_otu}")
            else:
                print("[Simulation] WARNING: Cell 1 has NO OTU attributes after mapping")

        # Check stats
        stats = calc_result.get('statistics', {})
        update(90, f"OTU Calculated. Mean: {stats.get('mean', 0):.3f}")
        
    except Exception as e:
        print(f"OTU Calculation Failed: {e}")
        update(90, "OTU Calculation Skipped (Error)")
    
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
        },
        date_config={
            "target_date": target_date,
            "start_date": start_date,
            "end_date": end_date,
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
