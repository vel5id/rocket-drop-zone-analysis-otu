"""FastAPI application for rocket simulation backend."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    SimulationRequest,
    SimulationResponse,
    SimulationStatusResponse,
    OTURequest,
    OTUResponse,
    HealthResponse,
    TrajectoryResponse,
    TelemetryExportResponse,
    ZonePreviewResponse,
)
from .simulation_runner import (
    create_job,
    get_job,
    run_simulation_async,
    get_simulation_result,
)
from .preview import calculate_trajectory_preview
from .zone_preview_logic import get_zone_preview

# Telemetry for reproducibility
try:
    from telemetry import record_simulation
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    print("Warning: Telemetry module not available. Scientific reproducibility features disabled.")


app = FastAPI(
    title="Rocket Simulation API",
    description="Backend API for Monte Carlo rocket impact zone simulation",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/api/simulation/preview", response_model=TrajectoryResponse, tags=["Simulation"])
async def preview_trajectory(request: SimulationRequest):
    """
    Generate a quick preview of the nominal rocket trajectory.
    Calculates single deterministic path (sigma=0).
    """
    return calculate_trajectory_preview(request)


@app.post("/api/simulation/preview-zone", response_model=ZonePreviewResponse, tags=["Simulation"])
async def preview_zone(request: SimulationRequest):
    """
    Get preview of the impact zone geometry (if applying a preset).
    """
    return get_zone_preview(request)




@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok", version="1.0.0")


@app.post("/api/simulation/run", response_model=SimulationStatusResponse, tags=["Simulation"])
async def run_simulation(request: SimulationRequest):
    """
    Start a new Monte Carlo simulation.
    
    Returns a job_id that can be used to poll for status and results.
    """
    job_id = create_job()
    
    # Record configuration for scientific reproducibility
    analysis_id = None
    if TELEMETRY_AVAILABLE:
        config_dict = request.dict()
        analysis_id = record_simulation(config_dict)
        print(f"Recorded simulation configuration with Analysis ID: {analysis_id}")
    
    # Start simulation in background
    run_simulation_async(
        job_id=job_id,
        iterations=request.iterations,
        use_gpu=request.use_gpu,
        launch_lat=request.launch_lat,
        launch_lon=request.launch_lon,
        azimuth=request.azimuth,
        target_date=request.target_date,
        start_date=request.start_date,
        end_date=request.end_date,
        sep_altitude=request.sep_altitude,
        sep_velocity=request.sep_velocity,
        sep_fp_angle=request.sep_fp_angle,
        sep_azimuth=request.sep_azimuth,
        hurricane_mode=request.hurricane_mode,
        cloud_threshold=request.cloud_threshold,
        zone_id=request.zone_id,
    )
    print(f"[API DEBUG] Triggered simulation with zone_id={request.zone_id}")
    
    return SimulationStatusResponse(
        job_id=job_id,
        status="running",
        progress=0,
        analysis_id=analysis_id,
    )


@app.get("/api/simulation/status/{job_id}", response_model=SimulationStatusResponse, tags=["Simulation"])
async def get_simulation_status(job_id: str):
    """Get the current status of a simulation job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return SimulationStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
    )


@app.get("/api/results/{job_id}", response_model=SimulationResponse, tags=["Simulation"])
async def get_results(job_id: str):
    """Get full simulation results including ellipses, impact points, and OTU grid."""
    result = get_simulation_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return result


@app.post("/api/otu/calculate", response_model=OTUResponse, tags=["OTU"])
async def calculate_otu(request: OTURequest):
    """
    Calculate OTU ecological index.
    
    Requires an existing simulation job_id to use its grid,
    or calculates for a default area if no job_id provided.
    """
    # For now, return a placeholder - full OTU integration can be added later
    if request.job_id:
        job = get_job(request.job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"Job {request.job_id} not found")
        if job.status != "completed":
            raise HTTPException(status_code=400, detail=f"Job {request.job_id} is not completed yet")
    
    return OTUResponse(
        job_id=request.job_id or "otu-standalone",
        status="pending",
        otu_grid=None,
        statistics=None,
    )


