"""Chunk manager for efficient OTU processing.

Splits large regions into 1x1 km chunks (matching grid cells),
downloads data locally, and processes in parallel.
"""
from __future__ import annotations

import os
import math
import json
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

try:
    import ee
except ImportError:
    ee = None


@dataclass
class Chunk:
    """Represents a 1x1 km processing chunk."""
    id: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    center_lat: float
    center_lon: float
    
    # Calculated indices (filled after processing)
    q_vi: Optional[float] = None
    q_si: Optional[float] = None
    q_bi: Optional[float] = None
    q_relief: Optional[float] = None
    q_otu: Optional[float] = None
    
    # Metadata
    is_processed: bool = False
    error: Optional[str] = None
    missing_data: List[str] = field(default_factory=list)
    
    def to_ee_geometry(self) -> "ee.Geometry":
        """Convert chunk to Earth Engine geometry."""
        if ee is None:
            raise ImportError("Earth Engine API not available")
        return ee.Geometry.Rectangle([
            self.min_lon, self.min_lat,
            self.max_lon, self.max_lat
        ])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "bounds": {
                "min_lat": self.min_lat,
                "max_lat": self.max_lat,
                "min_lon": self.min_lon,
                "max_lon": self.max_lon,
            },
            "center": {"lat": self.center_lat, "lon": self.center_lon},
            "indices": {
                "q_vi": self.q_vi,
                "q_si": self.q_si,
                "q_bi": self.q_bi,
                "q_relief": self.q_relief,
                "q_otu": self.q_otu,
            },
            "is_processed": self.is_processed,
            "error": self.error,
            "missing_data": self.missing_data,
        }


