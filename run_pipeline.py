"""Complete pipeline with GPU acceleration, tqdm progress bars, and visualization."""
from __future__ import annotations

import os
import json
import time
import numpy as np

try:
    from tqdm import tqdm
    import sys
    # Умный tqdm: отключается в неинтерактивном режиме
    def smart_tqdm(iterable, **kwargs):
        if not sys.stdout.isatty():
            # Неинтерактивный режим - отключаем прогресс-бар
            kwargs['disable'] = True
        return tqdm(iterable, **kwargs)
except ImportError:
    def smart_tqdm(iterable, **kwargs):
        desc = kwargs.get('desc', '')
        if desc:
            print(f"  {desc}...")
        return iterable

from config.rocket_params import PROTON_STAGE_ONE
from config.simulation_config import build_default_config, PROTON_FRAGMENTATION, HURRICANE_PERTURBATIONS
from core.aerodynamics import proton_drag_coefficient
from core.ballistics import BallisticModel
from core.monte_carlo import MonteCarloSimulator, collect_impacts, separate_primary_and_fragments
from core.geo_utils import meters_to_latlon, GeoPoint
from grid.ellipse_calculator import compute_dispersion_ellipse
from grid.grid_generator import build_grid, GridConfig


# Launch site (Baikonur)
LAUNCH_LAT = 45.72341
LAUNCH_LON = 63.32275
NOMINAL_AZIMUTH = 45.0


def run_simulation_gpu(
    iterations: int = 1000, 
    show_progress: bool = True,
    launch_lat: float = LAUNCH_LAT,
    launch_lon: float = LAUNCH_LON,
    azimuth: float = NOMINAL_AZIMUTH,
    sep_altitude: float = 43000.0,
    sep_velocity: float = 1738.0,
    sep_fp_angle: float = 25.0,
    sep_azimuth: float = 0.0,
    dry_mass_kg: float = 30600.0,
    reference_area_m2: float = 43.0,
    hurricane_mode: bool = False,
) -> tuple[list, list, float]:
    """Run simulation with GPU acceleration. Returns (primary_geo, fragment_geo, elapsed_time)."""
    try:
        from core.gpu_ballistics import propagate_batch, check_gpu_available, HAS_NUMBA
        
        if not HAS_NUMBA:
            print("  Numba not available, falling back to standard simulation")
            return run_simulation_standard(
                iterations, 
                show_progress,
                launch_lat=launch_lat,
                launch_lon=launch_lon,
                azimuth=azimuth,
                sep_altitude=sep_altitude,
                sep_velocity=sep_velocity,
                sep_fp_angle=sep_fp_angle,
                sep_azimuth=sep_azimuth,
                dry_mass_kg=dry_mass_kg,
                reference_area_m2=reference_area_m2,
                hurricane_mode=hurricane_mode,
            )
        
        print(f"Running GPU/parallel Monte Carlo ({iterations} iterations)...")
        if check_gpu_available():
            print("  CUDA GPU detected!")
        else:
            print("  Using CPU parallel (Numba)")
        
        config = build_default_config()
        if hurricane_mode:
            print("  [WARNING] HURRICANE MODE ACTIVE: Using high-entropy perturbation profile")
            config.perturbations = HURRICANE_PERTURBATIONS.copy()
            
        rng = np.random.default_rng(config.random_seed)
        
        # Generate all initial states
        print("  Generating initial states...")
        initial_states = np.zeros((iterations, 6), dtype=np.float64)
        params = np.zeros((iterations, 5), dtype=np.float64)
        
        gen_iter = range(iterations)
        if show_progress:
            gen_iter = smart_tqdm(gen_iter, desc="Generating states", leave=False)
        
        # Convert relative azimuth to absolute
        abs_azimuth = azimuth + sep_azimuth
        
        for i in gen_iter:
            initial_states[i] = [
                0.0, 
                0.0, 
                rng.normal(sep_altitude, 2000), 
                rng.normal(sep_velocity, 150),
                np.radians(rng.normal(sep_fp_angle, 4)), 
                np.radians(rng.normal(0, 3))
            ]
            params[i] = [rng.normal(1.0, 0.12), rng.normal(0, 40), rng.normal(0, 40),
                        rng.normal(dry_mass_kg, 500), rng.uniform(0.7, 1.5)]
        
        print("  Propagating trajectories...")
        start_time = time.time()
        results = propagate_batch(initial_states, params, dt=0.5, max_steps=1200,
                                  reference_area=reference_area_m2,
                                  base_mass=dry_mass_kg, use_gpu=True)
        elapsed = time.time() - start_time
        print(f"  Propagation: {elapsed:.2f}s ({iterations/elapsed:.0f} traj/sec)")
        
        # Convert to geo
        print("  Converting to geographic coordinates...")
        primary_geo = []
        conv_iter = range(iterations)
        if show_progress:
            conv_iter = smart_tqdm(conv_iter, desc="Converting primary", leave=False)
        
        for i in conv_iter:
            pt = meters_to_latlon(launch_lat, launch_lon, abs_azimuth, results[i, 0], results[i, 1])
            primary_geo.append({'lat': pt.lat, 'lon': pt.lon, 'is_fragment': False, 'velocity': results[i, 3]})
        
        # Generate fragments
        print("  Generating fragment impacts...")
        fragment_geo = []
        frag_params = PROTON_FRAGMENTATION
        
        frag_iter = range(iterations)
        if show_progress:
            frag_iter = smart_tqdm(frag_iter, desc="Generating fragments", leave=False)
        
        for i in frag_iter:
            if rng.random() > frag_params.breakup_probability:
                continue
            
            # Fragments start from ~70% of primary impact distance (breakup during descent)
            base_dr = results[i, 0] * 0.7
            base_cr = results[i, 1] * 0.7
            
            num_frags = max(2, int(rng.normal(frag_params.num_fragments_mean, frag_params.num_fragments_sigma)))
            
            for f in range(num_frags):
                spread_dr = rng.normal(0, 15000)
                spread_cr = rng.normal(0, 12000)
                pt = meters_to_latlon(launch_lat, launch_lon, abs_azimuth, base_dr + spread_dr, base_cr + spread_cr)
                fragment_geo.append({'lat': pt.lat, 'lon': pt.lon, 'is_fragment': True, 'fragment_id': f})
        
        print(f"  Primary: {len(primary_geo)}, Fragments: {len(fragment_geo)}")
        return primary_geo, fragment_geo, elapsed
        
    except Exception as e:
        print(f"  GPU acceleration failed: {e}")
        return run_simulation_standard(iterations, show_progress)


