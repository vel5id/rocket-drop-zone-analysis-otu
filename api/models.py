"""Pydantic models for API request/response validation."""
from __future__ import annotations

from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ============================================
# REQUEST MODELS
# ============================================

class SimulationRequest(BaseModel):
    """Request body for running a Monte Carlo simulation."""
    iterations: int = Field(default=1000, ge=10, le=50000, description="Number of Monte Carlo iterations")
    use_gpu: bool = Field(default=True, description="Enable GPU/parallel acceleration")
    launch_lat: float = Field(default=45.72341, description="Launch site latitude")
    launch_lon: float = Field(default=63.32275, description="Launch site longitude")
    azimuth: float = Field(default=45.0, ge=0, le=360, description="Launch azimuth in degrees")


class OTURequest(BaseModel):
    """Request body for OTU ecological index calculation."""
    target_date: str = Field(default="2024-09-09", description="Target date for NDVI (YYYY-MM-DD)")
    job_id: Optional[str] = Field(default=None, description="Use grid from existing simulation job")


# ============================================
# RESPONSE MODELS
# ============================================

class EllipseData(BaseModel):
    """Dispersion ellipse parameters."""
    center_lat: float
    center_lon: float
    semi_major_km: float
    semi_minor_km: float
    angle_deg: float


class SimulationStats(BaseModel):
    """Simulation statistics."""
    iterations: int
    simulation_time_s: float
    primary_impacts: int
    fragment_impacts: int
    grid_cells: int


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature."""
    type: str = "Feature"
    properties: dict
    geometry: dict


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection."""
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class SimulationResponse(BaseModel):
    """Full simulation results response."""
    job_id: str
    status: str  # "pending", "running", "completed", "failed"
    progress: int = Field(default=0, ge=0, le=100)
    primary_ellipse: Optional[EllipseData] = None
    fragment_ellipse: Optional[EllipseData] = None
    impact_points: Optional[GeoJSONFeatureCollection] = None
    otu_grid: Optional[GeoJSONFeatureCollection] = None
    stats: Optional[SimulationStats] = None
    error: Optional[str] = None


class SimulationStatusResponse(BaseModel):
    """Minimal status response for polling."""
    job_id: str
    status: str
    progress: int = 0
    message: Optional[str] = None  # <--- New field


class OTUResponse(BaseModel):
    """OTU calculation response."""
    job_id: str
    status: str
    otu_grid: Optional[GeoJSONFeatureCollection] = None
    statistics: Optional[dict] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"
