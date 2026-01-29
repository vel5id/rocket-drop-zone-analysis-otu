"""OTU Calculator - Main calculation module.

Calculates Q_OTUi ecological resilience index for each grid cell/chunk
using data from Google Earth Engine with local processing.
"""
from __future__ import annotations

import os
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        desc = kwargs.get('desc', '')
        if desc:
            print(f"  {desc}...")
        return iterable

try:
    import ee
except ImportError:
    ee = None

from otu.chunk_manager import ChunkManager, Chunk
from config.otu_config import OTUConfig
from otu.otu_logic import (
    compute_q_si, 
    compute_q_bi, 
    compute_q_relief, 
    compute_otu_index
)


@dataclass
class OTUCalculator:
    """
    Calculator for Q_OTUi ecological resilience index.
    
    Formula: Q_OTUi = (k_vi * Q_Vi + k_si * Q_Si + k_bi * Q_Bi) * Q_relief
    
    Where:
    - Q_Vi: Vegetation index from NDVI
    - Q_Si: Soil mechanical strength
    - Q_Bi: Soil quality/bonitet
    - Q_relief: Relief factor (penalizes slopes, water bodies)
    """
    chunk_manager: ChunkManager
    output_dir: Path = field(default_factory=lambda: Path("output/otu"))
    
    def __post_init__(self):
        """Initialize calculator."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._ee_initialized = False
    
    def _init_ee(self) -> None:
        """Initialize Earth Engine if not already done."""
        if self._ee_initialized:
            return
            
        if ee is None:
            if OTUConfig.gee.strict_mode:
                raise ImportError("Earth Engine API not installed and strict mode is ON.")
            return
        
        try:
            ee.Initialize(project=OTUConfig.gee.project_id)
            self._ee_initialized = True
        except Exception:
            try:
                ee.Authenticate()
                ee.Initialize(project=OTUConfig.gee.project_id)
                self._ee_initialized = True
            except Exception as e:
                if OTUConfig.gee.strict_mode:
                    raise RuntimeError(f"Could not initialize Earth Engine: {e}")
                print(f"Warning: Could not initialize Earth Engine: {e}")
    
    def calculate_single_day(
        self,
        target_date: str = "2024-09-09",
        max_workers: int = 4,
        use_cache: bool = True,
        show_progress: bool = True,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Calculate OTU for a single day.
        
        Args:
            target_date: Target date in YYYY-MM-DD format
            max_workers: Number of parallel workers for processing
            use_cache: Whether to use cached data
            show_progress: Show progress bar
            progress_callback: Function(msg: str) to update UI status
        """
        self._init_ee()
        
        def report(msg):
            if progress_callback:
                progress_callback(msg)
            if show_progress:
                print(f"  [OTU] {msg}")

        print(f"\n{'='*60}")
        print(f"OTU CALCULATION - {target_date}")
        print(f"{'='*60}")
        print(f"  Chunks: {len(self.chunk_manager.chunks)}")
        w = OTUConfig.weights
        print(f"  Weights: Q_Vi={w.k_vi}, Q_Si={w.k_si}, Q_Bi={w.k_bi}")
        print(f"  Strict Mode: {OTUConfig.gee.strict_mode}")
        
        # Step 1: Fetch NDVI data
        report("Fetch NDVI (Sentinel-2)...")
        ndvi_data = self._fetch_ndvi_for_chunks(target_date, use_cache, show_progress, progress_callback)
        
        # Step 2: Fetch soil data
        report("Fetch Soil Data (SoilGrids)...")
        soil_data = self._fetch_soil_for_chunks(use_cache, show_progress, progress_callback)
        
        # Step 3: Fetch relief data
        report("Fetch Relief (SRTM/Water)...")
        relief_data = self._fetch_relief_for_chunks(use_cache, show_progress, progress_callback)
        
        # Step 4: Calculate OTU for each chunk
        report(f"Computing Index for {len(self.chunk_manager.chunks)} chunks...")
        self._calculate_otu_for_chunks(ndvi_data, soil_data, relief_data, show_progress)
        
        # Generate summary
        stats = self.chunk_manager.get_otu_statistics()
        
        # Enhanced Dynamic Analysis (MAD, Min/Max)
        chunks_with_otu = [c for c in self.chunk_manager.chunks if c.is_processed]
        otu_values = [c.q_otu for c in chunks_with_otu]
        
        if otu_values:
            median_otu = np.median(otu_values)
            mad = np.median(np.abs(np.array(otu_values) - median_otu))
            
            # Find outliers (Max/Min)
            max_chunk = max(chunks_with_otu, key=lambda c: c.q_otu)
            min_chunk = min(chunks_with_otu, key=lambda c: c.q_otu)
            
            stats.update({
                "median": float(median_otu),
                "mad": float(mad),
                "highest_otu_chunk": {
                    "id": max_chunk.id, 
                    "val": max_chunk.q_otu, 
                    "lat": max_chunk.center_lat, 
                    "lon": max_chunk.center_lon
                },
                "lowest_otu_chunk": {
                    "id": min_chunk.id, 
                    "val": min_chunk.q_otu, 
                    "lat": min_chunk.center_lat, 
                    "lon": min_chunk.center_lon
                }
            })
        
        summary = self.chunk_manager.summary()
        
        print(f"\n{'='*60}")
        print("OTU CALCULATION COMPLETE")
        print(f"{'='*60}")
        print(f"  Processed: {summary['processed']}/{summary['total_chunks']} chunks")
        if summary['failed'] > 0:
            print(f"  Failed: {summary['failed']} chunks")
        print(f"  Q_OTU Mean: {stats.get('mean', 0):.3f}")
        print(f"  Q_OTU MAD:  {stats.get('mad', 0):.3f} (Median Absolute Deviation)")
        print(f"  Q_OTU Range: [{stats.get('min', 0):.3f}, {stats.get('max', 0):.3f}]")
        
        # Save results
        output_path = self.output_dir / f"otu_{target_date}.geojson"
        self.chunk_manager.save_geojson(str(output_path))
        print(f"  Saved: {output_path}")
        
        return {
            "date": target_date,
            "statistics": stats,
            "summary": summary,
            "output_path": str(output_path),
            "chunks": self.chunk_manager.chunks, # Return chunks to map back to grid_cells
        }
    
    def _fetch_ndvi_for_chunks(
        self,
        target_date: str,
        use_cache: bool,
        show_progress: bool,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, float]:
        """Fetch NDVI values for all chunks."""
        if not self._ee_initialized:
            print("  Warning: Earth Engine not available, using mock data")
            return self._generate_mock_ndvi_data()
        
        # Parse target date
        target_dt = datetime.strptime(target_date, "%Y-%m-%d")
        window = OTUConfig.gee.ndvi_window_days
        start_dt = target_dt - timedelta(days=window)
        end_dt = target_dt + timedelta(days=window)
        
        start_str = start_dt.strftime("%Y-%m-%d")
        end_str = end_dt.strftime("%Y-%m-%d")
        
        # Get merged ROI for efficient batch query
        roi = self.chunk_manager.get_merged_ee_geometry()
        
        try:
            s2 = (
                ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
                .filterBounds(roi)
                .filterDate(start_str, end_str)
                .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", OTUConfig.gee.cloud_threshold))
            )
            
            # Count images
            try:
                img_count = s2.size().getInfo()
                msg = f"Aggregating {img_count} Sentinel Scenes ({OTUConfig.gee.cloud_threshold}% cloud risk)..."
                if progress_callback: progress_callback(msg)
                print(f"  [GEE] {msg}")
            except:
                pass
            
            # Apply cloud mask
            def mask_clouds(image):
                qa = image.select("QA60")
                cloud_mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
                return image.updateMask(cloud_mask)
            
            s2_masked = s2.map(mask_clouds)
            composite = s2_masked.median()
            ndvi = composite.normalizedDifference(["B8", "B4"]).rename("NDVI")
            
            ndvi_data = {}
            chunks_iter = self.chunk_manager.chunks
            if show_progress:
                chunks_iter = tqdm(chunks_iter, desc="Sampling NDVI", leave=False)
            
                try:
                    # BATCH OPTIMIZATION: Create features for all non-cached chunks
                    chunks_to_process = []
                    for c in chunks_iter:
                        if use_cache:
                            cached = self.chunk_manager.load_from_cache(c, "ndvi", target_date)
                            if cached is not None:
                                ndvi_data[c.id] = cached.get("value", 0.5)
                                continue
                        chunks_to_process.append(c)
                    
                    if not chunks_to_process:
                        return ndvi_data
                    
                    total_chunks = len(chunks_to_process)
                    print(f"  Batch processing {total_chunks} chunks via GEE...")
                    
                    # PROCESS IN SMALLER BATCHES TO AVOID TIMEOUTS
                    # User requested ~50 pieces for 2500 points -> ~50pts/batch
                    BATCH_SIZE = 50 
                    
                    for i in range(0, total_chunks, BATCH_SIZE):
                        batch = chunks_to_process[i : i + BATCH_SIZE]
                        current_batch_num = (i // BATCH_SIZE) + 1
                        total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE
                        
                        msg = f"Requesting GEE Batch {current_batch_num}/{total_batches} ({len(batch)} chunks)..."
                        print(f"  [GEE] {msg}")
                        if progress_callback: progress_callback(msg)
                        
                        # Create FeatureCollection for this batch
                        features = []
                        for c in batch:
                            geom = ee.Geometry.Point([c.center_lon, c.center_lat]).buffer(500)
                            feat = ee.Feature(geom, {'chunk_id': c.id})
                            features.append(feat)
                        
                        fc = ee.FeatureCollection(features)
                        
                        # Reduce Regions (Batch Request)
                        reduced = ndvi.reduceRegions(
                            collection=fc,
                            reducer=ee.Reducer.mean(),
                            scale=10,
                        )
                        
                        # Get Info (Network Call - can take time)
                        results = reduced.getInfo()
                        
                        feat_count = len(results.get('features', []))
                        print(f"  [GEE DEBUG] Batch {current_batch_num} returned {feat_count} features")
                        
                        null_count = 0
                        # Parse Results
                        for feat in results['features']:
                            c_id = feat['properties']['chunk_id']
                            val = feat['properties'].get('NDVI')
                            
                            if val is None:
                                null_count += 1
                                val = 0.5  # Default
                            
                            val = max(0, min(1, val))
                            ndvi_data[c_id] = val
                            
                            # Cache result
                            chunk = next((c for c in batch if c.id == c_id), None)
                            if chunk and use_cache:
                                self.chunk_manager.save_to_cache(chunk, "ndvi", target_date, {"value": val})
                        
                        if null_count > 0:
                            print(f"  [GEE DEBUG] Warning: {null_count}/{feat_count} chunks in batch {current_batch_num} had NULL NDVI")
                            
                except Exception as e:
                    print(f"  Batch NDVI failed: {e}")
                    # Fallback to per-chunk (or mock)
                    for c in chunks_to_process:
                        if c.id not in ndvi_data:
                            ndvi_data[c.id] = 0.5
            
            return ndvi_data
            
        except Exception as e:
            if OTUConfig.gee.strict_mode:
                raise e
            print(f"  Error fetching NDVI: {e}")
            return self._generate_mock_ndvi_data()
    
    def _fetch_soil_for_chunks(
        self,
        use_cache: bool,
        show_progress: bool,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Fetch raw soil data (BD, Clay, SOC, Nitrogen) for all chunks.
        """
        if not self._ee_initialized:
            return self._generate_mock_soil_data()
        
        try:
            # Load SoilGrids data
            bulk_density = ee.Image("projects/soilgrids-isric/bdod_mean").select("bdod_0-5cm_mean")
            clay = ee.Image("projects/soilgrids-isric/clay_mean").select("clay_0-5cm_mean")
            soc = ee.Image("projects/soilgrids-isric/soc_mean").select("soc_0-5cm_mean")
            nitrogen = ee.Image("projects/soilgrids-isric/nitrogen_mean").select("nitrogen_0-5cm_mean")
            
            combined = bulk_density.addBands(clay).addBands(soc).addBands(nitrogen)
            
            chunks_iter = self.chunk_manager.chunks
            
            # BATCH OPTIMIZATION: Process in chunks of 50
            chunks_to_process = []
            for c in chunks_iter:
                if use_cache:
                    cached = self.chunk_manager.load_from_cache(c, "soil_raw", "static")
                    if cached is not None:
                        soil_data[c.id] = cached
                        continue
                chunks_to_process.append(c)
            
            if not chunks_to_process:
                return soil_data
                
            total_chunks = len(chunks_to_process)
            BATCH_SIZE = 50
            
            for i in range(0, total_chunks, BATCH_SIZE):
                batch = chunks_to_process[i : i + BATCH_SIZE]
                current_batch_num = (i // BATCH_SIZE) + 1
                total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE
                
                msg = f"Soil Sampling Batch {current_batch_num}/{total_batches} ({len(batch)} chunks)..."
                if progress_callback: progress_callback(msg)
                if show_progress: print(f"  [GEE] {msg}")
                
                try:
                    features = []
                    for c in batch:
                        geom = ee.Geometry.Point([c.center_lon, c.center_lat]).buffer(500)
                        feat = ee.Feature(geom, {'chunk_id': c.id})
                        features.append(feat)
                    
                    fc = ee.FeatureCollection(features)
                    
                    reduced = combined.reduceRegions(
                        collection=fc,
                        reducer=ee.Reducer.mean(),
                        scale=250,
                    )
                    
                    results = reduced.getInfo()
                    
                    for feat in results['features']:
                        c_id = feat['properties']['chunk_id']
                        props = feat['properties']
                        
                        data = {
                            "bd": props.get("bdod_0-5cm_mean", 1300),
                            "clay": props.get("clay_0-5cm_mean", 200),
                            "soc": props.get("soc_0-5cm_mean", 50),
                            "n": props.get("nitrogen_0-5cm_mean", 2),
                        }
                        
                        # Handle None
                        for k, v in data.items():
                            if v is None:
                                if k == "bd": data[k] = 1300
                                elif k == "clay": data[k] = 200
                                elif k == "soc": data[k] = 50
                                elif k == "n": data[k] = 2
                                else: data[k] = 0
                        
                        soil_data[c_id] = data
                        
                        chunk = next((c for c in batch if c.id == c_id), None)
                        if chunk and use_cache:
                            self.chunk_manager.save_to_cache(chunk, "soil_raw", "static", data)
                            
                except Exception as e:
                    print(f"  Warning: Soil/GEE Batch {current_batch_num} failed: {e}")
                    for c in batch:
                        soil_data[c.id] = {"bd": 1300, "clay": 200, "soc": 50, "n": 2}
            
            return soil_data
            
        except Exception as e:
            if OTUConfig.gee.strict_mode:
                raise e
            print(f"  Error fetching soil data: {e}")
            return self._generate_mock_soil_data()
    
    def _fetch_relief_for_chunks(
        self,
        use_cache: bool,
        show_progress: bool,
        progress_callback: Optional[Any] = None,
    ) -> Dict[str, Dict[str, float]]:
        """
        Fetch raw relief data (Slope, Water) for all chunks.
        """
        if not self._ee_initialized:
            return self._generate_mock_relief_data()
        
        try:
            # DEM and slope
            dem = ee.Image("USGS/SRTMGL1_003")
            slope = ee.Terrain.products(dem).select("slope")
            
            # Water bodies
            water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
            
            combined = slope.addBands(water)
            
            chunks_iter = self.chunk_manager.chunks
            
            # BATCH OPTIMIZATION: Process in chunks of 50
            chunks_to_process = []
            for c in chunks_iter:
                if use_cache:
                    cached = self.chunk_manager.load_from_cache(c, "relief_raw", "static")
                    if cached is not None:
                        relief_data[c.id] = cached
                        continue
                chunks_to_process.append(c)
                
            if not chunks_to_process:
                return relief_data
            
            total_chunks = len(chunks_to_process)
            BATCH_SIZE = 50
            
            for i in range(0, total_chunks, BATCH_SIZE):
                batch = chunks_to_process[i : i + BATCH_SIZE]
                current_batch_num = (i // BATCH_SIZE) + 1
                total_batches = (total_chunks + BATCH_SIZE - 1) // BATCH_SIZE
                
                msg = f"Relief Sampling Batch {current_batch_num}/{total_batches} ({len(batch)} chunks)..."
                if progress_callback: progress_callback(msg)
                if show_progress: print(f"  [GEE] {msg}")
                
                try:
                    features = []
                    for c in batch:
                        geom = ee.Geometry.Point([c.center_lon, c.center_lat]).buffer(500)
                        feat = ee.Feature(geom, {'chunk_id': c.id})
                        features.append(feat)
                    
                    fc = ee.FeatureCollection(features)
                    
                    reduced = combined.reduceRegions(
                        collection=fc,
                        reducer=ee.Reducer.mean(),
                        scale=30,
                    )
                    
                    results = reduced.getInfo()
                    
                    for feat in results['features']:
                        c_id = feat['properties']['chunk_id']
                        props = feat['properties']
                        
                        data = {
                            "slope": props.get("slope", 0),
                            "water": props.get("occurrence", 0),
                        }
                        
                        # Handle None
                        if data["slope"] is None: data["slope"] = 0
                        if data["water"] is None: data["water"] = 0
                        
                        relief_data[c_id] = data
                        
                        chunk = next((c for c in batch if c.id == c_id), None)
                        if chunk and use_cache:
                            self.chunk_manager.save_to_cache(chunk, "relief_raw", "static", data)
                            
                except Exception as e:
                    print(f"  Warning: Relief/GEE Batch {current_batch_num} failed: {e}")
                    for c in batch:
                        relief_data[c.id] = {"slope": 0, "water": 0}
            
            return relief_data
            
        except Exception as e:
            if OTUConfig.gee.strict_mode:
                raise e
            print(f"  Error fetching relief data: {e}")
            return self._generate_mock_relief_data()
    
    def _calculate_otu_for_chunks(
        self,
        ndvi_data: Dict[str, float],
        soil_data: Dict[str, Dict[str, float]],
        relief_data: Dict[str, Dict[str, float]],
        show_progress: bool,
    ) -> None:
        """Calculate OTU for each chunk using fetched data and shared logic."""
        
        chunks_iter = self.chunk_manager.chunks
        if show_progress:
            chunks_iter = tqdm(chunks_iter, desc="Computing OTU", leave=False)
        
        for chunk in chunks_iter:
            try:
                # 1. Vegetation
                q_vi = ndvi_data.get(chunk.id, 0.5)
                
                # 2. Soil
                s = soil_data.get(chunk.id, {"bd": 1300, "clay": 200, "soc": 50, "n": 2})
                q_si = compute_q_si(s["bd"], s["clay"])
                q_bi = compute_q_bi(s["soc"], s["n"])
                
                # 3. Relief
                r = relief_data.get(chunk.id, {"slope": 0, "water": 0})
                # Water occurrence is 0-100 in GEE, normalize to 0-1 for logic if needed?
                # Logic expects "is_water" as 0 or 1 usually, or probability.
                # GEE 'occurrence' is percentage 0-100.
                # Let's convert to 0-1 probability.
                water_prob = r["water"] / 100.0
                q_relief = compute_q_relief(r["slope"], water_prob)
                
                # 4. Final OTU
                q_otu = compute_otu_index(q_vi, q_si, q_bi, q_relief)
                
                # Store in chunk
                chunk.q_vi = float(q_vi)
                chunk.q_si = float(q_si)
                chunk.q_bi = float(q_bi)
                chunk.q_relief = float(q_relief)
                chunk.q_otu = float(q_otu)
                chunk.is_processed = True
                
            except Exception as e:
                chunk.error = str(e)
    
    # Mock data generators
    def _generate_mock_ndvi_data(self) -> Dict[str, float]:
        rng = np.random.default_rng(42)
        return {c.id: float(rng.uniform(0.2, 0.7)) for c in self.chunk_manager.chunks}
    
    def _generate_mock_soil_data(self) -> Dict[str, Dict[str, float]]:
        rng = np.random.default_rng(43)
        return {
            c.id: {
                "bd": float(rng.uniform(1000, 1600)),
                "clay": float(rng.uniform(100, 400)),
                "soc": float(rng.uniform(20, 100)),
                "n": float(rng.uniform(1, 10))
            } for c in self.chunk_manager.chunks
        }
    
    def _generate_mock_relief_data(self) -> Dict[str, Dict[str, float]]:
        rng = np.random.default_rng(44)
        return {
            c.id: {
                "slope": float(rng.exponential(5)), # Mostly flat
                "water": float(rng.choice([0, 100], p=[0.9, 0.1]))
            } for c in self.chunk_manager.chunks
        }


def calculate_otu_for_grid(
    grid_cells: List,
    target_date: str = "2024-09-09",
    weights: Optional[Dict[str, float]] = None, # Deprecated, kept for compat
    output_dir: str = "output/otu",
    cache_dir: str = "output/otu_cache",
    show_progress: bool = True,
    progress_callback: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Convenience function to calculate OTU for grid cells.
    """
    # Create chunk manager from grid cells
    chunk_manager = ChunkManager.from_grid_cells(grid_cells, cache_dir=cache_dir)
    
    # Create calculator (weights now from config)
    calculator = OTUCalculator(
        chunk_manager=chunk_manager,
        output_dir=Path(output_dir),
    )
    
    # Run calculation
    return calculator.calculate_single_day(
        target_date=target_date,
        show_progress=show_progress,
        progress_callback=progress_callback,
    )


if __name__ == "__main__":
    # Demo with mock data
    print("OTU Calculator Demo (Mock Data)")
    
    # Create test chunks
    manager = ChunkManager.from_bounds(
        min_lat=47.0, max_lat=47.5,
        min_lon=66.0, max_lon=66.5,
        chunk_size_km=1.0,
    )
    
    print(f"Created {len(manager.chunks)} test chunks")
    
    calculator = OTUCalculator(chunk_manager=manager)
    results = calculator.calculate_single_day(target_date="2024-09-09")
    
    print(f"\nResults: {results}")
