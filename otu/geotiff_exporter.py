"""GeoTIFF exporter for OTU data layers.

Downloads raster data from GEE as GeoTIFF files for local processing:
- NDVI from Sentinel-2
- Soil indices from SoilGrids
- Relief from SRTM DEM
- Water mask from JRC
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Optional, Dict, Any
from datetime import datetime, timedelta

try:
    import ee
except ImportError:
    ee = None

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable


@dataclass
class ExportConfig:
    """Configuration for GeoTIFF export."""
    output_dir: str = "output/geotiff"
    scale: int = 10  # Resolution in meters (10m for Sentinel-2)
    crs: str = "EPSG:4326"
    max_pixels: int = 1e9
    
    # NDVI settings
    ndvi_window_days: int = 15
    cloud_threshold: int = 20


class GeoTIFFExporter:
    """
    Export GEE data as GeoTIFF files for local processing.
    
    Workflow:
    1. Define region from ellipse bounds
    2. Export NDVI, soil, relief as separate GeoTIFF files
    3. Download to local disk
    4. Process locally with GPU acceleration
    """
    
    def __init__(self, config: Optional[ExportConfig] = None):
        self.config = config or ExportConfig()
        self._ee_initialized = False
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
    
    def _init_ee(self) -> None:
        """Initialize Earth Engine."""
        if self._ee_initialized or ee is None:
            return
        
        try:
            ee.Initialize()
            self._ee_initialized = True
            print("  Earth Engine initialized")
        except Exception:
            try:
                ee.Authenticate()
                ee.Initialize()
                self._ee_initialized = True
            except Exception as e:
                raise RuntimeError(f"Could not initialize Earth Engine: {e}")
    
    def export_all_layers(
        self,
        bounds: Tuple[float, float, float, float],
        target_date: str = "2024-09-09",
        prefix: str = "otu",
        wait_for_completion: bool = True,
    ) -> Dict[str, str]:
        """
        Export all data layers as GeoTIFF files.
        
        Args:
            bounds: (min_lat, max_lat, min_lon, max_lon) bounding box
            target_date: Target date for NDVI in YYYY-MM-DD format
            prefix: Prefix for output filenames
            wait_for_completion: Wait for GEE export tasks to complete
        
        Returns:
            Dictionary with paths to exported files
        """
        self._init_ee()
        
        min_lat, max_lat, min_lon, max_lon = bounds
        roi = ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
        
        print(f"\nExporting GeoTIFF layers for region:")
        print(f"  Bounds: ({min_lat:.4f}, {max_lat:.4f}) x ({min_lon:.4f}, {max_lon:.4f})")
        print(f"  Target date: {target_date}")
        print(f"  Resolution: {self.config.scale}m")
        
        tasks = {}
        output_paths = {}
        
        # 1. Export NDVI
        print("\n[1/4] Preparing NDVI layer...")
        ndvi_image = self._prepare_ndvi(roi, target_date)
        ndvi_path = f"{prefix}_ndvi_{target_date}"
        tasks['ndvi'] = self._start_export(ndvi_image, roi, ndvi_path, scale=10)
        output_paths['ndvi'] = os.path.join(self.config.output_dir, f"{ndvi_path}.tif")
        
        # 2. Export Soil Strength (Q_Si)
        print("[2/4] Preparing Soil Strength layer...")
        q_si_image = self._prepare_soil_strength(roi)
        q_si_path = f"{prefix}_soil_strength"
        tasks['q_si'] = self._start_export(q_si_image, roi, q_si_path, scale=250)
        output_paths['q_si'] = os.path.join(self.config.output_dir, f"{q_si_path}.tif")
        
        # 3. Export Soil Quality (Q_Bi)
        print("[3/4] Preparing Soil Quality layer...")
        q_bi_image = self._prepare_soil_quality(roi)
        q_bi_path = f"{prefix}_soil_quality"
        tasks['q_bi'] = self._start_export(q_bi_image, roi, q_bi_path, scale=250)
        output_paths['q_bi'] = os.path.join(self.config.output_dir, f"{q_bi_path}.tif")
        
        # 4. Export Relief Factor
        print("[4/4] Preparing Relief Factor layer...")
        relief_image = self._prepare_relief(roi)
        relief_path = f"{prefix}_relief"
        tasks['relief'] = self._start_export(relief_image, roi, relief_path, scale=30)
        output_paths['relief'] = os.path.join(self.config.output_dir, f"{relief_path}.tif")
        
        print(f"\n  Started {len(tasks)} export tasks")
        
        if wait_for_completion:
            self._wait_for_tasks(tasks)
        
        return output_paths
    
    def _prepare_ndvi(self, roi: "ee.Geometry", target_date: str) -> "ee.Image":
        """Prepare NDVI image from Sentinel-2."""
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        start_dt = target_dt - timedelta(days=self.config.ndvi_window_days)
        end_dt = target_dt + timedelta(days=self.config.ndvi_window_days)
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        
        print(f"    Date range: {start_str} to {end_str}")
        
        # Sentinel-2 Surface Reflectance
        s2 = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(roi)
            .filterDate(start_str, end_str)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", self.config.cloud_threshold))
        )
        
        # Cloud mask
        def mask_clouds(image):
            qa = image.select("QA60")
            cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
            return image.updateMask(cloud_mask)
        
        s2_masked = s2.map(mask_clouds)
        composite = s2_masked.median()
        
        # NDVI
        ndvi = composite.normalizedDifference(["B8", "B4"]).rename("NDVI")
        
        # Clamp to [0, 1] for vegetation
        ndvi_clamped = ndvi.clamp(0, 1)
        
        return ndvi_clamped.clip(roi)
    
    def _prepare_soil_strength(self, roi: "ee.Geometry") -> "ee.Image":
        """Prepare Q_Si (soil strength) from SoilGrids."""
        bulk_density = ee.Image("projects/soilgrids-isric/bdod_mean").select("bdod_0-5cm_mean")
        clay = ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean")
        
        # Normalize
        bd_norm = bulk_density.subtract(800).divide(1000).clamp(0, 1)
        clay_norm = clay.divide(600).clamp(0, 1)
        
        # Combined Q_Si
        q_si = bd_norm.multiply(0.6).add(clay_norm.multiply(0.4)).rename("Q_Si")
        
        return q_si.clip(roi)
    
    def _prepare_soil_quality(self, roi: "ee.Geometry") -> "ee.Image":
        """Prepare Q_Bi (soil quality) from SoilGrids."""
        soc = ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean")
        nitrogen = ee.Image("projects/soilgrids-isric/nitrogen_mean").select("nitrogen_0-5cm_mean")
        
        # Normalize
        soc_norm = soc.divide(200).clamp(0, 1)
        n_norm = nitrogen.divide(20).clamp(0, 1)
        
        # Combined Q_Bi
        q_bi = soc_norm.multiply(0.7).add(n_norm.multiply(0.3)).rename("Q_Bi")
        
        return q_bi.clip(roi)
    
    def _prepare_relief(self, roi: "ee.Geometry") -> "ee.Image":
        """Prepare Q_relief from DEM and water data."""
        # SRTM DEM
        dem = ee.Image("USGS/SRTMGL1_003")
        terrain = ee.Terrain.products(dem)
        slope = terrain.select("slope")
        
        # Water bodies
        water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
        is_water = water.gt(50).unmask(0)
        
        # Penalties
        slope_penalty = slope.divide(75.0).clamp(0, 0.4)
        water_penalty = is_water.multiply(0.5)
        
        # Q_relief = 1 - penalties
        q_relief = (
            ee.Image.constant(1.0)
            .subtract(slope_penalty)
            .subtract(water_penalty)
            .clamp(0, 1)
            .rename("Q_relief")
        )
        
        return q_relief.clip(roi)
    
    def _start_export(
        self,
        image: "ee.Image",
        roi: "ee.Geometry",
        filename: str,
        scale: int = 10,
    ) -> "ee.batch.Task":
        """Start GEE export task to Google Drive."""
        task = ee.batch.Export.image.toDrive(
            image=image.toFloat(),
            description=filename,
            folder="GEE_OTU_Exports",
            fileNamePrefix=filename,
            region=roi,
            scale=scale,
            crs=self.config.crs,
            maxPixels=self.config.max_pixels,
            fileFormat="GeoTIFF",
        )
        task.start()
        print(f"    Started export: {filename}")
        return task
    
    def _wait_for_tasks(self, tasks: Dict[str, "ee.batch.Task"], check_interval: int = 30) -> None:
        """Wait for all export tasks to complete."""
        print("\nWaiting for export tasks to complete...")
        print("  (Files will be saved to Google Drive folder 'GEE_OTU_Exports')")
        
        pending = set(tasks.keys())
        
        while pending:
            time.sleep(check_interval)
            
            for name in list(pending):
                task = tasks[name]
                status = task.status()
                state = status.get('state', 'UNKNOWN')
                
                if state == 'COMPLETED':
                    print(f"  [COMPLETED] {name}")
                    pending.remove(name)
                elif state == 'FAILED':
                    error = status.get('error_message', 'Unknown error')
                    print(f"  [FAILED] {name}: {error}")
                    pending.remove(name)
                elif state == 'CANCELLED':
                    print(f"  [CANCELLED] {name}")
                    pending.remove(name)
            
            if pending:
                print(f"  Waiting... ({len(pending)} tasks remaining)")
        
        print("\nAll export tasks completed!")


def export_otu_layers(
    bounds: Tuple[float, float, float, float],
    target_date: str = "2024-09-09",
    output_dir: str = "output/geotiff",
    wait: bool = True,
) -> Dict[str, str]:
    """
    Convenience function to export all OTU layers.
    
    Args:
        bounds: (min_lat, max_lat, min_lon, max_lon)
        target_date: Target NDVI date
        output_dir: Output directory
        wait: Wait for completion
    
    Returns:
        Dictionary of layer names to expected file paths
    """
    config = ExportConfig(output_dir=output_dir)
    exporter = GeoTIFFExporter(config)
    return exporter.export_all_layers(bounds, target_date, wait_for_completion=wait)


if __name__ == "__main__":
    # Test export for a small region
    test_bounds = (47.0, 47.5, 66.0, 66.5)  # ~50x50 km
    
    print("GeoTIFF Exporter Test")
    print("=" * 40)
    
    paths = export_otu_layers(
        bounds=test_bounds,
        target_date="2024-09-09",
        wait=False,  # Don't wait in test
    )
    
    print("\nExpected output files:")
    for name, path in paths.items():
        print(f"  {name}: {path}")
