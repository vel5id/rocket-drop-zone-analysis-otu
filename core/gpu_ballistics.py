"""GPU-accelerated ballistic trajectory calculations using Numba CUDA."""
from __future__ import annotations

import math
import numpy as np

try:
    from numba import cuda, jit, prange
    HAS_CUDA = cuda.is_available()
    HAS_NUMBA = True
except ImportError:
    HAS_CUDA = False
    HAS_NUMBA = False

# Physical constants
EARTH_RADIUS_M = 6_371_000.0
STANDARD_GRAVITY = 9.80665
GAMMA_AIR = 1.4
R_AIR = 287.05


def check_gpu_available() -> bool:
    """Check if CUDA GPU is available."""
    return HAS_CUDA


if HAS_NUMBA:
    @jit(nopython=True, parallel=True, fastmath=True)
    def propagate_batch_cpu(
        initial_states: np.ndarray,
        params: np.ndarray,
        dt: float,
        max_steps: int,
        reference_area: float,
        base_mass: float,
    ) -> np.ndarray:
        """
        CPU-parallel batch trajectory propagation using Numba.
        
        Args:
            initial_states: (N, 6) array [dr, cr, alt, vel, gamma, psi]
            params: (N, 5) array [density_factor, wind_u, wind_v, mass, cd]
            dt: time step
            max_steps: maximum integration steps
            reference_area: rocket cross-section area
            base_mass: base dry mass
        
        Returns:
            (N, 6) array of final impact states
        """
        n_trajectories = initial_states.shape[0]
        results = np.zeros((n_trajectories, 6), dtype=np.float64)
        
        for i in prange(n_trajectories):
            # Initial state
            dr = initial_states[i, 0]
            cr = initial_states[i, 1]
            alt = initial_states[i, 2]
            vel = initial_states[i, 3]
            gamma = initial_states[i, 4]
            psi = initial_states[i, 5]
            
            # Parameters
            density_factor = params[i, 0]
            wind_u = params[i, 1]
            wind_v = params[i, 2]
            mass = params[i, 3]
            cd = params[i, 4]
            
            # Propagate until ground impact
            for step in range(max_steps):
                if alt <= 0:
                    break
                
                # Atmosphere (exponential model)
                rho0 = 1.225
                H = 8500.0
                rho = rho0 * math.exp(-alt / H) * density_factor
                
                # Temperature and speed of sound
                T = max(288.15 - 0.0065 * min(alt, 11000), 216.65)
                a = math.sqrt(GAMMA_AIR * R_AIR * T)
                mach = vel / a
                
                # Drag coefficient (Mach-dependent approximation)
                if mach < 0.8:
                    cd_actual = 0.5 * cd
                elif mach < 1.2:
                    cd_actual = (0.5 + (1.1 - 0.5) * (mach - 0.8) / 0.4) * cd
                else:
                    cd_actual = max(0.6, 1.1 - 0.1 * (mach - 1.2)) * cd
                
                # Dynamic pressure and drag
                v_rel = math.sqrt((vel * math.cos(gamma) - wind_u)**2 + 
                                  wind_v**2 + 
                                  (vel * math.sin(gamma))**2)
                q = 0.5 * rho * v_rel * v_rel
                drag_acc = q * cd_actual * reference_area / max(mass, 1.0)
                
                # Gravity
                gravity = STANDARD_GRAVITY * (EARTH_RADIUS_M / (EARTH_RADIUS_M + alt))**2
                
                # Derivatives (RK4 simplified to Euler for GPU efficiency)
                dr_dot = vel * math.cos(gamma) * math.cos(psi)
                cr_dot = vel * math.cos(gamma) * math.sin(psi) - wind_v
                alt_dot = vel * math.sin(gamma)
                vel_dot = -gravity * math.sin(gamma) - drag_acc
                gamma_dot = -gravity * math.cos(gamma) / max(vel, 1.0)
                psi_dot = 0.0  # Simplified
                
                # Update state
                dr += dr_dot * dt
                cr += cr_dot * dt
                alt += alt_dot * dt
                vel += vel_dot * dt
                gamma += gamma_dot * dt
                psi += psi_dot * dt
            
            # Store results
            results[i, 0] = dr
            results[i, 1] = cr
            results[i, 2] = alt
            results[i, 3] = vel
            results[i, 4] = gamma
            results[i, 5] = psi
        
        return results


