"""Lightweight smoke test runner."""

from core.ballistics import BallisticModel


def main() -> None:
	model = BallisticModel(reference_area_m2=40.0, dry_mass_kg=30_000.0)
	derivs = model.derivatives(0.0, [0.0, 43_000.0, 1_700.0, 0.2, 0.0, 0.0])
	print("Derivatives:", derivs)


if __name__ == "__main__":
	main()
