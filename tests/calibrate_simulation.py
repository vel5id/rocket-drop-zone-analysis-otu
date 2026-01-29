"""
Monte Carlo Calibration Script v2.0

This script calibrates simulation parameters so that impact points
fall within the target zone polygons (Zone 15 and Zone 25 from shapefiles).

IMPROVED: Now focuses on CENTER TARGETING first, then size adjustment.
"""
from __future__ import annotations

import sys
import numpy as np
from pathlib import Path
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent))

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

# Import simulation components
from tests.run_pipeline import run_simulation_gpu, run_simulation_standard
from grid.shapefile_loader import load_yu24_zones, polygon_to_ellipse_approx
from config.rocket_params import PROTON_STAGE_ONE, PROTON_SEPARATION


@dataclass
class CalibrationParams:
    """Parameters to calibrate"""
    # Mean values (determine CENTER of impact zone)
    h_mean: float = 43_000.0      # Mean separation altitude (m)
    v_mean: float = 1_738.0       # Mean separation velocity (m/s)
    gamma_mean: float = 25.0      # Mean flight path angle (deg)
    psi_mean: float = 45.0        # Mean azimuth (deg)
    
    # Standard deviations (determine SIZE of impact zone)
    h_std: float = 500.0          # σ altitude (m) - REDUCED for smaller zones
    v_std: float = 30.0           # σ velocity (m/s) - REDUCED
    gamma_std: float = 1.0        # σ flight path angle (deg) - REDUCED
    psi_std: float = 1.0          # σ azimuth (deg) - REDUCED
    
    # Wind
    wind_u_std: float = 10.0      # σ along-track wind (m/s) - REDUCED
    wind_v_std: float = 10.0      # σ cross-track wind (m/s) - REDUCED


