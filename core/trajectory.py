"""Trajectory propagation helpers built on top of a custom RK4 integrator (3D)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import numpy as np

from core.ballistics import BallisticModel


@dataclass
class TrajectoryResult:
    """Stores dense trajectory outputs for further analysis."""

    time_s: np.ndarray
    state: np.ndarray  # shape (6, N) for 3D: [dr, cr, alt, vel, gamma, psi]

    @property
    def impact_index(self) -> int:
        """Return the index where altitude crosses zero or the last sample."""
        altitude = self.state[2]  # altitude is now index 2
        below_ground = np.where(altitude <= 0)[0]
        return int(below_ground[0]) if below_ground.size else len(altitude) - 1

    @property
    def impact_state(self) -> np.ndarray:
        """Return state vector at impact."""
        return self.state[:, self.impact_index]
    
    @property
    def impact_downrange(self) -> float:
        """Downrange distance at impact [m]."""
        return float(self.impact_state[0])
    
    @property
    def impact_crossrange(self) -> float:
        """Crossrange distance at impact [m]."""
        return float(self.impact_state[1])
    
    @property
    def impact_velocity(self) -> float:
        """Velocity at impact [m/s]."""
        return float(self.impact_state[3])


def _rk4_step(
    model: BallisticModel,
    t: float,
    y: np.ndarray,
    dt: float,
    model_kwargs: Mapping[str, float],
) -> np.ndarray:
    """Runge-Kutta 4 integrator step."""
    k1 = np.array(model.derivatives(t, y.tolist(), **model_kwargs))
    k2 = np.array(model.derivatives(t + 0.5 * dt, (y + 0.5 * dt * k1).tolist(), **model_kwargs))
    k3 = np.array(model.derivatives(t + 0.5 * dt, (y + 0.5 * dt * k2).tolist(), **model_kwargs))
    k4 = np.array(model.derivatives(t + dt, (y + dt * k3).tolist(), **model_kwargs))
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


def propagate_trajectory(
    model: BallisticModel,
    initial_state: Sequence[float],
    *,
    t_span: tuple[float, float],
    max_step: float = 0.5,
    model_kwargs: Mapping[str, float] | None = None,
) -> TrajectoryResult:
    """Integrate equations of motion until the altitude becomes non-positive."""
    start, stop = t_span
    if stop <= start:
        raise ValueError("t_span must have stop > start")

    times = [start]
    states = [np.array(initial_state, dtype=float)]

    t = start
    state_vec = states[0]
    extra_kwargs: dict[str, float] = dict(model_kwargs or {})

    # Altitude is at index 2 for 3D state
    altitude_index = 2

    while t < stop and state_vec[altitude_index] > 0.0:
        state_vec = _rk4_step(model, t, state_vec, max_step, extra_kwargs)
        t += max_step
        times.append(t)
        states.append(state_vec)

    state_matrix = np.vstack([s for s in states]).T
    return TrajectoryResult(time_s=np.array(times), state=state_matrix)