@dataclass
class ChunkManager:
    """
    Manages chunked processing of OTU calculations.
    
    Strategy:
    1. Split region into 1x1 km chunks (matching grid cells)
    2. Download GEE data for each chunk locally (caching)
    3. Process chunks in parallel on local machine
    4. Aggregate results into final OTU map
    """
    chunks: List[Chunk] = field(default_factory=list)
    cache_dir: Path = field(default_factory=lambda: Path("output/otu_cache"))
    chunk_size_km: float = 1.0
    
    def __post_init__(self):
        """Initialize cache directory."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_grid_cells(cls, grid_cells: List, cache_dir: str = "output/otu_cache") -> "ChunkManager":
        """
        Create ChunkManager from existing grid cells.
        
        Args:
            grid_cells: List of GridCell objects from polygon_grid
            cache_dir: Directory for caching downloaded data
        
        Returns:
            ChunkManager instance with chunks matching grid cells
        """
        chunks = []
        for i, cell in enumerate(grid_cells):
            chunk_id = f"chunk_{i:05d}_{cell.center_lat:.4f}_{cell.center_lon:.4f}"
            chunk_id = hashlib.md5(chunk_id.encode()).hexdigest()[:12]
            
            chunks.append(Chunk(
                id=chunk_id,
                min_lat=cell.min_lat,
                max_lat=cell.max_lat,
                min_lon=cell.min_lon,
                max_lon=cell.max_lon,
                center_lat=cell.center_lat,
                center_lon=cell.center_lon,
            ))
        
        return cls(chunks=chunks, cache_dir=Path(cache_dir))
    
    @classmethod
    def from_bounds(
        cls,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        chunk_size_km: float = 1.0,
        cache_dir: str = "output/otu_cache",
    ) -> "ChunkManager":
        """
        Create ChunkManager by splitting bounds into chunks.
        
        Args:
            min_lat, max_lat, min_lon, max_lon: Bounding box
            chunk_size_km: Size of each chunk in km
            cache_dir: Directory for caching
        
        Returns:
            ChunkManager with generated chunks
        """
        # Convert km to degrees
        center_lat = (min_lat + max_lat) / 2
        lat_rad = math.radians(center_lat)
        deg_per_km_lat = 1 / 111.0
        deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
        
        chunk_size_lat = chunk_size_km * deg_per_km_lat
        chunk_size_lon = chunk_size_km * deg_per_km_lon
        
        chunks = []
        chunk_idx = 0
        
        lat = min_lat
        while lat < max_lat:
            lon = min_lon
            while lon < max_lon:
                cell_min_lat = lat
                cell_max_lat = min(lat + chunk_size_lat, max_lat)
                cell_min_lon = lon
                cell_max_lon = min(lon + chunk_size_lon, max_lon)
                
                center_lat = (cell_min_lat + cell_max_lat) / 2
                center_lon = (cell_min_lon + cell_max_lon) / 2
                
                chunk_id = f"chunk_{chunk_idx:05d}"
                
                chunks.append(Chunk(
                    id=chunk_id,
                    min_lat=cell_min_lat,
                    max_lat=cell_max_lat,
                    min_lon=cell_min_lon,
                    max_lon=cell_max_lon,
                    center_lat=center_lat,
                    center_lon=center_lon,
                ))
                
                chunk_idx += 1
                lon += chunk_size_lon
            lat += chunk_size_lat
        
        return cls(chunks=chunks, cache_dir=Path(cache_dir), chunk_size_km=chunk_size_km)
    
    def get_merged_bounds(self) -> Tuple[float, float, float, float]:
        """Get bounding box of all chunks."""
        if not self.chunks:
            return (0, 0, 0, 0)
        
        return (
            min(c.min_lat for c in self.chunks),
            max(c.max_lat for c in self.chunks),
            min(c.min_lon for c in self.chunks),
            max(c.max_lon for c in self.chunks),
        )
    
    def get_merged_ee_geometry(self) -> "ee.Geometry":
        """Get Earth Engine geometry covering all chunks."""
        if ee is None:
            raise ImportError("Earth Engine API not available")
        
        min_lat, max_lat, min_lon, max_lon = self.get_merged_bounds()
        return ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])
    
    def get_cache_path(self, chunk: Chunk, data_type: str, date_str: str) -> Path:
        """Get cache file path for a chunk's data."""
        return self.cache_dir / f"{chunk.id}_{data_type}_{date_str}.json"
    
    def is_cached(self, chunk: Chunk, data_type: str, date_str: str) -> bool:
        """Check if chunk data is cached."""
        return self.get_cache_path(chunk, data_type, date_str).exists()
    
    def save_to_cache(self, chunk: Chunk, data_type: str, date_str: str, data: Dict) -> None:
        """Save chunk data to cache."""
        cache_path = self.get_cache_path(chunk, data_type, date_str)
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    
    def load_from_cache(self, chunk: Chunk, data_type: str, date_str: str) -> Optional[Dict]:
        """Load chunk data from cache."""
        cache_path = self.get_cache_path(chunk, data_type, date_str)
        if cache_path.exists():
            with open(cache_path, 'r') as f:
                return json.load(f)
        return None
    
    def get_unprocessed_chunks(self) -> List[Chunk]:
        """Get list of chunks that haven't been processed yet."""
        return [c for c in self.chunks if not c.is_processed]
    
    def get_processed_chunks(self) -> List[Chunk]:
        """Get list of successfully processed chunks."""
        return [c for c in self.chunks if c.is_processed and c.error is None]
    
    def get_failed_chunks(self) -> List[Chunk]:
        """Get list of chunks that failed processing."""
        return [c for c in self.chunks if c.error is not None]
    
    def summary(self) -> Dict[str, Any]:
        """Get processing summary."""
        return {
            "total_chunks": len(self.chunks),
            "processed": len(self.get_processed_chunks()),
            "failed": len(self.get_failed_chunks()),
            "pending": len(self.get_unprocessed_chunks()),
            "bounds": self.get_merged_bounds(),
        }
    
    def to_geojson(self) -> Dict:
        """Export all chunks as GeoJSON FeatureCollection."""
        features = []
        for chunk in self.chunks:
            feature = {
                "type": "Feature",
                "properties": {
                    "id": chunk.id,
                    "q_vi": chunk.q_vi,
                    "q_si": chunk.q_si,
                    "q_bi": chunk.q_bi,
                    "q_relief": chunk.q_relief,
                    "q_otu": chunk.q_otu,
                    "is_processed": chunk.is_processed,
                    "missing_data": chunk.missing_data,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [chunk.min_lon, chunk.min_lat],
                        [chunk.max_lon, chunk.min_lat],
                        [chunk.max_lon, chunk.max_lat],
                        [chunk.min_lon, chunk.max_lat],
                        [chunk.min_lon, chunk.min_lat],
                    ]]
                }
            }
            features.append(feature)
        
        return {
            "type": "FeatureCollection",
            "features": features,
        }
    
    def save_geojson(self, output_path: str) -> None:
        """Save chunks to GeoJSON file."""
        with open(output_path, 'w') as f:
            json.dump(self.to_geojson(), f, indent=2)
    
    def get_otu_statistics(self) -> Dict[str, float]:
        """Calculate statistics for OTU values across all processed chunks."""
        otu_values = [c.q_otu for c in self.get_processed_chunks() if c.q_otu is not None]
        
        if not otu_values:
            return {"mean": 0, "std": 0, "min": 0, "max": 0, "count": 0}
        
        arr = np.array(otu_values)
        return {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "median": float(np.median(arr)),
            "count": len(otu_values),
        }
