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
) -> None:
    """
    Run simulation in background thread using server_pipeline module.
    
    This is the main entry point called by the API.
    """
    def worker():
        try:
            update_job(job_id, status="running", progress=0, message="Starting pipeline...")
            
            # Import from server_pipeline
            from server_pipeline.simulation import run_simulation_safe
            
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
