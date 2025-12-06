"""CLI entry point that runs a small Monte Carlo batch."""
from __future__ import annotations

from config.rocket_params import PROTON_STAGE_ONE
from config.simulation_config import build_default_config
from core.ballistics import BallisticModel
from core.monte_carlo import MonteCarloSimulator, collect_impacts


from core.aerodynamics import proton_drag_coefficient

def run_demo(iterations: int = 50) -> None:
    config = build_default_config()
    config.iterations = iterations
    model = BallisticModel(
        reference_area_m2=PROTON_STAGE_ONE.reference_area_m2,
        dry_mass_kg=PROTON_STAGE_ONE.dry_mass_kg,
        drag_coefficient_provider=proton_drag_coefficient,
    )
    simulator = MonteCarloSimulator(model, config)
    impacts = collect_impacts(simulator)
    print(f"Simulated {len(impacts)} impacts. First entry: {impacts[0]}")


def main() -> None:
    run_demo()


if __name__ == "__main__":
    main()
