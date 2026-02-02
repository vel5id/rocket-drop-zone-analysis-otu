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
    
    # Date parameters for temporal analysis
    target_date: str = Field(default="2024-09-09", description="Target date for NDVI (YYYY-MM-DD)")
    start_date: Optional[str] = Field(default=None, description="Start date for temporal range (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date for temporal range (YYYY-MM-DD)")
    
    # Separation parameters
    sep_altitude: float = Field(default=43000.0, description="Separation altitude (m)")
    sep_velocity: float = Field(default=1738.0, description="Separation velocity (m/s)")
    sep_fp_angle: float = Field(default=25.0, description="Separation flight path angle (deg)")
    sep_azimuth: float = Field(default=0.0, description="Separation azimuth relative to launch azimuth (deg)")
    
    # Zone preset override
    zone_id: Optional[str] = Field(default=None, description="Predefined zone ID (overrides launch params)")

    # Rocket parameters
    rocket_dry_mass: float = Field(default=30600.0, description="Stage dry mass (kg)")
    rocket_ref_area: float = Field(default=43.0, description="Stage reference area (m2)")
    
    # Advanced flags
    hurricane_mode: bool = Field(default=False, description="Enable high-entropy hurricane weather interpretation")
    cloud_threshold: int = Field(default=30, ge=0, le=100, description="Maximum cloud cover percentage (0-100)")


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
    message: Optional[str] = None
    analysis_id: Optional[str] = None  # <--- Telemetry Analysis ID


class OTUResponse(BaseModel):
    """OTU calculation response."""
    job_id: str
    status: str
    otu_grid: Optional[GeoJSONFeatureCollection] = None
    statistics: Optional[Dict[str, float]] = None
    otu_mean: float = 0.0


class TrajectoryPoint(BaseModel):
    """Single point in a trajectory."""
    lat: float
    lon: float
    alt: float  # meters
    velocity: float  # m/s
    time: float  # seconds form launch


class TrajectoryResponse(BaseModel):
    """Response for trajectory preview."""
    path: List[TrajectoryPoint]
    impact_point: TrajectoryPoint


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    version: str = "1.0.0"


class TelemetryExportResponse(BaseModel):
    """Response for telemetry export."""
    analysis_id: str
    export_path: str
    message: str
    files_included: list[str] = []


class ZonePreviewResponse(BaseModel):
    """Response for zone geometry preview."""
    zone_id: Optional[str] = None
    primary_polygon: Optional[GeoJSONFeature] = None
    fragment_polygon: Optional[GeoJSONFeature] = None
    message: Optional[str] = None