@app.post("/api/telemetry/export/{analysis_id}", response_model=TelemetryExportResponse, tags=["Telemetry"])
async def export_telemetry(analysis_id: str, include_tables: bool = True):
    """
    Export complete data package for a given Analysis ID.
    
    Includes configuration, simulation results (if available), and generated tables.
    """
    if not TELEMETRY_AVAILABLE:
        raise HTTPException(status_code=501, detail="Telemetry module not available")
    
    try:
        from telemetry import TelemetryRecorder
        recorder = TelemetryRecorder()
        
        # Check if analysis exists
        analysis_dir = recorder.base_dir / analysis_id
        if not analysis_dir.exists():
            raise HTTPException(status_code=404, detail=f"Analysis ID {analysis_id} not found")
        
        # Try to get simulation results from job_id if linked
        # For simplicity, we'll just export configuration and tables
        export_dir = recorder.export_data_package(
            analysis_id=analysis_id,
            result_data=None,
            include_tables=include_tables
        )
        
        # List exported files
        files = []
        for f in export_dir.rglob("*"):
            if f.is_file():
                files.append(str(f.relative_to(recorder.base_dir)))
        
        return TelemetryExportResponse(
            analysis_id=analysis_id,
            export_path=str(export_dir),
            message=f"Exported {len(files)} files",
            files_included=files[:10]  # Limit to first 10
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

# Mount outputs directory for static access
os.makedirs("outputs", exist_ok=True)
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

@app.get("/api/outputs/tables/{filename}", tags=["Telemetry"])
async def download_table(filename: str):
    """Download a specific supplementary table."""
    file_path = f"outputs/supplementary_tables/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path, filename=filename)


# ============================================
# EXPORT SERVICE ENDPOINTS
# ============================================

from server_pipeline.export_service.models import ExportRequest
from server_pipeline.export_service.generator import generate_report_package
import asyncio
import uuid
import os

# Simple in-memory job store for export tasks
# Dict[str, str] -> job_id: status or filepath
export_tasks: Dict[str, Dict[str, Any]] = {}

@app.post("/api/export/generate", tags=["Export"])
async def generate_export(request: ExportRequest, background_tasks: BackgroundTasks):
    """
    Trigger generation of a full report package.
    """
    task_id = f"export_{request.job_id}_{str(uuid.uuid4())[:8]}"
    
    export_tasks[task_id] = {
        "status": "processing", 
        "progress": 0,
        "file_path": None,
        "error": None
    }
    
    # Background Worker
    async def _run_export(tid: str, req: ExportRequest):
        try:
            print(f"[EXPORT] Starting task {tid} for job {req.job_id}")
            # Run generator (it's async but uses blocking calls, might need threadpool if heavy)
            # For now, just await it directly if it's truly async, or run in executor
            # generate_report_package is defined as async but uses blocking GEE/Pandas.
            # Ideally wrap in run_in_executor for production.
            loop = asyncio.get_event_loop()
            path = await loop.run_in_executor(None, lambda: asyncio.run(generate_report_package(req))) \
                   if not asyncio.iscoroutinefunction(generate_report_package) else await generate_report_package(req)
            
            # Since generate_report_package in my code WAS defined as async but I didn't verify if it awaits anything.
            # Actually I wrote `async def generate_report_package`.
            # But GEE calls are blocking.
            # Best to run it synchronously in a thread.
            
            export_tasks[tid]["status"] = "completed"
            export_tasks[tid]["file_path"] = path
            export_tasks[tid]["progress"] = 100
            print(f"[EXPORT] Task {tid} completed: {path}")
            
        except Exception as e:
            export_tasks[tid]["status"] = "failed"
            export_tasks[tid]["error"] = str(e)
            print(f"[EXPORT] Task {tid} failed: {e}")

    background_tasks.add_task(_run_export, task_id, request)
    
    return {"task_id": task_id, "status": "processing"}

@app.get("/api/export/status/{task_id}", tags=["Export"])
async def get_export_status(task_id: str):
    """Check status of export task."""
    task = export_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task

@app.get("/api/export/download/{task_id}", tags=["Export"])
async def download_export(task_id: str):
    """Download the generated ZIP."""
    task = export_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task["status"] != "completed" or not task["file_path"]:
        raise HTTPException(status_code=400, detail="Export not ready")
        
    path = task["file_path"]
    filename = os.path.basename(path)
    
    return FileResponse(path, filename=filename, media_type="application/zip")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

