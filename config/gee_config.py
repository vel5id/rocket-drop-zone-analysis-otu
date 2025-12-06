"""IDs of Google Earth Engine datasets used for environmental scoring."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DatasetReference:
    """Represents a single GEE asset."""

    collection_id: str
    description: str
    scale_m: int


NDVI_DATASET = DatasetReference(
    collection_id="MODIS/061/MOD13A2",
    description="MODIS Terra vegetation indices (1 km, 16 day)",
    scale_m=1_000,
)

DEM_DATASET = DatasetReference(
    collection_id="USGS/SRTMGL1_003",
    description="SRTM 30 m global DEM",
    scale_m=30,
)

WATER_DATASET = DatasetReference(
    collection_id="JRC/GSW1_4/GlobalSurfaceWater",
    description="JRC surface water occurrence (30 m)",
    scale_m=30,
)

SOIL_DATASET = DatasetReference(
    collection_id="OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02",
    description="OpenLandMap clay fraction (250 m)",
    scale_m=250,
)