def get_zone_center(zone_coords: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Get center coordinates of a zone."""
    lats = [p[0] for p in zone_coords]
    lons = [p[1] for p in zone_coords]
    return np.mean(lats), np.mean(lons)


def run_single_simulation(params: CalibrationParams, n_iter: int = 100) -> List[Dict]:
    """Run simulation with given params and return impact points."""
    import config.simulation_config as sim_cfg
    
    # Apply calibration params
    sim_cfg.DEFAULT_PERTURBATIONS["initial_altitude"] = sim_cfg.Perturbation(
        "normal", (params.h_mean, params.h_std)
    )
    sim_cfg.DEFAULT_PERTURBATIONS["initial_velocity"] = sim_cfg.Perturbation(
        "normal", (params.v_mean, params.v_std)
    )
    sim_cfg.DEFAULT_PERTURBATIONS["flight_path_angle"] = sim_cfg.Perturbation(
        "normal", (params.gamma_mean, params.gamma_std)
    )
    sim_cfg.DEFAULT_PERTURBATIONS["azimuth"] = sim_cfg.Perturbation(
        "normal", (params.psi_mean, params.psi_std)
    )
    sim_cfg.DEFAULT_PERTURBATIONS["wind_u"] = sim_cfg.Perturbation(
        "normal", (0.0, params.wind_u_std)
    )
    sim_cfg.DEFAULT_PERTURBATIONS["wind_v"] = sim_cfg.Perturbation(
        "normal", (0.0, params.wind_v_std)
    )
    
    primary_geo, fragment_geo, _ = run_simulation_gpu(n_iter, show_progress=False)
    
    all_points = []
    for pt in primary_geo:
        all_points.append({"lat": pt["lat"], "lon": pt["lon"], "type": "primary"})
    if fragment_geo:
        for pt in fragment_geo:
            all_points.append({"lat": pt["lat"], "lon": pt["lon"], "type": "fragment"})
    
    return all_points


def get_impact_center(points: List[Dict]) -> Tuple[float, float]:
    """Get center of impact points."""
    lats = [p["lat"] for p in points]
    lons = [p["lon"] for p in points]
    return np.mean(lats), np.mean(lons)


def center_distance_km(center1: Tuple[float, float], center2: Tuple[float, float]) -> float:
    """Distance between two centers in km."""
    lat1, lon1 = center1
    lat2, lon2 = center2
    dlat = (lat2 - lat1) * 111.0
    dlon = (lon2 - lon1) * 111.0 * np.cos(np.radians((lat1 + lat2) / 2))
    return np.sqrt(dlat**2 + dlon**2)


def calculate_containment(points: List[Dict], polygon: Polygon) -> float:
    """Calculate fraction of points inside polygon."""
    inside = 0
    for pt in points:
        if polygon.contains(Point(pt["lon"], pt["lat"])):
            inside += 1
    return inside / len(points) if points else 0


def calibrate_center_first(
    target_center: Tuple[float, float],
    target_polygon: Polygon,
    initial_params: CalibrationParams,
    n_iterations: int = 100,
    max_steps: int = 20,
) -> CalibrationParams:
    """
    Calibrate by first moving the CENTER to target, then adjusting size.
    
    Uses gradient-descent-like approach to move impact center toward target.
    """
    print("\n" + "="*60)
    print("PHASE 1: CENTER TARGETING")
    print("="*60)
    print(f"  Target center: {target_center[0]:.4f}°N, {target_center[1]:.4f}°E")
    
    current_params = CalibrationParams(**initial_params.__dict__)
    
    # Initial simulation to find current center
    points = run_single_simulation(current_params, n_iterations)
    current_center = get_impact_center(points)
    initial_distance = center_distance_km(current_center, target_center)
    
    print(f"  Initial impact center: {current_center[0]:.4f}°N, {current_center[1]:.4f}°E")
    print(f"  Distance to target: {initial_distance:.1f} km")
    
    # Parameters that affect center position and their sensitivities
    # These are approximate gradients: change in lat/lon per unit change in param
    center_params = [
        ("gamma_mean", 0.02, 0.005),   # (param_name, dlat_per_unit, dlon_per_unit)
        ("psi_mean", 0.005, 0.02),
        ("v_mean", 0.0001, 0.00005),
        ("h_mean", 0.00001, 0.000005),
    ]
    
    learning_rate = 0.5
    best_distance = initial_distance
    best_params = CalibrationParams(**current_params.__dict__)
    
    for step in range(max_steps):
        # Calculate error
        lat_error = target_center[0] - current_center[0]
        lon_error = target_center[1] - current_center[1]
        
        if abs(lat_error) < 0.05 and abs(lon_error) < 0.05:
            print(f"  Step {step}: Center converged! Distance: {best_distance:.1f} km")
            break
        
        # Adjust parameters based on error
        for param_name, lat_sens, lon_sens in center_params:
            current_val = getattr(current_params, param_name)
            
            # Gradient step
            adjustment = lat_error * lat_sens + lon_error * lon_sens
            adjustment *= learning_rate * 10  # Scale factor
            
            # Apply limits
            if param_name == "gamma_mean":
                new_val = np.clip(current_val + adjustment * 5, 10, 45)
            elif param_name == "psi_mean":
                new_val = np.clip(current_val + adjustment * 10, 0, 90)
            elif param_name == "v_mean":
                new_val = np.clip(current_val + adjustment * 100, 1400, 2200)
            elif param_name == "h_mean":
                new_val = np.clip(current_val + adjustment * 1000, 30000, 60000)
            else:
                new_val = current_val
            
            setattr(current_params, param_name, new_val)
        
        # Re-simulate
        points = run_single_simulation(current_params, n_iterations)
        current_center = get_impact_center(points)
        distance = center_distance_km(current_center, target_center)
        
        print(f"  Step {step+1}: Center at {current_center[0]:.3f}°N, {current_center[1]:.3f}°E | Distance: {distance:.1f} km")
        
        if distance < best_distance:
            best_distance = distance
            best_params = CalibrationParams(**current_params.__dict__)
            learning_rate *= 0.9  # Decay
        else:
            learning_rate *= 0.7  # Faster decay if not improving
    
    print(f"\n  Final distance to target: {best_distance:.1f} km")
    return best_params


def calibrate_size(
    target_polygon: Polygon,
    centered_params: CalibrationParams,
    n_iterations: int = 100,
    max_steps: int = 15,
) -> CalibrationParams:
    """
    After centering, adjust σ parameters to match zone size.
    """
    print("\n" + "="*60)
    print("PHASE 2: SIZE CALIBRATION")
    print("="*60)
    
    # Calculate target zone dimensions
    bounds = target_polygon.bounds  # (minx, miny, maxx, maxy) = (min_lon, min_lat, max_lon, max_lat)
    target_width_km = (bounds[2] - bounds[0]) * 111 * np.cos(np.radians((bounds[1] + bounds[3]) / 2))
    target_height_km = (bounds[3] - bounds[1]) * 111
    print(f"  Target zone size: ~{target_width_km:.0f} × {target_height_km:.0f} km")
    
    current_params = CalibrationParams(**centered_params.__dict__)
    best_containment = 0
    best_params = current_params
    
    # Start with small dispersions and increase if needed
    sigma_scale = 0.3
    
    for step in range(max_steps):
        # Adjust sigma parameters
        current_params.h_std = 500 + step * 200
        current_params.v_std = 20 + step * 15
        current_params.gamma_std = 0.5 + step * 0.3
        current_params.psi_std = 0.5 + step * 0.3
        current_params.wind_u_std = 5 + step * 5
        current_params.wind_v_std = 5 + step * 5
        
        points = run_single_simulation(current_params, n_iterations)
        containment = calculate_containment(points, target_polygon)
        
        # Calculate actual dispersion
        lats = [p["lat"] for p in points]
        lons = [p["lon"] for p in points]
        center_lat = np.mean(lats)
        actual_width = (max(lons) - min(lons)) * 111 * np.cos(np.radians(center_lat))
        actual_height = (max(lats) - min(lats)) * 111
        
        print(f"  Step {step+1}: Size ~{actual_width:.0f}×{actual_height:.0f} km | Containment: {containment:.1%}")
        
        if containment > best_containment:
            best_containment = containment
            best_params = CalibrationParams(**current_params.__dict__)
        
        # Stop if containment starts dropping after peak
        if containment < best_containment * 0.7 and best_containment > 0.1:
            print(f"  Containment dropping, stopping at best: {best_containment:.1%}")
            break
    
    return best_params


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Calibrate Monte Carlo simulation to target zones (v2.0)")
    parser.add_argument("--zone", type=str, default="15", choices=["15", "25", "both"],
                        help="Target zone to calibrate for")
    parser.add_argument("--iterations", "-n", type=int, default=100,
                        help="Monte Carlo iterations per evaluation")
    parser.add_argument("--center-steps", type=int, default=15,
                        help="Max steps for center calibration")
    parser.add_argument("--size-steps", type=int, default=10,
                        help="Max steps for size calibration")
    args = parser.parse_args()
    
    # Load target zones
    print("Loading target zone polygons...")
    zone_15_coords, zone_25_coords = load_yu24_zones(str(Path(__file__).parent))
    
    if not zone_15_coords or not zone_25_coords:
        print("[ERROR] Could not load zone shapefiles")
        return
    
    # Select target
    if args.zone == "15":
        target_coords = zone_15_coords
        target_polygon = Polygon([(lon, lat) for lat, lon in zone_15_coords])
        zone_name = "Zone 15"
    elif args.zone == "25":
        target_coords = zone_25_coords
        target_polygon = Polygon([(lon, lat) for lat, lon in zone_25_coords])
        zone_name = "Zone 25"
    else:
        # Both zones - use larger one (25) for now
        target_coords = zone_25_coords
        p25 = Polygon([(lon, lat) for lat, lon in zone_25_coords])
        target_polygon = p25
        zone_name = "Zone 25 (larger)"
    
    target_center = get_zone_center(target_coords)
    print(f"\nTarget: {zone_name}")
    print(f"  Center: {target_center[0]:.4f}°N, {target_center[1]:.4f}°E")
    print(f"  Area: {target_polygon.area * 111**2:.0f} km²")
    
    # Initial params with reduced dispersion
    initial = CalibrationParams()
    
    # Phase 1: Center targeting
    centered_params = calibrate_center_first(
        target_center=target_center,
        target_polygon=target_polygon,
        initial_params=initial,
        n_iterations=args.iterations,
        max_steps=args.center_steps,
    )
    
    # Phase 2: Size calibration
    final_params = calibrate_size(
        target_polygon=target_polygon,
        centered_params=centered_params,
        n_iterations=args.iterations,
        max_steps=args.size_steps,
    )
    
    # Final evaluation
    print("\n" + "="*60)
    print("FINAL EVALUATION")
    print("="*60)
    
    points = run_single_simulation(final_params, args.iterations * 2)
    containment = calculate_containment(points, target_polygon)
    center = get_impact_center(points)
    distance = center_distance_km(center, target_center)
    
    print(f"  Impact center: {center[0]:.4f}°N, {center[1]:.4f}°E")
    print(f"  Distance to target: {distance:.1f} km")
    print(f"  Containment: {containment:.1%}")
    
    # Print calibrated config
    p = final_params
    print("\n" + "="*60)
    print("CALIBRATED PARAMETERS")
    print("="*60)
    print(f"""
Copy this to config/simulation_config.py:

DEFAULT_PERTURBATIONS = {{
    "initial_velocity": Perturbation("normal", ({p.v_mean:.1f}, {p.v_std:.1f})),
    "initial_altitude": Perturbation("normal", ({p.h_mean:.1f}, {p.h_std:.1f})),
    "flight_path_angle": Perturbation("normal", ({p.gamma_mean:.1f}, {p.gamma_std:.1f})),
    "azimuth": Perturbation("normal", ({p.psi_mean:.1f}, {p.psi_std:.1f})),
    "drag_coefficient": Perturbation("uniform", (0.7, 1.5)),
    "air_density_factor": Perturbation("normal", (1.0, 0.12)),
    "wind_u": Perturbation("normal", (0.0, {p.wind_u_std:.1f})),
    "wind_v": Perturbation("normal", (0.0, {p.wind_v_std:.1f})),
    "initial_mass": Perturbation("normal", (30600.0, 500.0)),
}}
""")


if __name__ == "__main__":
    main()
