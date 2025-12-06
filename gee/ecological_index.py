"""Calculation of the composite ecological resilience index Q_OTU using GEE with real data."""
from __future__ import annotations

import os
import ee
import geemap

from gee.authenticator import initialize_ee, PROJECT_ID
from gee.soil_processor import get_soil_indices
from gee.dem_processor import get_relief_factor, get_terrain_analysis
from gee.water_processor import get_water_mask
from gee.ndvi_processor import get_ndvi


def calculate_ecological_index(
    center_lat: float = 47.35,
    center_lon: float = 66.5,
    buffer_m: int = 15000,
    output_dir: str = "output",
    weights: dict | None = None,
) -> tuple[ee.Image, ee.Geometry]:
    """
    Calculate Q_OTUi index over a region using real satellite data.
    
    Uses:
    - Sentinel-2 NDVI for vegetation (Q_Vi)
    - SoilGrids for soil strength and quality (Q_Si, Q_Bi)
    - SRTM + JRC/HydroSHEDS for relief factor (Q_relief)
    
    Formula: Q_OTUi = (k_Vi * Q_Vi + k_Si * Q_Si + k_Bi * Q_Bi) * Q_relief
    
    Args:
        center_lat: Latitude of ROI center
        center_lon: Longitude of ROI center  
        buffer_m: Buffer around center in meters
        output_dir: Directory for output files
        weights: Optional dict with k_vi, k_si, k_bi weights
    
    Returns:
        Tuple of (Q_OTUi image, ROI geometry)
    """
    # Initialize EE
    initialize_ee()
    
    # Default weights
    w = weights or {"k_vi": 0.35, "k_si": 0.35, "k_bi": 0.30}
    
    # Define region of interest
    point = ee.Geometry.Point([center_lon, center_lat])
    roi = point.buffer(buffer_m).bounds()
    
    print(f"Calculating ecological index for ({center_lat}, {center_lon}) ± {buffer_m/1000} km")

    # 1. Vegetation Index (Q_Vi) from NDVI
    print("  Fetching NDVI from Sentinel-2...")
    ndvi = get_ndvi(roi)
    q_vi = ndvi.max(0).rename("Q_Vi")  # Clip negative values

    # 2. Soil Indices from SoilGrids
    print("  Fetching soil data from SoilGrids...")
    q_si, q_bi = get_soil_indices(roi)

    # 3. Relief Factor
    print("  Calculating relief factor...")
    q_relief = get_relief_factor(roi)

    # 4. Calculate composite index
    print("  Computing Q_OTUi...")
    q_otui = (
        q_vi.multiply(w["k_vi"])
        .add(q_si.multiply(w["k_si"]))
        .add(q_bi.multiply(w["k_bi"]))
        .multiply(q_relief)
        .clamp(0, 1)
        .rename("Q_OTUi")
    )

    # 5. Visualization
    print("  Generating map...")
    terrain = get_terrain_analysis(roi)
    water = get_water_mask(roi)
    
    vis_q_otui = {"min": 0, "max": 1, "palette": ["red", "orange", "yellow", "lightgreen", "green"]}
    vis_ndvi = {"min": 0, "max": 0.8, "palette": ["brown", "yellow", "green"]}
    vis_soil = {"min": 0, "max": 1, "palette": ["white", "tan", "brown"]}
    
    Map = geemap.Map(center=[center_lat, center_lon], zoom=11)
    Map.addLayer(terrain["hillshade"], {"min": 0, "max": 255}, "Hillshade", False)
    Map.addLayer(ndvi, vis_ndvi, "NDVI", False)
    Map.addLayer(q_si, vis_soil, "Soil Strength (Q_Si)", False)
    Map.addLayer(q_bi, vis_soil, "Soil Quality (Q_Bi)", False)
    Map.addLayer(q_relief, {"min": 0, "max": 1, "palette": ["red", "yellow", "green"]}, "Relief Factor", False)
    Map.addLayer(water.selfMask(), {"palette": ["blue"]}, "Water Bodies", True)
    Map.addLayer(q_otui, vis_q_otui, "Ecological Index (Q_OTUi)", True)
    Map.addLayer(roi, {"color": "red"}, "ROI", True)

    # Save map
    os.makedirs(output_dir, exist_ok=True)
    output_html = os.path.join(output_dir, "ecological_index_map.html")
    Map.to_html(output_html)
    print(f"  Map saved to {output_html}")

    return q_otui, roi


def export_ecological_index(
    q_otui: ee.Image,
    roi: ee.Geometry,
    description: str = "ecological_index",
    scale: int = 1000,
) -> ee.batch.Task:
    """Export ecological index to Google Drive."""
    task = ee.batch.Export.image.toDrive(
        image=q_otui,
        description=description,
        folder="GEE_Exports",
        region=roi,
        scale=scale,
        crs="EPSG:4326",
        maxPixels=1e9,
    )
    task.start()
    print(f"Export task started: {description}")
    return task


if __name__ == "__main__":
    q_otui, roi = calculate_ecological_index()
    print("\n=== Ecological Index Calculation Complete ===")
