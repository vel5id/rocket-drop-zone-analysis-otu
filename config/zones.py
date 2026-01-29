"""
Predefined Drop Zones configuration.
Source: https://adilet.zan.kz/rus/docs/U950002195_
"""
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class ZoneDefinition:
    name: str
    center_lat: float
    center_lon: float
    semi_major_km: float
    semi_minor_km: float
    angle_deg: float  # Angle from North (0=N, 90=E)
    description: Optional[str] = None

# Ю-24 (Karaganda region)
# Zone 15: 47 deg 20'00" N, 66 deg 46'30" E, size 27x18 km, angle ~75 deg
# Zone 25: 47 deg 14'00" N, 66 deg 23'00" E, size 60x30 km, angle ~75 deg

YU24_ZONES: Dict[str, ZoneDefinition] = {
    "yu24_15": ZoneDefinition(
        name="Ю-24 Zone 15",
        center_lat=47 + 20/60,
        center_lon=66 + 46/60 + 30/3600,
        semi_major_km=27.0,
        semi_minor_km=18.0,
        angle_deg=75.0,
        description="Primary impact zone for Soyuz stages"
    ),
    "yu24_25": ZoneDefinition(
        name="Ю-24 Zone 25",
        center_lat=47 + 14/60,
        center_lon=66 + 23/60,
        semi_major_km=60.0,
        semi_minor_km=30.0,
        angle_deg=75.0,
        description="Fragment dispersion zone"
    ),
}

# All available zones registry
ALL_ZONES = {**YU24_ZONES}