def run_simulation_standard(
    iterations: int = 1000, 
    show_progress: bool = True,
    launch_lat: float = LAUNCH_LAT,
    launch_lon: float = LAUNCH_LON,
    azimuth: float = NOMINAL_AZIMUTH,
    sep_altitude: float = 43000.0,
    sep_velocity: float = 1738.0,
    sep_fp_angle: float = 25.0,
    sep_azimuth: float = 0.0,
    dry_mass_kg: float = 30600.0,
    reference_area_m2: float = 43.0,
    hurricane_mode: bool = False,
) -> tuple[list, list, float]:
    """Standard CPU simulation with progress bars."""
    print(f"Running standard Monte Carlo ({iterations} iterations)...")
    
    config = build_default_config()
    if hurricane_mode:
        print("  [WARNING] HURRICANE MODE ACTIVE: Using high-entropy perturbation profile")
        config.perturbations = HURRICANE_PERTURBATIONS.copy()
        
    config.iterations = iterations
    
    # Update config with user parameters
    config.altitude_mean = sep_altitude
    config.velocity_mean = sep_velocity
    config.flight_path_angle_mean = sep_fp_angle
    
    # Absolute azimuth
    abs_azimuth = azimuth + sep_azimuth
    
    model = BallisticModel(
        reference_area_m2=reference_area_m2,
        dry_mass_kg=dry_mass_kg,
        drag_coefficient_provider=proton_drag_coefficient,
    )
    
    start_time = time.time()
    simulator = MonteCarloSimulator(model, config, enable_fragmentation=True)
    
    # Collect with progress
    impacts = []
    sim_iter = simulator.run()
    if show_progress:
        sim_iter = smart_tqdm(sim_iter, total=iterations * 5, desc="Simulating", leave=False)  # ~5 fragments per primary
    
    for impact in sim_iter:
        impacts.append(impact)
    
    elapsed = time.time() - start_time
    
    primary, fragments = separate_primary_and_fragments(impacts)
    print(f"  Completed in {elapsed:.2f}s")
    print(f"  Primary: {len(primary)}, Fragments: {len(fragments)}")
    
    # Convert to geo with progress
    print("  Converting to geographic coordinates...")
    primary_geo = []
    if show_progress:
        primary = smart_tqdm(primary, desc="Converting primary", leave=False)
    for imp in primary:
        pt = meters_to_latlon(launch_lat, launch_lon, abs_azimuth, imp.downrange_m, imp.crossrange_m)
        primary_geo.append({'lat': pt.lat, 'lon': pt.lon, 'is_fragment': False, 'velocity': imp.impact_velocity_m_s})
    
    fragment_geo = []
    if show_progress:
        fragments_iter = smart_tqdm(fragments, desc="Converting fragments", leave=False)
    else:
        fragments_iter = fragments
    for imp in fragments_iter:
        pt = meters_to_latlon(launch_lat, launch_lon, abs_azimuth, imp.downrange_m, imp.crossrange_m)
        fragment_geo.append({'lat': pt.lat, 'lon': pt.lon, 'is_fragment': True, 'fragment_id': imp.fragment_id})
    
    return primary_geo, fragment_geo, elapsed


