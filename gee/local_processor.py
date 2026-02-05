"""
Smart Tiled GeoTIFF Downloader.

Automatically calculates tile sizes to stay under GEE 50MB limit.
Downloads tiles and mosaics them locally for fast processing.
"""
import os
import math
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
import requests
import zipfile
import io
import shutil

try:
    import rasterio
    from rasterio.merge import merge
    HAS_RASTERIO = True
except ImportError:
    HAS_RASTERIO = False

try:
    import ee
    HAS_GEE = True
except ImportError:
    ee = None
    HAS_GEE = False


@dataclass
class TileInfo:
    """Information about a single tile."""
    id: int
    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float
    width_px: int
    height_px: int
    size_mb: float


@dataclass  
class DownloadPlan:
    """Download plan with tile information."""
    bounds: Tuple[float, float, float, float]
    scale_m: int
    total_width_px: int
    total_height_px: int
    total_size_mb: float
    num_tiles: int
    tiles: List[TileInfo]


# GEE limit is 50MB, we use 25MB to be safe
GEE_MAX_SIZE_MB = 25


def calculate_download_plan(bounds, scale_m, bytes_per_pixel=4):
    """Calculate how many tiles needed and their sizes."""
    min_lon, min_lat, max_lon, max_lat = bounds
    
    mid_lat = (min_lat + max_lat) / 2
    lat_km = (max_lat - min_lat) * 111
    lon_km = (max_lon - min_lon) * 111 * math.cos(math.radians(mid_lat))
    
    width_px = int(lon_km * 1000 / scale_m)
    height_px = int(lat_km * 1000 / scale_m)
    
    total_bytes = width_px * height_px * bytes_per_pixel
    total_size_mb = total_bytes / (1024 * 1024)
    
    if total_size_mb <= GEE_MAX_SIZE_MB:
        num_tiles = 1
        tiles_x = 1
        tiles_y = 1
    else:
        num_tiles = math.ceil(total_size_mb / GEE_MAX_SIZE_MB)
        tiles_x = max(1, int(math.ceil(math.sqrt(num_tiles * (lon_km / max(lat_km, 0.01))))))
        tiles_y = max(1, int(math.ceil(num_tiles / tiles_x)))
    
    tiles = []
    tile_width = (max_lon - min_lon) / tiles_x
    tile_height = (max_lat - min_lat) / tiles_y
    
    tile_id = 0
    for ty in range(tiles_y):
        for tx in range(tiles_x):
            t_min_lon = min_lon + tx * tile_width
            t_max_lon = min_lon + (tx + 1) * tile_width
            t_min_lat = min_lat + ty * tile_height
            t_max_lat = min_lat + (ty + 1) * tile_height
            
            t_width_px = max(1, int((t_max_lon - t_min_lon) * 111 * math.cos(math.radians(mid_lat)) * 1000 / scale_m))
            t_height_px = max(1, int((t_max_lat - t_min_lat) * 111 * 1000 / scale_m))
            t_size_mb = t_width_px * t_height_px * bytes_per_pixel / (1024 * 1024)
            
            tiles.append(TileInfo(
                id=tile_id,
                min_lon=t_min_lon, min_lat=t_min_lat,
                max_lon=t_max_lon, max_lat=t_max_lat,
                width_px=t_width_px, height_px=t_height_px,
                size_mb=t_size_mb
            ))
            tile_id += 1
    
    return DownloadPlan(
        bounds=bounds,
        scale_m=scale_m,
        total_width_px=width_px,
        total_height_px=height_px,
        total_size_mb=total_size_mb,
        num_tiles=len(tiles),
        tiles=tiles
    )


def print_download_plan(plan, name="Data"):
    """Print download plan summary."""
    print(f"\n  [DOWNLOAD PLAN] {name}:")
    print(f"     Resolution: {plan.scale_m}m")
    print(f"     Total size: {plan.total_width_px}x{plan.total_height_px} px")
    print(f"     Estimated: {plan.total_size_mb:.1f} MB")
    print(f"     Tiles: {plan.num_tiles}")
    for t in plan.tiles[:3]:
        print(f"       Tile {t.id}: {t.width_px}x{t.height_px} ({t.size_mb:.1f} MB)")
    if len(plan.tiles) > 3:
        print(f"       ... and {len(plan.tiles) - 3} more")


def download_tile(image, tile, scale_m, output_path, timeout=300):
    """Download a single tile from GEE."""
    region = ee.Geometry.Rectangle([
        tile.min_lon, tile.min_lat, tile.max_lon, tile.max_lat
    ])
    
    try:
        url = image.getDownloadURL({
            'region': region,
            'scale': scale_m,
            'format': 'GEO_TIFF',
            'crs': 'EPSG:4326'
        })
    except Exception as e:
        print(f"  [ERROR] Tile {tile.id}: {e}")
        return None
    
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except Exception as e:
        print(f"  [ERROR] Tile {tile.id} download: {e}")
        return None
    
    content = response.content
    if response.headers.get('content-type', '').startswith('application/zip'):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            tif_names = [n for n in z.namelist() if n.endswith('.tif')]
            if tif_names:
                content = z.read(tif_names[0])
    
    with open(output_path, 'wb') as f:
        f.write(content)
    
    return output_path