if HAS_CUDA:
    @cuda.jit
    def _propagate_kernel(
        initial_states,
        params,
        results,
        dt,
        max_steps,
        reference_area,
    ):
        """CUDA kernel for GPU-parallel trajectory propagation."""
        i = cuda.grid(1)
        if i >= initial_states.shape[0]:
            return
        
        # Initial state
        dr = initial_states[i, 0]
        cr = initial_states[i, 1]
        alt = initial_states[i, 2]
        vel = initial_states[i, 3]
        gamma = initial_states[i, 4]
        psi = initial_states[i, 5]
        
        # Parameters
        density_factor = params[i, 0]
        wind_u = params[i, 1]
        wind_v = params[i, 2]
        mass = params[i, 3]
        cd = params[i, 4]
        
        rho0 = 1.225
        H = 8500.0
        
        for step in range(max_steps):
            if alt <= 0:
                break
            
            # Atmosphere
            rho = rho0 * math.exp(-alt / H) * density_factor
            T = max(288.15 - 0.0065 * min(alt, 11000.0), 216.65)
            a = math.sqrt(1.4 * 287.05 * T)
            mach = vel / a
            
            # Drag coefficient
            if mach < 0.8:
                cd_actual = 0.5 * cd
            elif mach < 1.2:
                cd_actual = (0.5 + 0.6 * (mach - 0.8) / 0.4) * cd
            else:
                cd_actual = max(0.6, 1.1 - 0.1 * (mach - 1.2)) * cd
            
            # Drag
            v_rel_sq = (vel * math.cos(gamma) - wind_u)**2 + wind_v**2 + (vel * math.sin(gamma))**2
            q = 0.5 * rho * v_rel_sq
            drag_acc = q * cd_actual * reference_area / max(mass, 1.0)
            
            # Gravity
            gravity = 9.80665 * (6371000.0 / (6371000.0 + alt))**2
            
            # Update
            dr += vel * math.cos(gamma) * math.cos(psi) * dt
            cr += (vel * math.cos(gamma) * math.sin(psi) - wind_v) * dt
            alt += vel * math.sin(gamma) * dt
            vel += (-gravity * math.sin(gamma) - drag_acc) * dt
            gamma += (-gravity * math.cos(gamma) / max(vel, 1.0)) * dt
        
        results[i, 0] = dr
        results[i, 1] = cr
        results[i, 2] = alt
        results[i, 3] = vel
        results[i, 4] = gamma
        results[i, 5] = psi
    
    
    def propagate_batch_gpu(
        initial_states: np.ndarray,
        params: np.ndarray,
        dt: float = 0.5,
        max_steps: int = 1200,
        reference_area: float = 43.0,
    ) -> np.ndarray:
        """GPU-accelerated batch trajectory propagation."""
        n = initial_states.shape[0]
        results = np.zeros((n, 6), dtype=np.float64)
        
        # Transfer to GPU
        d_states = cuda.to_device(initial_states)
        d_params = cuda.to_device(params)
        d_results = cuda.to_device(results)
        
        # Launch kernel
        threads_per_block = 256
        blocks = (n + threads_per_block - 1) // threads_per_block
        
        _propagate_kernel[blocks, threads_per_block](
            d_states, d_params, d_results, dt, max_steps, reference_area
        )
        
        # Copy back
        return d_results.copy_to_host()


def propagate_batch(
    initial_states: np.ndarray,
    params: np.ndarray,
    dt: float = 0.5,
    max_steps: int = 1200,
    reference_area: float = 43.0,
    base_mass: float = 30600.0,
    use_gpu: bool = True,
) -> np.ndarray:
    """
    Batch trajectory propagation with automatic GPU/CPU selection.
    
    Args:
        initial_states: (N, 6) initial state vectors
        params: (N, 5) parameter vectors
        dt: time step in seconds
        max_steps: maximum integration steps
        reference_area: cross-section area in m²
        base_mass: base dry mass in kg
        use_gpu: prefer GPU if available
    
    Returns:
        (N, 6) final impact states
    """
    if use_gpu and HAS_CUDA:
        print(f"  Using GPU acceleration ({cuda.get_current_device().name})")
        return propagate_batch_gpu(initial_states, params, dt, max_steps, reference_area)
    elif HAS_NUMBA:
        import os
        n_threads = os.cpu_count() or 4
        print(f"  Using CPU parallel ({n_threads} threads)")
        return propagate_batch_cpu(initial_states, params, dt, max_steps, reference_area, base_mass)
    else:
        raise RuntimeError("Neither CUDA nor Numba available. Install numba: pip install numba")