def benchmark_gpu_vs_cpu(iterations: int = 500) -> dict:
    """Run benchmark comparing GPU vs CPU performance."""
    print("\n" + "="*60)
    print("GPU vs CPU BENCHMARK")
    print("="*60)
    
    results = {}
    
    # GPU/Parallel run
    print("\n[1/2] GPU/Parallel mode:")
    _, _, gpu_time = run_simulation_gpu(iterations, show_progress=True)
    results['gpu_time'] = gpu_time
    results['gpu_throughput'] = iterations / gpu_time
    
    # Standard CPU run  
    print("\n[2/2] Standard CPU mode:")
    _, _, cpu_time = run_simulation_standard(iterations, show_progress=True)
    results['cpu_time'] = cpu_time
    results['cpu_throughput'] = iterations / cpu_time
    
    # Analysis
    speedup = cpu_time / gpu_time if gpu_time > 0 else 0
    results['speedup'] = speedup
    
    print("\n" + "-"*40)
    print("BENCHMARK RESULTS")
    print("-"*40)
    print(f"  Iterations:       {iterations}")
    print(f"  GPU/Parallel:     {gpu_time:.2f}s ({results['gpu_throughput']:.1f} traj/sec)")
    print(f"  Standard CPU:     {cpu_time:.2f}s ({results['cpu_throughput']:.1f} traj/sec)")
    print(f"  Speedup:          {speedup:.2f}x")
    print("-"*40)
    
    return results


def compute_ellipse_from_geo(points: list, confidence: float = 0.997) -> dict:
    """Compute ellipse from geo points."""
    arr = np.array([[p['lat'], p['lon']] for p in points])
    return compute_dispersion_ellipse(arr, confidence)


