"""Monte Carlo driver with fragmentation support for realistic dispersion modeling."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Sequence, List
import math

import numpy as np

from config.simulation_config import Perturbation, SimulationConfig, PROTON_FRAGMENTATION, FragmentationParams
from core.ballistics import BallisticModel
from core.trajectory import TrajectoryResult, propagate_trajectory


@dataclass
class ImpactRecord:
    """Holds the key results of a single simulation trial."""
    downrange_m: float
    crossrange_m: float
    impact_velocity_m_s: float
    flight_path_angle_rad: float
    heading_rad: float
    is_fragment: bool = False
    fragment_id: int = 0


class MonteCarloSimulator:
    """Handles sampling of input disturbances and orchestrates trajectory runs."""

    def __init__(
        self,
        model: BallisticModel,
        config: SimulationConfig,
        enable_fragmentation: bool = True,
        fragmentation_params: FragmentationParams | None = None,
    ) -> None:
        self._model = model
        self._config = config
        self._rng = np.random.default_rng(config.random_seed)
        self._enable_fragmentation = enable_fragmentation
        self._frag_params = fragmentation_params or PROTON_FRAGMENTATION

    def _sample(self, perturbation: Perturbation) -> float:
        distribution = perturbation.distribution
        params = perturbation.args
        if distribution == "normal":
            mean, sigma = params
            return float(self._rng.normal(mean, sigma))
        if distribution == "uniform":
            low, high = params
            return float(self._rng.uniform(low, high))
        if distribution == "poisson":
            (lam,) = params
            return float(self._rng.poisson(lam))
        raise ValueError(f"Unknown distribution: {distribution}")

    def _initial_state(self) -> Sequence[float]:
        """Generate initial state for primary body."""
        downrange = 0.0
        crossrange = 0.0
        altitude = self._sample(self._config.perturbations["initial_altitude"])
        velocity = self._sample(self._config.perturbations["initial_velocity"])
        gamma_deg = self._sample(self._config.perturbations["flight_path_angle"])
        gamma_rad = np.radians(gamma_deg)
        
        azimuth_deg = self._sample(self._config.perturbations["azimuth"])
        psi_rad = np.radians(azimuth_deg - 45.0)
        
        return [downrange, crossrange, altitude, velocity, gamma_rad, psi_rad]

    def _model_kwargs(self) -> dict[str, float]:
        return {
            "density_factor": self._sample(self._config.perturbations["air_density_factor"]),
            "wind_u_m_s": self._sample(self._config.perturbations["wind_u"]),
            "wind_v_m_s": self._sample(self._config.perturbations["wind_v"]),
            "mass": self._sample(self._config.perturbations["initial_mass"]),
        }

    def _simulate_primary(self) -> tuple[ImpactRecord, TrajectoryResult]:
        """Run single primary body trajectory."""
        state0 = self._initial_state()
        kwargs = self._model_kwargs()
        result = propagate_trajectory(
            self._model,
            state0,
            t_span=(0.0, self._config.max_time_s),
            max_step=self._config.time_step_s,
            model_kwargs=kwargs,
        )
        record = self._to_impact_record(result)
        return record, result

    def _generate_fragments(self, trajectory: TrajectoryResult) -> List[ImpactRecord]:
        """Generate fragment impacts from breakup during reentry."""
        fragments = []
        
        # Check if breakup occurs
        if self._rng.random() > self._frag_params.breakup_probability:
            return fragments
        
        # Find breakup point in trajectory (altitude in breakup range)
        altitudes = trajectory.state[2, :]
        for i, alt in enumerate(altitudes):
            if self._frag_params.breakup_altitude_min_m <= alt <= self._frag_params.breakup_altitude_max_m:
                breakup_idx = i
                break
        else:
            return fragments
        
        # State at breakup
        breakup_state = trajectory.state[:, breakup_idx]
        dr0, cr0, alt0, v0, gamma0, psi0 = breakup_state
        
        # Number of fragments
        num_frags = max(2, int(self._rng.normal(
            self._frag_params.num_fragments_mean,
            self._frag_params.num_fragments_sigma
        )))
        
        # Generate each fragment
        for frag_id in range(num_frags):
            # Delta-V from breakup
            delta_v = max(0, self._rng.normal(
                self._frag_params.breakup_delta_v_mean,
                self._frag_params.breakup_delta_v_sigma
            ))
            
            # Random direction spread
            angle_dev = np.radians(self._rng.normal(0, self._frag_params.breakup_angle_sigma))
            
            # New fragment state
            frag_state = [
                dr0,
                cr0,
                alt0,
                v0 + delta_v * math.cos(angle_dev),
                gamma0 + angle_dev * 0.5,
                psi0 + angle_dev,
            ]
            
            # Fragment mass (lighter than primary)
            if frag_id < len(self._frag_params.fragment_mass_fractions):
                mass_frac = self._frag_params.fragment_mass_fractions[frag_id]
            else:
                mass_frac = 0.05
            
            frag_mass = self._sample(self._config.perturbations["initial_mass"]) * mass_frac
            
            # Propagate fragment
            frag_kwargs = {
                "density_factor": self._sample(self._config.perturbations["air_density_factor"]),
                "wind_u_m_s": self._sample(self._config.perturbations["wind_u"]),
                "wind_v_m_s": self._sample(self._config.perturbations["wind_v"]),
                "mass": frag_mass,
            }
            
            try:
                frag_result = propagate_trajectory(
                    self._model,
                    frag_state,
                    t_span=(0.0, 300.0),  # Less time needed
                    max_step=self._config.time_step_s,
                    model_kwargs=frag_kwargs,
                )
                
                frag_record = self._to_impact_record(frag_result, is_fragment=True, fragment_id=frag_id)
                fragments.append(frag_record)
            except:
                pass  # Skip failed fragment propagations
        
        return fragments

    def run(self) -> Iterator[ImpactRecord]:
        """Run all Monte Carlo iterations."""
        for _ in range(self._config.iterations):
            primary_record, trajectory = self._simulate_primary()
            yield primary_record
            
            if self._enable_fragmentation:
                for frag in self._generate_fragments(trajectory):
                    yield frag

    def _to_impact_record(
        self,
        result: TrajectoryResult,
        is_fragment: bool = False,
        fragment_id: int = 0,
    ) -> ImpactRecord:
        impact_state = result.impact_state
        return ImpactRecord(
            downrange_m=impact_state[0],
            crossrange_m=impact_state[1],
            impact_velocity_m_s=impact_state[3],
            flight_path_angle_rad=impact_state[4],
            heading_rad=impact_state[5],
            is_fragment=is_fragment,
            fragment_id=fragment_id,
        )


def collect_impacts(simulator: MonteCarloSimulator) -> list[ImpactRecord]:
    """Utility to exhaust the simulator iterator and return a list."""
    return list(simulator.run())


def separate_primary_and_fragments(impacts: list[ImpactRecord]) -> tuple[list[ImpactRecord], list[ImpactRecord]]:
    """Separate primary body impacts from fragment impacts."""
    primary = [i for i in impacts if not i.is_fragment]
    fragments = [i for i in impacts if i.is_fragment]
    return primary, fragments