def download_and_mosaic(image, plan, output_dir, output_name):
    """Download all tiles and mosaic them into one file."""
    os.makedirs(output_dir, exist_ok=True)
    tile_dir = os.path.join(output_dir, f"{output_name}_tiles")
    os.makedirs(tile_dir, exist_ok=True)
    
    tile_paths = []
    for i, tile in enumerate(plan.tiles):
        tile_path = os.path.join(tile_dir, f"tile_{tile.id}.tif")
        print(f"  Tile {i+1}/{len(plan.tiles)} ({tile.size_mb:.1f}MB)...", end=" ", flush=True)
        
        result = download_tile(image, tile, plan.scale_m, tile_path)
        if result:
            tile_paths.append(result)
            print("OK")
        else:
            print("FAILED")
    
    if not tile_paths:
        print("  [ERROR] No tiles downloaded!")
        shutil.rmtree(tile_dir, ignore_errors=True)
        return None
    
    output_path = os.path.join(output_dir, f"{output_name}.tif")
    
    if len(tile_paths) == 1:
        shutil.copy(tile_paths[0], output_path)
    else:
        print(f"  Mosaicing {len(tile_paths)} tiles...")
        try:
            datasets = [rasterio.open(p) for p in tile_paths]
            mosaic, transform = merge(datasets)
            
            profile = datasets[0].profile.copy()
            profile.update({
                'height': mosaic.shape[1],
                'width': mosaic.shape[2],
                'transform': transform,
            })
            
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(mosaic)
            
            for ds in datasets:
                ds.close()
        except Exception as e:
            print(f"  [ERROR] Mosaic failed: {e}")
            shutil.rmtree(tile_dir, ignore_errors=True)
            return None
    
    shutil.rmtree(tile_dir, ignore_errors=True)
    
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Saved: {output_path} ({file_size_mb:.1f} MB)")
    
    return output_path


def fetch_ndvi_tiled(grid_cells, target_date, cache_dir="output/gee_cache", scale_m=20, cloud_threshold=20):
    """Fetch NDVI using smart tiled downloads at specified resolution."""
    from datetime import datetime, timedelta
    
    lats = [c.center_lat for c in grid_cells]
    lons = [c.center_lon for c in grid_cells]
    bounds = (min(lons) - 0.05, min(lats) - 0.05, max(lons) + 0.05, max(lats) + 0.05)
    
    # Use full month composite for better coverage
    date = datetime.strptime(target_date, "%Y-%m-%d")
    year = date.year
    month = date.month
    start = f"{year}-{month:02d}-01"
    # Get last day of month
    if month == 12:
        end = f"{year+1}-01-01"
    else:
        end = f"{year}-{month+1:02d}-01"
    
    cache_path = os.path.join(cache_dir, f"ndvi_{year}-{month:02d}_{scale_m}m.tif")
    
    if os.path.exists(cache_path):
        print(f"  Using cached NDVI: {cache_path}")
    else:
        plan = calculate_download_plan(bounds, scale_m)
        print_download_plan(plan, f"NDVI ({year}-{month:02d})")
        
        print(f"  NDVI composite: {start} to {end} (Cloud < {cloud_threshold}%)")
        
        s2 = (ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
              .filterBounds(ee.Geometry.Rectangle(list(bounds)))
              .filterDate(start, end)
              .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold)))
        
        def mask_clouds(img):
            qa = img.select("QA60")
            mask = qa.bitwiseAnd(1 << 10).eq(0).And(qa.bitwiseAnd(1 << 11).eq(0))
            return img.updateMask(mask)
        
        composite = s2.map(mask_clouds).median()
        ndvi = composite.normalizedDifference(["B8", "B4"]).rename("NDVI")
        
        result = download_and_mosaic(ndvi, plan, cache_dir, f"ndvi_{year}-{month:02d}_{scale_m}m")
        if not result:
            return np.full(len(grid_cells), np.nan)
        cache_path = result
    
    return sample_geotiff_at_points(cache_path, grid_cells)