def run_pipeline(
    iterations: int = 1000,
    output_dir: str = "output",
    use_gpu: bool = True,
    satellite_date: str = "2023-07-15",
    create_visualization: bool = True,
    run_benchmark: bool = False,
    calculate_otu: bool = False,
    otu_date: str = "2024-09-09",
) -> dict:
    """Run complete pipeline with visualization and optional benchmark."""
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*60)
    print("BALLISTIC SIMULATION PIPELINE")
    print("="*60)
    
    # Optional benchmark
    benchmark_results = None
    if run_benchmark:
        benchmark_results = benchmark_gpu_vs_cpu(iterations)
    
    # Run simulation
    print("\n[Step 1/6] Running Monte Carlo simulation...")
    if use_gpu:
        primary_geo, fragment_geo, sim_time = run_simulation_gpu(iterations)
    else:
        primary_geo, fragment_geo, sim_time = run_simulation_standard(iterations)
    
    # Compute ellipses
    print("\n[Step 2/6] Computing dispersion ellipses...")
    primary_ellipse = compute_ellipse_from_geo(primary_geo)
    fragment_ellipse = compute_ellipse_from_geo(fragment_geo) if fragment_geo else None
    
    print(f"\n  PRIMARY ELLIPSE:")
    print(f"    Center: ({primary_ellipse['center_lat']:.4f} deg N, {primary_ellipse['center_lon']:.4f} deg E)")
    print(f"    Size:   {primary_ellipse['semi_major_km']:.1f} x {primary_ellipse['semi_minor_km']:.1f} km")
    print(f"    Angle:  {primary_ellipse['angle_deg']:.1f} deg from North")
    
    if fragment_ellipse:
        print(f"\n  FRAGMENT ELLIPSE:")
        print(f"    Center: ({fragment_ellipse['center_lat']:.4f} deg N, {fragment_ellipse['center_lon']:.4f} deg E)")
        print(f"    Size:   {fragment_ellipse['semi_major_km']:.1f} x {fragment_ellipse['semi_minor_km']:.1f} km")
        print(f"    Angle:  {fragment_ellipse['angle_deg']:.1f} deg from North")
    
    # Generate grid INSIDE ellipse polygons
    print("\n[Step 3/6] Generating analysis grid inside ellipse polygons...")
    from grid.polygon_grid import create_ellipse_polygon, generate_grid_in_polygons
    
    # Create ellipse polygons at full size
    polygons = []
    if primary_ellipse:
        primary_polygon = create_ellipse_polygon(primary_ellipse, scale=1.0)
        polygons.append(primary_polygon)
    if fragment_ellipse:
        fragment_polygon = create_ellipse_polygon(fragment_ellipse, scale=1.0)
        polygons.append(fragment_polygon)
    
    # Generate grid cells inside polygons
    grid = generate_grid_in_polygons(polygons, cell_size_km=1.0)
    print(f"  Generated {len(grid)} grid cells (1x1 km) inside ellipse polygons")
    
    # Save GeoJSON
    print("\n[Step 4/6] Saving GeoJSON files...")
    _save_geojson(primary_geo, os.path.join(output_dir, "impact_points_primary.geojson"))
    if fragment_geo:
        _save_geojson(fragment_geo, os.path.join(output_dir, "impact_points_fragments.geojson"))
    _save_ellipse_geojson(primary_ellipse, os.path.join(output_dir, "ellipse_primary.geojson"), "primary")
    if fragment_ellipse:
        _save_ellipse_geojson(fragment_ellipse, os.path.join(output_dir, "ellipse_fragments.geojson"), "fragment")
    
    # Create visualization
    if create_visualization:
        print(f"\n[Step 5/6] Creating visualization (satellite date: {satellite_date})...")
        try:
            from visualization.satellite_overlay import create_impact_visualization
            
            all_points = primary_geo + fragment_geo
            # Use fragment ellipse center if available, otherwise primary
            center_ellipse = fragment_ellipse if fragment_ellipse else primary_ellipse
            
            viz_path = create_impact_visualization(
                center_lat=center_ellipse['center_lat'],
                center_lon=center_ellipse['center_lon'],
                primary_ellipse=primary_ellipse,
                fragment_ellipse=fragment_ellipse,
                impact_points=all_points,
                grid_cells=grid,
                output_path=os.path.join(output_dir, "impact_visualization.html"),
                satellite_date=satellite_date,
            )
            print(f"  Saved: {viz_path}")
        except Exception as e:
            print(f"  Visualization failed: {e}")
    else:
        print("\n[Step 5/7] Skipping visualization (--no-viz)")
    
    # OTU Calculation
    otu_results = None
    if calculate_otu:
        print(f"\n[Step 6/7] Calculating OTU ecological index (date: {otu_date})...")
        try:
            from otu.calculator import calculate_otu_for_grid
            otu_results = calculate_otu_for_grid(
                grid_cells=grid,
                target_date=otu_date,
                output_dir=os.path.join(output_dir, "otu"),
                cache_dir=os.path.join(output_dir, "otu_cache"),
                show_progress=True,
            )
            print(f"  OTU Mean: {otu_results['statistics']['mean']:.3f}")
            print(f"  OTU Saved: {otu_results['output_path']}")
        except Exception as e:
            print(f"  OTU calculation failed: {e}")
    else:
        print("\n[Step 6/7] Skipping OTU calculation (use --otu to enable)")
    
    # Summary
    print("\n[Step 7/7] Saving summary...")
    summary = {
        "iterations": iterations,
        "simulation_time_s": sim_time,
        "primary_impacts": len(primary_geo),
        "fragment_impacts": len(fragment_geo),
        "primary_ellipse": primary_ellipse,
        "fragment_ellipse": fragment_ellipse,
        "grid_cells": len(grid),
        "satellite_date": satellite_date,
        "benchmark": benchmark_results,
        "otu": otu_results,
    }
    
    with open(os.path.join(output_dir, "simulation_summary.json"), "w") as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "="*60)
    print("PIPELINE COMPLETE")
    print("="*60)
    print(f"  Simulation time: {sim_time:.2f}s")
    print(f"  Primary ellipse: {primary_ellipse['semi_major_km']:.1f} x {primary_ellipse['semi_minor_km']:.1f} km @ {primary_ellipse['angle_deg']:.0f} deg")
    if fragment_ellipse:
        print(f"  Fragment ellipse: {fragment_ellipse['semi_major_km']:.1f} x {fragment_ellipse['semi_minor_km']:.1f} km @ {fragment_ellipse['angle_deg']:.0f} deg")
    print(f"  Output: {output_dir}/")
    
    return summary


