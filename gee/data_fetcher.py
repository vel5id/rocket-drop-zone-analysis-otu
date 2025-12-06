"""High level wrapper for downloading rasters from GEE."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

try:  # pragma: no cover - optional dependency
    import ee as _ee  # type: ignore
except ImportError as exc:  # pragma: no cover - informative only
    _IMPORT_ERROR_INFO: Exception | None = exc
    _ee = None  # type: ignore
else:  # pragma: no cover - executed when ee is available
    _IMPORT_ERROR_INFO = None

from config import gee_config

ee: Any | None = _ee


def _ensure_ee() -> Any:
    if ee is None:
        raise ModuleNotFoundError(
            "earthengine-api is required. Install it via 'pip install earthengine-api'."
        ) from _IMPORT_ERROR_INFO
    return ee


@dataclass
class AreaOfInterest:
    """Defines the spatial bounds for data extraction."""

    center_lon: float
    center_lat: float
    buffer_m: float

    def as_geometry(self) -> Any:
        fetcher = _ensure_ee()
        point = fetcher.Geometry.Point([self.center_lon, self.center_lat])
        return point.buffer(self.buffer_m)


class GEEDataFetcher:
    """Prepares imagery collections that downstream modules can sample."""

    def __init__(self, aoi: AreaOfInterest):
        _ensure_ee()
        self._aoi = aoi

    def fetch_ndvi(self, start_date: str, end_date: str) -> Any:
        fetcher = _ensure_ee()
        collection = (
            fetcher.ImageCollection(gee_config.NDVI_DATASET.collection_id)
            .filterDate(start_date, end_date)
            .filterBounds(self._aoi.as_geometry())
            .select("NDVI")
        )
        return collection.mean().multiply(0.0001)

    def fetch_dem(self) -> Any:
        fetcher = _ensure_ee()
        return fetcher.Image(gee_config.DEM_DATASET.collection_id)

    def fetch_water(self) -> Any:
        fetcher = _ensure_ee()
        return fetcher.Image(gee_config.WATER_DATASET.collection_id).select("occurrence")

    def fetch_soil(self) -> Any:
        fetcher = _ensure_ee()
        return fetcher.Image(gee_config.SOIL_DATASET.collection_id)

    def export_tiles(self, images: Iterable[tuple[str, Any]], *, scale: int = 250) -> None:
        _ = images, scale  # Placeholder: implement once export strategy is defined.
