"""
Server Pipeline Module

Adapts run_otu_pipeline.py for UI/Backend use with safety limits:
1. Ellipse size limits (max 500km semi-major)
2. Grid cell caps (max 50,000 cells)
3. Fragment outlier filtering (IQR method)
4. Progress callbacks for UI updates
"""

from server_pipeline.simulation import (
    run_simulation_safe,
    SimulationResult,
)
from server_pipeline.ellipse import (
    compute_ellipse_safe,
    clamp_ellipse,
    filter_outliers_iqr,
)
from server_pipeline.grid_generator import (
    generate_grid_safe,
    MAX_GRID_CELLS,
)
from server_pipeline.geojson import (
    points_to_geojson,
    ellipse_to_geojson,
    grid_to_geojson,
)

__all__ = [
    # Simulation
    "run_simulation_safe",
    "SimulationResult",
    # Ellipse
    "compute_ellipse_safe",
    "clamp_ellipse",
    "filter_outliers_iqr",
    # Grid
    "generate_grid_safe",
    "MAX_GRID_CELLS",
    # GeoJSON
    "points_to_geojson",
    "ellipse_to_geojson",
    "grid_to_geojson",
]
