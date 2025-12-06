"""
GEE Preprocessing Script - Bulk export of static and NDVI data.

This script downloads and caches GEE data locally to avoid repeated API calls.
Run once for static data, monthly for NDVI updates.

Usage:
    # Export static data (DEM, Soil, Water) for a region
    python preprocess_gee.py --region 46.5,65.5,48.5,68.0 --static
    
    # Export NDVI for a specific month
    python preprocess_gee.py --region 46.5,65.5,48.5,68.0 --ndvi --year 2024 --month 9
    
    # Export both
    python preprocess_gee.py --region 46.5,65.5,48.5,68.0 --static --ndvi --year 2024 --month 9
    
    # Show cache statistics
    python preprocess_gee.py --stats
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

import numpy as np

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

# GEE imports
try:
    import ee
    from gee.authenticator import initialize_ee
    HAS_GEE = True
except ImportError:
    ee = None
    HAS_GEE = False
    def initialize_ee():
        print("[WARN] GEE not available")

# Database
from db.otu_database import (
    OTUDatabase,
    GridCellRecord,
    StaticDataRecord,
    NDVIRecord,
    encode_geohash,
)


@dataclass
class RegionBounds:
    """Geographic region bounds."""
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
    
    @classmethod
    def from_string(cls, s: str) -> "RegionBounds":
        """Parse 'min_lat,min_lon,max_lat,max_lon' string."""
        parts = [float(x.strip()) for x in s.split(",")]
        if len(parts) != 4:
            raise ValueError("Region must be 'min_lat,min_lon,max_lat,max_lon'")
        return cls(parts[0], parts[1], parts[2], parts[3])
    
    def to_ee_geometry(self) -> "ee.Geometry":
        """Convert to GEE Geometry."""
        return ee.Geometry.Rectangle([
            self.min_lon, self.min_lat,
            self.max_lon, self.max_lat
        ])


class GEEPreprocessor:
    """
    Bulk preprocessor for GEE data.
    
    Downloads static layers (DEM, Soil, Water) and NDVI composites,
    then stores them in SQLite database keyed by geohash.
    """
    
    def __init__(self, db_path: str = "output/otu_cache.db", cell_size_km: float = 1.0):
        self.db = OTUDatabase(db_path)
        self.cell_size_km = cell_size_km
        self._ee_initialized = False
    
    def _init_ee(self):
        """Initialize Earth Engine."""
        if not self._ee_initialized:
            initialize_ee()
            self._ee_initialized = True
    
    def generate_grid(self, bounds: RegionBounds) -> List[GridCellRecord]:
        """Generate grid cells for region."""
        import math
        
        center_lat = (bounds.min_lat + bounds.max_lat) / 2
        lat_rad = math.radians(center_lat)
        
        deg_per_km_lat = 1 / 111.0
        deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
        
        cell_size_lat = self.cell_size_km * deg_per_km_lat
        cell_size_lon = self.cell_size_km * deg_per_km_lon
        
        cells = []
        lat = bounds.min_lat
        while lat < bounds.max_lat:
            lon = bounds.min_lon
            while lon < bounds.max_lon:
                center_lat = lat + cell_size_lat / 2
                center_lon = lon + cell_size_lon / 2
                grid_id = encode_geohash(center_lat, center_lon, precision=7)
                
                cells.append(GridCellRecord(
                    grid_id=grid_id,
                    center_lat=center_lat,
                    center_lon=center_lon,
                    min_lat=lat,
                    max_lat=lat + cell_size_lat,
                    min_lon=lon,
                    max_lon=lon + cell_size_lon,
                ))
                lon += cell_size_lon
            lat += cell_size_lat
        
        return cells
    
    def preprocess_static(self, bounds: RegionBounds, force: bool = False) -> int:
        """
        Download and cache static data (DEM, Soil, Water) for region.
        
        Args:
            bounds: Region bounds
            force: If True, re-download even if cached
            
        Returns:
            Number of cells processed
        """
        self._init_ee()
        
        print("\n" + "="*60)
        print("STATIC DATA PREPROCESSING")
        print("="*60)
        print(f"  Region: ({bounds.min_lat}, {bounds.min_lon}) to ({bounds.max_lat}, {bounds.max_lon})")
        
        # Generate grid
        print("\n[1/4] Generating grid...")
        cells = self.generate_grid(bounds)
        print(f"  Generated {len(cells)} cells")
        
        # Save grid cells to DB
        new_count = self.db.save_grid_cells(cells)
        print(f"  Saved {new_count} new cells to database")
        
        # Check what's missing
        grid_ids = [c.grid_id for c in cells]
        if not force:
            missing_ids = self.db.get_missing_static_data(grid_ids)
            if not missing_ids:
                print("\n[SKIP] All static data already cached!")
                return 0
            print(f"  Need to fetch {len(missing_ids)} cells")
            cells = [c for c in cells if c.grid_id in set(missing_ids)]
        
        # Create GEE FeatureCollection
        print("\n[2/4] Creating GEE FeatureCollection...")
        features = []
        for c in cells:
            geom = ee.Geometry.Rectangle([c.min_lon, c.min_lat, c.max_lon, c.max_lat])
            features.append(ee.Feature(geom, {"grid_id": c.grid_id}))
        
        grid_fc = ee.FeatureCollection(features)
        
        # Fetch static data
        print("\n[3/4] Fetching static data from GEE...")
        
        # DEM
        print("  - DEM (slope, aspect)...")
        dem = ee.Image("USGS/SRTMGL1_003")
        terrain = ee.Terrain.products(dem)
        slope = terrain.select("slope")
        aspect = terrain.select("aspect")
        
        # Soil
        print("  - Soil (BD, Clay, SOC, N)...")
        soil_bd = ee.Image("projects/soilgrids-isric/bdod_mean").select("bdod_0-5cm_mean")
        soil_clay = ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean")
        soil_soc = ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean")
        soil_n = ee.Image("projects/soilgrids-isric/nitrogen_mean").select("nitrogen_0-5cm_mean")
        
        # Water
        print("  - Water occurrence...")
        water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
        
        # Combine all bands
        combined = slope.addBands([aspect, soil_bd, soil_clay, soil_soc, soil_n, water])
        combined = combined.rename(["slope", "aspect", "bd", "clay", "soc", "nitrogen", "water"])
        
        # Reduce regions
        print("  - Reducing regions (this may take a while)...")
        
        def extract_values(feature):
            geom = feature.geometry()
            values = combined.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geom,
                scale=30,
                maxPixels=1e6
            )
            return feature.set(values)
        
        results_fc = grid_fc.map(extract_values)
        
        # Fetch results
        print("  - Downloading results...")
        try:
            results_list = results_fc.getInfo()["features"]
        except Exception as e:
            print(f"  [ERROR] GEE fetch failed: {e}")
            return 0
        
        # Convert to records
        print("\n[4/4] Saving to database...")
        records = []
        for item in tqdm(results_list, desc="Processing"):
            props = item["properties"]
            records.append(StaticDataRecord(
                grid_id=props["grid_id"],
                slope=props.get("slope", 0) or 0,
                aspect=props.get("aspect", 0) or 0,
                bulk_density=props.get("bd", 0) or 0,
                clay=props.get("clay", 0) or 0,
                soc=props.get("soc", 0) or 0,
                nitrogen=props.get("nitrogen", 0) or 0,
                water_occurrence=props.get("water", 0) or 0,
            ))
        
        saved = self.db.save_static_data(records)
        print(f"  Saved {saved} static data records")
        
        return saved
    
    def preprocess_ndvi(self, bounds: RegionBounds, year: int, month: int, force: bool = False) -> int:
        """
        Download and cache NDVI composite for a month.
        
        Args:
            bounds: Region bounds
            year: Year
            month: Month (1-12)
            force: If True, re-download even if cached
            
        Returns:
            Number of cells processed
        """
        self._init_ee()
        
        target_date = f"{year}-{month:02d}-15"  # Mid-month representative date
        
        print("\n" + "="*60)
        print("NDVI PREPROCESSING")
        print("="*60)
        print(f"  Region: ({bounds.min_lat}, {bounds.min_lon}) to ({bounds.max_lat}, {bounds.max_lon})")
        print(f"  Period: {year}-{month:02d}")
        
        # Generate grid
        print("\n[1/4] Generating grid...")
        cells = self.generate_grid(bounds)
        grid_ids = [c.grid_id for c in cells]
        print(f"  Generated {len(cells)} cells")
        
        # Ensure grid is in DB
        self.db.save_grid_cells(cells)
        
        # Check what's missing
        if not force:
            missing_ids = self.db.get_missing_ndvi(grid_ids, target_date)
            if not missing_ids:
                print(f"\n[SKIP] All NDVI data already cached for {target_date}!")
                return 0
            print(f"  Need to fetch {len(missing_ids)} cells")
            cells = [c for c in cells if c.grid_id in set(missing_ids)]
        
        # Create GEE FeatureCollection
        print("\n[2/4] Creating GEE FeatureCollection...")
        features = []
        for c in cells:
            geom = ee.Geometry.Rectangle([c.min_lon, c.min_lat, c.max_lon, c.max_lat])
            features.append(ee.Feature(geom, {"grid_id": c.grid_id}))
        
        grid_fc = ee.FeatureCollection(features)
        roi = bounds.to_ee_geometry()
        
        # Fetch NDVI
        print("\n[3/4] Fetching NDVI from Sentinel-2...")
        
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"
        
        def mask_clouds(img):
            qa = img.select("QA60")
            cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
            return img.updateMask(cloud_mask)
        
        s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
            .filterBounds(roi) \
            .filterDate(start_date, end_date) \
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30)) \
            .map(mask_clouds)
        
        # Compute median NDVI
        ndvi = s2.map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("ndvi")).median()
        
        # Reduce regions
        print("  - Reducing regions...")
        
        def extract_ndvi(feature):
            geom = feature.geometry()
            values = ndvi.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=geom,
                scale=10,
                maxPixels=1e6
            )
            return feature.set("ndvi", values.get("ndvi"))
        
        results_fc = grid_fc.map(extract_ndvi)
        
        # Download
        print("  - Downloading results...")
        try:
            results_list = results_fc.getInfo()["features"]
        except Exception as e:
            print(f"  [ERROR] GEE fetch failed: {e}")
            return 0
        
        # Save to DB
        print("\n[4/4] Saving to database...")
        records = []
        for item in tqdm(results_list, desc="Processing"):
            props = item["properties"]
            ndvi_val = props.get("ndvi")
            if ndvi_val is not None:
                records.append(NDVIRecord(
                    grid_id=props["grid_id"],
                    observation_date=target_date,
                    ndvi=float(ndvi_val),
                ))
        
        saved = self.db.save_ndvi(records)
        print(f"  Saved {saved} NDVI records for {target_date}")
        
        return saved
    
    def show_stats(self):
        """Show database statistics."""
        stats = self.db.get_stats()
        dates = self.db.get_available_dates()
        
        print("\n" + "="*60)
        print("CACHE STATISTICS")
        print("="*60)
        print(f"  Grid cells:     {stats['grid_cells']}")
        print(f"  Static data:    {stats['static_data']}")
        print(f"  NDVI records:   {stats['ndvi_records']}")
        print(f"  OTU records:    {stats['otu_records']}")
        print(f"  Unique dates:   {stats['unique_dates']}")
        
        if dates:
            print(f"\n  Available NDVI dates:")
            for d in dates[:10]:
                print(f"    - {d}")
            if len(dates) > 10:
                print(f"    ... and {len(dates) - 10} more")


def main():
    parser = argparse.ArgumentParser(
        description="GEE Preprocessing - Bulk data export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Export static data for Baikonur region
  python preprocess_gee.py --region 46.5,65.5,48.5,68.0 --static
  
  # Export NDVI for September 2024
  python preprocess_gee.py --region 46.5,65.5,48.5,68.0 --ndvi --year 2024 --month 9
  
  # Show cache statistics
  python preprocess_gee.py --stats
        """
    )
    
    parser.add_argument("--region", type=str, help="Region bounds: min_lat,min_lon,max_lat,max_lon")
    parser.add_argument("--static", action="store_true", help="Preprocess static data (DEM, Soil, Water)")
    parser.add_argument("--ndvi", action="store_true", help="Preprocess NDVI")
    parser.add_argument("--year", type=int, default=2024, help="Year for NDVI")
    parser.add_argument("--month", type=int, default=9, help="Month for NDVI")
    parser.add_argument("--force", action="store_true", help="Force re-download even if cached")
    parser.add_argument("--stats", action="store_true", help="Show cache statistics")
    parser.add_argument("--db", type=str, default="output/otu_cache.db", help="Database path")
    
    args = parser.parse_args()
    
    preprocessor = GEEPreprocessor(db_path=args.db)
    
    if args.stats:
        preprocessor.show_stats()
        return
    
    if not args.region and (args.static or args.ndvi):
        print("ERROR: --region is required for preprocessing")
        parser.print_help()
        return
    
    if args.region:
        bounds = RegionBounds.from_string(args.region)
        
        if args.static:
            preprocessor.preprocess_static(bounds, force=args.force)
        
        if args.ndvi:
            preprocessor.preprocess_ndvi(bounds, args.year, args.month, force=args.force)
    
    # Always show stats at end
    preprocessor.show_stats()


if __name__ == "__main__":
    main()
