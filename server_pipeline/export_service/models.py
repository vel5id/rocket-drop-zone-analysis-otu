"""
Export Service Data Models.

Defines the structures for data exchange within the Report Generation Service.
Strict typing enforced for scientific rigour.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ExportRequest(BaseModel):
    """Request to generate a full report package."""
    job_id: str = Field(..., description="ID of the completed simulation job")
    analysis_id: Optional[str] = Field(None, description="Optional telemetry ID")
    format: str = Field("csv", description="Output format (csv/excel)")
    include_time_series: bool = Field(False, description="Whether to include historical time series (expensive)")

class CostBreakdown(BaseModel):
    """Economic cost breakdown for a single OTU cell."""
    c_fire: float
    c_soil_strength: float
    c_soil_quality: float
    c_vegetation: float
    c_total: float
    currency: str = "USD"

class OTUExtendedRecord(BaseModel):
    """
    Comprehensive OTU record for export.
    Matches the reviewer's requested CSV structure.
    """
    # Identification
    otu_id: str
    lat: float
    lon: float
    
    # Physical Properties
    area_km2: float
    slope_deg: float
    aspect_deg: float
    elevation_m: float
    water_dist_m: float
    
    # Vegetation
    ndvi: float
    vegetation_type: str
    fire_hazard_qfi: float
    
    # Soil
    soil_type: str
    q_si: float
    q_bi: float
    
    # OTU Components
    q_relief: float
    q_otu: float
    stability_class: str
    
    # Economics
    economic_cost: float
    recommended_landing: str
    
    # Raw Data (for audit)
    raw_soil_bd: Optional[float] = None
    raw_soil_clay: Optional[float] = None
    
class SceneMetadata(BaseModel):
    """Sentinel-2 Scene Metadata."""
    scene_id: str
    date: str
    cloud_cover_pct: float
    processing_baseline: str
    status: str = "Included"
    notes: Optional[str] = None
