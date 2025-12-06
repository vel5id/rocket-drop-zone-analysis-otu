"""Geographic coordinate utilities for converting simulation outputs to lat/lon."""
from __future__ import annotations

import math
from dataclasses import dataclass

# Earth parameters
EARTH_RADIUS_M = 6_371_000.0


@dataclass
class GeoPoint:
    """A point in geographic coordinates."""
    lat: float
    lon: float


def meters_to_latlon(
    launch_lat: float,
    launch_lon: float,
    azimuth_deg: float,
    downrange_m: float,
    crossrange_m: float = 0.0,
) -> GeoPoint:
    """
    Convert downrange/crossrange displacement to geographic coordinates.
    
    Args:
        launch_lat: Launch point latitude in degrees
        launch_lon: Launch point longitude in degrees
        azimuth_deg: Launch azimuth in degrees (0=North, 90=East)
        downrange_m: Downrange distance in meters (along azimuth)
        crossrange_m: Crossrange distance in meters (perpendicular, positive=right)
    
    Returns:
        GeoPoint with impact latitude and longitude
    """
    # Convert to radians
    lat1 = math.radians(launch_lat)
    lon1 = math.radians(launch_lon)
    azimuth = math.radians(azimuth_deg)
    
    # Compute total displacement vector
    # Downrange is along azimuth, crossrange is perpendicular (90° clockwise)
    dx = downrange_m * math.sin(azimuth) + crossrange_m * math.sin(azimuth + math.pi / 2)
    dy = downrange_m * math.cos(azimuth) + crossrange_m * math.cos(azimuth + math.pi / 2)
    
    # Angular distance
    total_distance = math.sqrt(dx**2 + dy**2)
    angular_dist = total_distance / EARTH_RADIUS_M
    
    # Bearing from components
    if total_distance > 0:
        bearing = math.atan2(dx, dy)
    else:
        bearing = 0.0
    
    # Haversine forward calculation
    lat2 = math.asin(
        math.sin(lat1) * math.cos(angular_dist) +
        math.cos(lat1) * math.sin(angular_dist) * math.cos(bearing)
    )
    lon2 = lon1 + math.atan2(
        math.sin(bearing) * math.sin(angular_dist) * math.cos(lat1),
        math.cos(angular_dist) - math.sin(lat1) * math.sin(lat2)
    )
    
    return GeoPoint(
        lat=math.degrees(lat2),
        lon=math.degrees(lon2)
    )


def latlon_to_meters(
    launch_lat: float,
    launch_lon: float,
    impact_lat: float,
    impact_lon: float,
    azimuth_deg: float,
) -> tuple[float, float]:
    """
    Convert geographic coordinates to downrange/crossrange displacement.
    
    Returns:
        Tuple of (downrange_m, crossrange_m)
    """
    # Convert to radians
    lat1, lon1 = math.radians(launch_lat), math.radians(launch_lon)
    lat2, lon2 = math.radians(impact_lat), math.radians(impact_lon)
    azimuth = math.radians(azimuth_deg)
    
    # Haversine distance
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    distance = EARTH_RADIUS_M * c
    
    # Bearing from point 1 to point 2
    y = math.sin(dlon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlon)
    bearing = math.atan2(y, x)
    
    # Decompose into downrange (along azimuth) and crossrange (perpendicular)
    angle_diff = bearing - azimuth
    downrange = distance * math.cos(angle_diff)
    crossrange = distance * math.sin(angle_diff)
    
    return downrange, crossrange
