from core.atmosphere import ExponentialAtmosphere
from core.ballistics import BallisticModel


def test_density_decreases_with_altitude():
    atmosphere = ExponentialAtmosphere()
    rho_low = atmosphere.density(1_000)
    rho_high = atmosphere.density(10_000)
    assert rho_high < rho_low


def test_ballistic_model_returns_six_derivatives():
    model = BallisticModel(reference_area_m2=40.0, dry_mass_kg=30_000.0)
    # state: [downrange, crossrange, altitude, velocity, gamma, psi]
    derivs = model.derivatives(0.0, [0.0, 40_000.0, 1_700.0, 0.2, 0.0, 0.0])
    assert len(derivs) == 6