def _save_geojson(points: list, path: str) -> None:
    features = [{"type": "Feature", "properties": p, "geometry": {"type": "Point", "coordinates": [p['lon'], p['lat']]}} for p in points]
    with open(path, "w") as f:
        json.dump({"type": "FeatureCollection", "features": features}, f)
    print(f"    {path}")


def _save_ellipse_geojson(ellipse: dict, path: str, etype: str, scale: float = 1.0) -> None:
    """Save ellipse as GeoJSON polygon with optional scaling."""
    import math
    center_lat, center_lon = ellipse["center_lat"], ellipse["center_lon"]
    a_km, b_km = ellipse["semi_major_km"] * scale, ellipse["semi_minor_km"] * scale
    angle_deg = ellipse.get("angle_deg", 0)
    
    # Convert km to degrees
    lat_rad = math.radians(center_lat)
    deg_per_km_lat = 1 / 111.0
    deg_per_km_lon = 1 / (111.0 * math.cos(lat_rad))
    
    a_lat = a_km * deg_per_km_lat
    a_lon = a_km * deg_per_km_lon
    b_lat = b_km * deg_per_km_lat
    b_lon = b_km * deg_per_km_lon
    
    # Angle from North (geographic) to math angle (from East, CCW)
    math_angle = math.radians(90 - angle_deg)
    
    coords = []
    for t in np.linspace(0, 2*np.pi, 64):
        # Ellipse in local frame
        x = a_lon * np.cos(t)
        y = a_lat * np.sin(t) * (b_km / a_km) if a_km > 0 else 0
        
        # Rotate
        x_rot = x * np.cos(math_angle) - y * np.sin(math_angle)
        y_rot = x * np.sin(math_angle) + y * np.cos(math_angle)
        
        coords.append([center_lon + x_rot, center_lat + y_rot])
    coords.append(coords[0])
    
    # Store both original and scaled sizes in properties
    props = {
        "type": etype,
        "original_semi_major_km": ellipse["semi_major_km"],
        "original_semi_minor_km": ellipse["semi_minor_km"],
        "scaled_semi_major_km": a_km,
        "scaled_semi_minor_km": b_km,
        "scale_factor": scale,
        "center_lat": center_lat,
        "center_lon": center_lon,
        "angle_deg": angle_deg,
    }
    
    geojson = {"type": "FeatureCollection", "features": [{"type": "Feature", "properties": props, "geometry": {"type": "Polygon", "coordinates": [coords]}}]}
    with open(path, "w") as f:
        json.dump(geojson, f)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Ballistic simulation with GPU and visualization")
    parser.add_argument("-n", "--iterations", type=int, default=1000)
    parser.add_argument("-o", "--output", type=str, default="output")
    parser.add_argument("--no-gpu", action="store_true", help="Disable GPU acceleration")
    parser.add_argument("--no-viz", action="store_true", help="Skip visualization")
    parser.add_argument("--date", type=str, default="2023-07-15", help="Satellite image date")
    parser.add_argument("--benchmark", action="store_true", help="Run GPU vs CPU benchmark")
    parser.add_argument("--otu", action="store_true", help="Calculate OTU ecological index")
    parser.add_argument("--otu-date", type=str, default="2024-09-09", help="Target date for OTU NDVI (YYYY-MM-DD)")
    args = parser.parse_args()
    
    run_pipeline(
        iterations=args.iterations,
        output_dir=args.output,
        use_gpu=not args.no_gpu,
        satellite_date=args.date,
        create_visualization=not args.no_viz,
        run_benchmark=args.benchmark,
        calculate_otu=args.otu,
        otu_date=args.otu_date,
    )
