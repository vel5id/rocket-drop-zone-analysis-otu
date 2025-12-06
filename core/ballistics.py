"""Ballistic equations of motion for a tumbling first stage (3D model)."""
from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Callable

from core.atmosphere import Atmosphere, ExponentialAtmosphere

EARTH_RADIUS_M = 6_371_000.0
STANDARD_GRAVITY = 9.80665
GAMMA_AIR = 1.4  # Ratio of specific heats for air
R_AIR = 287.05  # Gas constant for air [J/(kg·K)]


@dataclass
class BallisticState:
    """State vector for a 3D fall."""
    downrange_m: float
    crossrange_m: float
    altitude_m: float
    velocity_m_s: float
    flight_path_angle_rad: float
    heading_rad: float  # Azimuth angle


def speed_of_sound(temperature_k: float) -> float:
    """Calculate speed of sound from temperature using ideal gas law."""
    return math.sqrt(GAMMA_AIR * R_AIR * max(temperature_k, 100.0))


class BallisticModel:
    """Computes state derivatives for numerical propagators (3D model)."""

    def __init__(
        self,
        *,
        atmosphere: Atmosphere | None = None,
        reference_area_m2: float,
        dry_mass_kg: float,
        drag_coefficient_provider: Callable[[float], float] | None = None,
    ) -> None:
        self._atmosphere = atmosphere or ExponentialAtmosphere()
        self._area = reference_area_m2
        self._mass = dry_mass_kg

        def _default_drag_coefficient(_: float) -> float:
            return 1.0

        self._drag_coefficient_provider: Callable[[float], float] = (
            drag_coefficient_provider or _default_drag_coefficient
        )

    def derivatives(
        self,
        _t: float,
        state: list[float],
        *,
        density_factor: float = 1.0,
        wind_u_m_s: float = 0.0,  # Along-track wind (headwind positive)
        wind_v_m_s: float = 0.0,  # Cross-track wind (right positive)
        mass: float | None = None,
    ) -> list[float]:
        """
        Compute state derivatives for 3D ballistic trajectory.
        
        State vector: [downrange, crossrange, altitude, velocity, gamma, psi]
        - downrange: distance along nominal trajectory [m]
        - crossrange: lateral displacement [m]  
        - altitude: height above ground [m]
        - velocity: total speed [m/s]
        - gamma: flight path angle [rad] (positive up)
        - psi: heading angle [rad] (azimuth, 0=launch direction)
        """
        _downrange, _crossrange, altitude, velocity, gamma, psi = state
        
        # Atmospheric properties
        density = self._atmosphere.density(altitude, density_factor=density_factor)
        temperature = self._atmosphere.temperature(altitude)
        
        # Mach number from actual speed of sound
        a = speed_of_sound(temperature)
        mach = velocity / a
        
        # Drag coefficient
        drag_coeff = self._drag_coefficient_provider(mach)
        current_mass = mass if mass is not None else self._mass
        
        # Velocity components in trajectory frame
        v_along = velocity * math.cos(gamma)  # Horizontal component
        v_vert = velocity * math.sin(gamma)   # Vertical component
        
        # Wind-relative velocity (along-track and cross-track)
        v_rel_along = v_along - wind_u_m_s
        v_rel_cross = -wind_v_m_s  # Cross-track wind causes side force
        v_rel = math.sqrt(v_rel_along**2 + v_rel_cross**2 + v_vert**2)
        
        # Dynamic pressure and drag
        q = 0.5 * density * v_rel**2
        drag_force = q * drag_coeff * self._area
        drag_acc = drag_force / max(current_mass, 1.0)
        
        # Gravity (varies with altitude)
        gravity = STANDARD_GRAVITY * (EARTH_RADIUS_M / (EARTH_RADIUS_M + altitude)) ** 2
        
        # Decompose drag into along-track and normal components
        if v_rel > 1.0:
            # Drag opposes velocity
            drag_along = drag_acc * v_rel_along / v_rel
            drag_cross = drag_acc * v_rel_cross / v_rel
            drag_vert = drag_acc * v_vert / v_rel
        else:
            drag_along = drag_cross = drag_vert = 0.0
        
        # State derivatives
        # Position rates
        downrange_rate = velocity * math.cos(gamma) * math.cos(psi)
        crossrange_rate = velocity * math.cos(gamma) * math.sin(psi) - wind_v_m_s
        altitude_rate = velocity * math.sin(gamma)
        
        # Velocity rate (drag + gravity along velocity vector)
        velocity_rate = -gravity * math.sin(gamma) - drag_acc
        
        # Flight path angle rate
        if velocity > 1.0:
            gamma_rate = (-gravity * math.cos(gamma) + drag_cross * math.sin(psi)) / velocity
        else:
            gamma_rate = 0.0
        
        # Heading rate (due to cross-track forces)
        if velocity * math.cos(gamma) > 1.0:
            psi_rate = drag_cross / (velocity * math.cos(gamma))
        else:
            psi_rate = 0.0
        
        return [downrange_rate, crossrange_rate, altitude_rate, velocity_rate, gamma_rate, psi_rate]
