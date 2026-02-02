"""
GEE Data Fetcher for Export Service.

Handles interaction with Google Earth Engine to retrieve:
1. Sentinel-2 Scene Metadata
2. Extended environmental variables (Soil, Relief, Water Distance)
"""
import ee
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .models import SceneMetadata

# Initialize GEE (Assuming it's already initialized by the main pipeline, but safe to check)
try:
    if not ee.data._credentials:
        ee.Initialize()
except Exception:
    pass # logic handled elsewhere usually

def fetch_scene_metadata(
    bounds_coords: List[List[float]],
    target_date: str,
    search_window_days: int = 5
) -> List[SceneMetadata]:
    """
    Fetch metadata for Sentinel-2 scenes covering the area.
    
    Args:
        bounds_coords: Polygon coordinates [[lon, lat], ...]
        target_date: "YYYY-MM-DD"
        search_window_days: +/- days to search
        
    Returns:
        List of SceneMetadata objects
    """
    # 1. Define ROI
    roi = ee.Geometry.Polygon(bounds_coords)
    
    # 2. Time Range
    dt = datetime.strptime(target_date, "%Y-%m-%d")
    start_date = (dt - timedelta(days=search_window_days)).strftime("%Y-%m-%d")
    end_date = (dt + timedelta(days=search_window_days)).strftime("%Y-%m-%d")
    
    # 3. Query Collection
    # We use S2_SR_HARMONIZED matching the main pipeline
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 50)) # Loose filter, let user see what's there
    )
    
    # 4. Fetch Metadata
    # We only need the list of images, not the pixels
    image_list = collection.limit(20).getInfo().get("features", [])
    
    results = []
    for img in image_list:
        props = img.get("properties", {})
        
        # Parse ID and Date
        scene_id = props.get("PRODUCT_ID", img.get("id"))
        acq_date = datetime.utcfromtimestamp(props.get("system:time_start") / 1000).strftime("%Y-%m-%d")
        
        results.append(SceneMetadata(
            scene_id=scene_id,
            date=acq_date,
            cloud_cover_pct=round(props.get("CLOUDY_PIXEL_PERCENTAGE", 0.0), 2),
            processing_baseline=props.get("PROCESSING_BASELINE", "N/A"),
            status="Included" if acq_date == target_date else "Available",
            notes="Target date match" if acq_date == target_date else f"Offset matches search window"
        ))
        
    return results

def fetch_water_distance(
    points: List[ee.Geometry.Point],
    roi_bounds: ee.Geometry,
    batch_size: int = 1000
) -> List[float]:
    """
    Calculate distance to nearest water body (JRC Global Surface Water).
    
    Args:
        points: List of EE Points
        roi_bounds: Bounding box for processing
        batch_size: Number of points to process per GEE call
    
    Returns:
        List of distances in meters
    """
    # JRC Water Occurrence > 50% considered permanent water
    water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
    water_mask = water.gt(50)
    
    source = water_mask
    # Use larger neighborhood (2048 px * 30m ~= 60km) to avoid constant max values
    dist_px = source.fastDistanceTransform(2048, 'pixels', 'squared_euclidean').sqrt()
    dist_m = dist_px.multiply(30) # Approx 30m resolution
    
    all_results = [0.0] * len(points)
    
    # Process in batches
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        
        fc = ee.FeatureCollection([
            ee.Feature(p, {'idx': idx + i}) for idx, p in enumerate(batch)
        ])
        
        try:
            samples = dist_m.reduceRegions(
                collection=fc,
                reducer=ee.Reducer.first(),
                scale=30
            )
            
            features = samples.getInfo().get('features', [])
            for feat in features:
                idx = feat['properties']['idx']
                d = feat['properties'].get('first', 9999)
                all_results[idx] = float(d)
                
        except Exception as e:
            print(f"Batch {i//batch_size} failed in water dist: {e}")
            
    return all_results

def fetch_elevation(
    points: List[ee.Geometry.Point],
    batch_size: int = 2000
) -> List[float]:
    """Fetch SRTM Elevation."""
    dem = ee.Image("USGS/SRTMGL1_003")
    
    all_results = [0.0] * len(points)
    
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        
        fc = ee.FeatureCollection([
            ee.Feature(p, {'idx': idx + i}) for idx, p in enumerate(batch)
        ])
        
        try:
            samples = dem.reduceRegions(
                collection=fc,
                reducer=ee.Reducer.first(),
                scale=30
            )
            
            features = samples.getInfo().get('features', [])
            for feat in features:
                idx = feat['properties']['idx']
                val = feat['properties'].get('first', 0.0)
                all_results[idx] = float(val)
                
        except Exception as e:
            print(f"Batch {i//batch_size} failed in elevation: {e}")
        
    return all_results
