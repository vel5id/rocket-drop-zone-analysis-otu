from config.simulation_config import build_default_config
from core.ballistics import BallisticModel
from core.monte_carlo import MonteCarloSimulator


def test_monte_carlo_runs_with_defaults():
    model = BallisticModel(reference_area_m2=40.0, dry_mass_kg=30_000.0)
    config = build_default_config()
    config.iterations = 5
    simulator = MonteCarloSimulator(model, config)
    samples = list(simulator.run())
    assert len(samples) == 5
