from config.simulation_config import build_default_config, SimulationConfig, Perturbation
from core.ballistics import BallisticModel
from core.aerodynamics import proton_drag_coefficient
from core.trajectory import propagate_trajectory
from core.geo_utils import meters_to_latlon
from api.models import SimulationRequest, TrajectoryResponse, TrajectoryPoint
import math

def calculate_trajectory_preview(request: SimulationRequest) -> TrajectoryResponse:
    """
    Run a deterministic simulation (sigma=0) to generate a preview trajectory.
    """
    # 1. Build Config with NO perturbations
    config = build_default_config()
    
    # Set nominal values (user inputs)
    config.altitude_mean = request.sep_altitude
    config.velocity_mean = request.sep_velocity
    config.flight_path_angle_mean = request.sep_fp_angle
    config.azimuth_mean = 0.0 
    
    # Overwrite perturbations to be zero/deterministic
    new_perturbations = {}
    for key, pert in config.perturbations.items():
        # Create NEW Perturbation instance since it is frozen
        # Set sigma/variation to 0.0
        new_perturbations[key] = Perturbation(
            distribution="normal",
            args=(pert.args[0], 0.0)
        )
    config.perturbations = new_perturbations

    # 2. Initial State (Deterministic)
    # Separation point
    sep_alt = request.sep_altitude
    sep_vel = request.sep_velocity
    sep_gamma = math.radians(request.sep_fp_angle)
    
    # Azimuth: Launch Azimuth + Separation Relative Azimuth
    total_azimuth_deg = request.azimuth + request.sep_azimuth
    # In ballistic frame, downrange is X, crossrange is Y.
    # We simulate in frame aligned with total_azimuth for simplicity of 2D, 
    # OR we use 3D with correct Heading.
    # The BallisticModel uses 'psi' (heading) relative to "downrange" axis? 
    # Usually MonteCarlo sets psi=0 as "nominal" relative to launch azimuth.
    # Let's check monte_carlo.py: psi_rad = np.radians(azimuth_deg - 45.0) ???
    # Wait, the MonteCarlo _initial_state sets psi based on sampled azimuth perturbation.
    # For preview, we want the nominal path.
    # Let's assume the ballistic propagation starts at downrange=0, crossrange=0.
    # We will map (dr, cr) to (lat, lon) using the launch_lat/lon and total_azimuth.
    
    state0 = [
        0.0, # downrange
        0.0, # crossrange
        sep_alt,
        sep_vel,
        sep_gamma,
        math.radians(0.0) # Heading relative to the nominal track (which is total_azimuth)
    ]
    
    # 3. Model
    model = BallisticModel(
        reference_area_m2=request.rocket_ref_area,
        dry_mass_kg=request.rocket_dry_mass,
        drag_coefficient_provider=proton_drag_coefficient,
    )
    
    # 4. Propagate
    # No wind for preview
    kwargs = {
        "density_factor": 1.0,
        "wind_u_m_s": 0.0,
        "wind_v_m_s": 0.0,
        "mass": request.rocket_dry_mass,
    }
    
    result = propagate_trajectory(
        model,
        state0,
        t_span=(0.0, 1000.0), # Enough max time
        max_step=1.0, # Coarse step is fine for preview
        model_kwargs=kwargs
    )
    
    # 5. Convert to Geo
    path_points = []
    
    # Decimate points to reduce payload (e.g., every 5th point)
    # The solver returns variable steps, but max_step=1.0 ensures they aren't too far.
    # We just iterate all.
    
    times = result.time_s
    states = result.state # shape (6, N)
    
    for i in range(0, len(times), 2): # Take every 2nd point for speed
        t = times[i]
        dr = states[0, i]
        cr = states[1, i]
        alt = states[2, i]
        vel = states[3, i]
        
        geo = meters_to_latlon(request.launch_lat, request.launch_lon, total_azimuth_deg, dr, cr)
        
        path_points.append(TrajectoryPoint(
            lat=geo.lat,
            lon=geo.lon,
            alt=alt,
            velocity=vel,
            time=t
        ))
        
    # Ensure impact point is included if not covered
    impact_state = result.impact_state
    imp_geo = meters_to_latlon(request.launch_lat, request.launch_lon, total_azimuth_deg, impact_state[0], impact_state[1])
    impact_point = TrajectoryPoint(
        lat=imp_geo.lat,
        lon=imp_geo.lon,
        alt=impact_state[2], # Should be 0
        velocity=impact_state[3],
        time=times[-1]
    )
    
    # Append impact if not last
    if not path_points or (path_points[-1].time < impact_point.time):
        path_points.append(impact_point)
        
    return TrajectoryResponse(path=path_points, impact_point=impact_point)
