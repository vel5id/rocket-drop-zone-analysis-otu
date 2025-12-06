"""Generation of 1x1 km analytical grids."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List


@dataclass
class GridCell:
    """Represents a single square cell in geographical coordinates."""

    min_lon: float
    min_lat: float
    max_lon: float
    max_lat: float

    @property
    def center(self) -> tuple[float, float]:
        return (
            (self.min_lon + self.max_lon) * 0.5,
            (self.min_lat + self.max_lat) * 0.5,
        )


@dataclass
class GridConfig:
    """Parameters that drive the regular grid construction."""

    center_lat: float
    center_lon: float
    radius_km: float
    cell_size_km: float = 1.0


def _km_to_deg_lat(distance_km: float) -> float:
    return distance_km / 111.0


def _km_to_deg_lon(distance_km: float, latitude_deg: float) -> float:
    return distance_km / (111.0 * math.cos(math.radians(latitude_deg)))


def build_grid(config: GridConfig) -> List[GridCell]:
    """Return a list of grid cells covering the area of interest."""

    lat_stride = _km_to_deg_lat(config.cell_size_km)
    lon_stride = _km_to_deg_lon(config.cell_size_km, config.center_lat)

    lat_extent = _km_to_deg_lat(config.radius_km)
    lon_extent = _km_to_deg_lon(config.radius_km, config.center_lat)

    lat_min = config.center_lat - lat_extent
    lat_max = config.center_lat + lat_extent
    lon_min = config.center_lon - lon_extent
    lon_max = config.center_lon + lon_extent

    cells: list[GridCell] = []
    lat = lat_min
    while lat < lat_max:
        lon = lon_min
        while lon < lon_max:
            cell = GridCell(
                min_lon=lon,
                min_lat=lat,
                max_lon=lon + lon_stride,
                max_lat=lat + lat_stride,
            )
            cells.append(cell)
            lon += lon_stride
        lat += lat_stride

    return cells
