"""Map rendering helpers built on top of Folium when available."""
from __future__ import annotations

from typing import Any, Iterable

try:  # pragma: no cover - optional dependency
    import folium
except ImportError:  # pragma: no cover - degrade gracefully
    folium = None  # type: ignore


class MapRenderer:
    """Builds interactive Leaflet maps for dispersion and Q_OTU layers."""

    def __init__(self, *, center: tuple[float, float], zoom_start: int = 6) -> None:
        if folium is None:
            raise ModuleNotFoundError("folium is required for MapRenderer")
        self._map = folium.Map(location=center, zoom_start=zoom_start, tiles="CartoDB positron")

    def add_points(self, points: Iterable[tuple[float, float]], **style: Any) -> None:
        if folium is None:
            return
        for lat, lon in points:
            folium.CircleMarker(location=(lat, lon), radius=style.get("radius", 3), color=style.get("color", "red"), fill=True).add_to(self._map)

    def render(self) -> Any:
        return self._map