def fetch_soil_tiled(grid_cells, cache_dir="output/gee_cache", scale_m=250):
    """Fetch soil data using tiled downloads."""
    lats = [c.center_lat for c in grid_cells]
    lons = [c.center_lon for c in grid_cells]
    bounds = (min(lons) - 0.05, min(lats) - 0.05, max(lons) + 0.05, max(lats) + 0.05)
    
    layers = {
        "bdod": ("projects/soilgrids-isric/bdod_mean", "bdod_0-5cm_mean", 1300),
        "clay": ("projects/soilgrids-isric/clay_mean", "clay_0-5cm_mean", 200),
        "soc": ("projects/soilgrids-isric/soc_mean", "soc_0-5cm_mean", 50),
        "nitrogen": ("projects/soilgrids-isric/nitrogen_mean", "nitrogen_0-5cm_mean", 2),
    }
    
    plan = calculate_download_plan(bounds, scale_m)
    print_download_plan(plan, "Soil")
    
    results = {}
    for name, (asset, band, default) in layers.items():
        cache_path = os.path.join(cache_dir, f"soil_{name}.tif")
        
        if os.path.exists(cache_path):
            print(f"  Using cached {name}")
        else:
            print(f"  Downloading {name}...")
            img = ee.Image(asset).select(band)
            result = download_and_mosaic(img, plan, cache_dir, f"soil_{name}")
            if not result:
                results[name] = np.full(len(grid_cells), default)
                continue
            cache_path = result
        
        results[name] = sample_geotiff_at_points(cache_path, grid_cells, default=default)
    
    return np.column_stack([
        results.get("bdod", np.full(len(grid_cells), 1300)),
        results.get("clay", np.full(len(grid_cells), 200)),
        results.get("soc", np.full(len(grid_cells), 50)),
        results.get("nitrogen", np.full(len(grid_cells), 2)),
    ])


def fetch_relief_tiled(grid_cells, cache_dir="output/gee_cache", scale_m=30):
    """Fetch relief data using tiled downloads."""
    lats = [c.center_lat for c in grid_cells]
    lons = [c.center_lon for c in grid_cells]
    bounds = (min(lons) - 0.05, min(lats) - 0.05, max(lons) + 0.05, max(lats) + 0.05)
    
    plan = calculate_download_plan(bounds, scale_m)
    print_download_plan(plan, "Relief")
    
    dem = ee.Image("USGS/SRTMGL1_003")
    terrain = ee.Terrain.products(dem)
    
    results = {}
    for name, img in [("slope", terrain.select("slope")), ("aspect", terrain.select("aspect"))]:
        cache_path = os.path.join(cache_dir, f"relief_{name}.tif")
        
        if os.path.exists(cache_path):
            print(f"  Using cached {name}")
        else:
            print(f"  Downloading {name}...")
            result = download_and_mosaic(img, plan, cache_dir, f"relief_{name}")
            if result:
                cache_path = result
        
        default = 0 if name == "slope" else 180
        if os.path.exists(cache_path):
            results[name] = sample_geotiff_at_points(cache_path, grid_cells, default=default)
        else:
            results[name] = np.full(len(grid_cells), default)
    
    # Water occurrence
    water_path = os.path.join(cache_dir, "relief_water.tif")
    if not os.path.exists(water_path):
        print("  Downloading water...")
        water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
        download_and_mosaic(water, plan, cache_dir, "relief_water")
    
    if os.path.exists(water_path):
        water_data = sample_geotiff_at_points(water_path, grid_cells, default=0)
    else:
        water_data = np.zeros(len(grid_cells))
    
    return np.column_stack([
        results.get("slope", np.zeros(len(grid_cells))),
        water_data,
        results.get("aspect", np.full(len(grid_cells), 180)),
    ])


def sample_geotiff_at_points(geotiff_path, grid_cells, default=np.nan):
    """Sample GeoTIFF values at grid cell center points."""
    n_points = len(grid_cells)
    values = np.full(n_points, default, dtype=np.float32)
    
    if not os.path.exists(geotiff_path):
        return values
    
    try:
        with rasterio.open(geotiff_path) as src:
            transform = src.transform
            data = src.read(1)
            nodata = src.nodata
            
            # Vectorized coordinate transformation
            lons = np.array([c.center_lon for c in grid_cells])
            lats = np.array([c.center_lat for c in grid_cells])

            # ~transform * (x, y) returns (cols, rows) in float
            cols_float, rows_float = ~transform * (lons, lats)

            # Convert to indices (int() truncates towards 0, matching original behavior)
            cols = cols_float.astype(int)
            rows = rows_float.astype(int)

            height, width = data.shape

            # Valid indices mask
            valid_mask = (rows >= 0) & (rows < height) & (cols >= 0) & (cols < width)

            if np.any(valid_mask):
                # Extract values for valid coordinates
                valid_rows = rows[valid_mask]
                valid_cols = cols[valid_mask]

                extracted_values = data[valid_rows, valid_cols]

                # Check for valid data (nodata and NaN)
                is_data_valid = ~np.isnan(extracted_values)
                if nodata is not None:
                    is_data_valid &= (extracted_values != nodata)

                # Update 'values' array where both coordinates and data are valid
                valid_indices = np.where(valid_mask)[0]
                final_indices = valid_indices[is_data_valid]
                final_values = extracted_values[is_data_valid]
                
                values[final_indices] = final_values
    except Exception as e:
        print(f"  [ERROR] Sampling {geotiff_path}: {e}")
    
    valid = np.sum(~np.isnan(values)) if np.issubdtype(values.dtype, np.floating) else n_points
    print(f"  Sampled: {valid}/{n_points} valid ({100*valid/n_points:.1f}%)")
    
    return values
