"""Simulation runner wrapper for API - uses server_pipeline module."""
from __future__ import annotations

import sys
import os
import uuid
import time
import threading
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class SimulationJob:
    """In-memory job state."""
    job_id: str
    status: str = "pending"  # pending, running, completed, failed
    progress: int = 0
    message: str = "Initializing..."
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: float = field(default_factory=time.time)


# In-memory job storage (can be replaced with Redis/DB later)
_jobs: Dict[str, SimulationJob] = {}
_jobs_lock = threading.Lock()


def create_job() -> str:
    """Create a new job and return its ID."""
    job_id = str(uuid.uuid4())[:8]
    with _jobs_lock:
        _jobs[job_id] = SimulationJob(job_id=job_id)
    return job_id


def get_job(job_id: str) -> Optional[SimulationJob]:
    """Get job by ID."""
    with _jobs_lock:
        return _jobs.get(job_id)


def update_job(job_id: str, **kwargs) -> None:
    """Update job fields."""
    with _jobs_lock:
        if job_id in _jobs:
            for key, value in kwargs.items():
                setattr(_jobs[job_id], key, value)


def run_simulation_async(
    job_id: str,
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
    hurricane_mode: bool = False,
    cloud_threshold: int = 30,
) -> None:
    """
    Run simulation in background thread using server_pipeline module.
    
    This is the main entry point called by the API.
    """
    def worker():
        try:
            update_job(job_id, status="running", progress=0, message="Initializing pipeline...")
            
            # Import from server_pipeline
            from server_pipeline.simulation import run_simulation_safe
            from config.otu_config import OTUConfig
            from scripts.sentinel_table_with_logging import run_extraction
            from pathlib import Path
            
            # 1. Update Cloud Threshold Configuration
            OTUConfig.gee.cloud_threshold = cloud_threshold
            
            # 2. Regenerate Sentinel-2 Tables (if not in mock mode implicitly)
            update_job(job_id, progress=5, message=f"Regenerating Sentinel tables (<{cloud_threshold}% cloud)...")
            try:
                table_output = Path("outputs/supplementary_tables")
                run_extraction(table_output, cloud_threshold=cloud_threshold, use_mock=False)
            except Exception as e:
                print(f"Warning: Sentinel table generation failed: {e}")
                # Don't fail the whole simulation for report generation failure
            
            # Progress callback to update job status
            def progress_callback(pct: int, msg: str):
                update_job(job_id, progress=pct, message=msg)
            
            # Run the safe pipeline with all protections
            result = run_simulation_safe(
                iterations=iterations,
                use_gpu=use_gpu,
                launch_lat=launch_lat,
                launch_lon=launch_lon,
                azimuth=azimuth,
                target_date=target_date,
                start_date=start_date,
                end_date=end_date,
                sep_altitude=sep_altitude,
                sep_velocity=sep_velocity,
                sep_fp_angle=sep_fp_angle,
                sep_azimuth=sep_azimuth,
                zone_id=zone_id,
                rocket_dry_mass=rocket_dry_mass,
                rocket_ref_area=rocket_ref_area,
                hurricane_mode=hurricane_mode,
                cell_size_km=1.0,
                progress_callback=progress_callback,
            )
            
            # Convert result to dict format expected by API
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
    
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()


def get_simulation_result(job_id: str) -> Optional[Dict[str, Any]]:
    """Get formatted simulation result for API response."""
    job = get_job(job_id)
    if not job:
        return None
    
    result = {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "error": job.error,
    }
    
    if job.result:
        result["primary_ellipse"] = job.result.get("primary_ellipse")
        result["fragment_ellipse"] = job.result.get("fragment_ellipse")
        result["impact_points"] = job.result.get("impact_points")
        result["otu_grid"] = job.result.get("otu_grid")
        result["stats"] = job.result.get("stats")
    
    return result
