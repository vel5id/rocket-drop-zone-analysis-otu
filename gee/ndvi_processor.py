"""NDVI calculation from Sentinel-2 imagery."""
from __future__ import annotations

import ee


def get_ndvi(
    roi: ee.Geometry,
    start_date: str = "2023-06-01",
    end_date: str = "2023-09-01",
    cloud_threshold: int = 20,
) -> ee.Image:
    """
    Calculate NDVI from Sentinel-2 Surface Reflectance.
    
    Args:
        roi: Region of interest
        start_date: Start date for image collection
        end_date: End date for image collection
        cloud_threshold: Maximum cloud cover percentage
    
    Returns:
        NDVI image clipped to ROI
    """
    # Sentinel-2 Surface Reflectance
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
    )
    
    # Apply cloud mask
    def mask_clouds(image):
        qa = image.select("QA60")
        cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
        return image.updateMask(cloud_mask)
    
    s2_masked = s2.map(mask_clouds)
    
    # Compute median composite
    composite = s2_masked.median()
    
    # Calculate NDVI: (NIR - Red) / (NIR + Red)
    ndvi = composite.normalizedDifference(["B8", "B4"]).rename("NDVI")
    
    return ndvi.clip(roi)


def get_vegetation_health(roi: ee.Geometry) -> ee.Image:
    """
    Calculate vegetation health index combining NDVI with seasonal trends.
    
    Returns:
        Vegetation health [0, 1] where 1 = healthiest
    """
    ndvi = get_ndvi(roi)
    
    # Normalize NDVI to [0, 1]
    # NDVI typically ranges from -0.2 (water) to 0.9 (dense vegetation)
    # For vegetation health, we focus on positive values
    health = ndvi.clamp(0, 1).rename("vegetation_health")
    
    return health
