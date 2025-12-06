# Proton Monte Carlo Toolkit

Prototype implementation for ballistic dispersion modeling and ecological impact assessment of the Proton launch vehicle first-stage drop zone.

## Quick start

1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies: `pip install -r requirements.txt`.
3. Authenticate with Google Earth Engine if you plan to pull remote datasets.
4. Run a demo batch: `python main.py`.

## Project layout

- `config/` – Rocket constants, simulation knobs, GEE dataset references.
- `core/` – Atmosphere model, equations of motion, simple RK4 propagator, Monte Carlo driver.
- `gee/` – Lightweight wrappers for fetching NDVI/DEM/soil/water data and transforming them into indicators.
- `grid/` – Helpers for generating a 1×1 km grid and computing dispersion ellipses.
- `indices/` – Translating raw indicators into the composite ecological index $Q_{OTU}$.
- `visualization/` – Placeholders for maps, heatmaps, and reports.
- `tests/` – Smoke tests that validate the physics helpers and index math.

## Next steps

- Hook up real GEE reducers for NDVI, DEM, soil, and water datasets.
- Add cross-range modeling driven by azimuth perturbations and winds.
- Feed processed rasters into `grid/cell_calculator.py` to produce $Q_{OTU}$ maps.
- Extend visualization modules for publication-grade figures.
