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
)
from .simulation_runner import (
    create_job,
    get_job,
    run_simulation_async,
    get_simulation_result,
)


app = FastAPI(
    title="Rocket Simulation API",
    description="Backend API for Monte Carlo rocket impact zone simulation",
    version="1.0.0",
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    
    # Start simulation in background
    run_simulation_async(
        job_id=job_id,
        iterations=request.iterations,
        use_gpu=request.use_gpu,
        launch_lat=request.launch_lat,
        launch_lon=request.launch_lon,
        azimuth=request.azimuth,
    )
    
    return SimulationStatusResponse(
        job_id=job_id,
        status="running",
        progress=0,
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
