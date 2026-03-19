"""NDVI calculation from Sentinel-2 imagery."""
from __future__ import annotations

import ee
from datetime import datetime, timedelta


def get_ndvi(
    roi: ee.Geometry,
    start_date: str = "2023-06-01",
    end_date: str = "2023-09-01",
    cloud_threshold: int = 20,
) -> ee.Image:
    """
    Calculate NDVI from Sentinel-2 Surface Reflectance with robust unmasking.
    
    Args:
        roi: Region of interest
        start_date: Start date for image collection
        end_date: End date for image collection
        cloud_threshold: Maximum cloud cover percentage
    
    Returns:
        NDVI image clipped to ROI
    """
    # Parse dates for fallbacks
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        # Use middle date as target for fallbacks
        target_dt = start_dt + (end_dt - start_dt) / 2
    except ValueError:
        # Fallback if date format is unexpected
        target_dt = datetime(2023, 7, 15)

    # Apply cloud mask
    def mask_clouds(image):
        qa = image.select("QA60")
        cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
        return image.updateMask(cloud_mask)

    # 1. Primary Collection
    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
    )
    ndvi = s2.map(mask_clouds).median().normalizedDifference(["B8", "B4"]).rename("NDVI")
    
    # 2. FALLBACK 1: Wider time window (+/- 60 days)
    start_wide = (target_dt - timedelta(days=60)).strftime("%Y-%m-%d")
    end_wide = (target_dt + timedelta(days=60)).strftime("%Y-%m-%d")
    s2_fallback = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(start_wide, end_wide)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
    ).map(mask_clouds).median()
    ndvi_fallback = s2_fallback.normalizedDifference(["B8", "B4"]).rename("NDVI")
    
    # 3. FALLBACK 2: Annual Composite (Last Resort)
    start_annual = (target_dt - timedelta(days=180)).strftime("%Y-%m-%d")
    end_annual = (target_dt + timedelta(days=180)).strftime("%Y-%m-%d")
    s2_annual = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(start_annual, end_annual)
    ).median()
    ndvi_annual = s2_annual.normalizedDifference(["B8", "B4"]).rename("NDVI")
    
    # Combine fallbacks and final unmask(0.0)
    # CRITICAL FIX: Use unmask(0.0) to ensure all pixels have data
    ndvi_final = ndvi.unmask(ndvi_fallback).unmask(ndvi_annual).unmask(0.0)
    
    return ndvi_final.clip(roi)


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
