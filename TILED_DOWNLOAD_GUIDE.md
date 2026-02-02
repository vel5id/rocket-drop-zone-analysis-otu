"""Configuration for enabling tile-based GEE downloads.

Add this to your calculator initialization to enable fast tile-based processing:

    calculator = OTUCalculator(
        chunk_manager=manager,
        use_tiled_download=True  # ← Enable this!
    )

This will:
- Reduce GEE requests from ~1500 to ~10-20
- Speed up processing by 5-10x
- Cache tiles for instant re-runs

Requirements:
    pip install rasterio
"""

# To enable globally, modify otu/calculator.py:
# 1. Add import at top:
#    from gee.local_processor import fetch_ndvi_tiled, fetch_soil_tiled, fetch_relief_tiled
#
# 2. In __init__, add parameter:
#    def __init__(self, chunk_manager, output_dir="output/otu", use_tiled_download=False):
#        self.use_tiled_download = use_tiled_download
#
# 3. In _fetch_ndvi_for_chunks, add at start:
#    if self.use_tiled_download:
#        try:
#            return fetch_ndvi_tiled(
#                grid_cells=list(self.chunk_manager.chunks),
#                target_date=target_date,
#                cache_dir="output/gee_cache",
#                scale_m=30
#            )
#        except ImportError:
#            print("  [WARN] rasterio not installed, falling back to batch mode")
#
# Same for _fetch_soil_for_chunks and _fetch_relief_for_chunks
