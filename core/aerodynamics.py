"""Aerodynamic coefficients for the Proton first stage."""
from __future__ import annotations

def proton_drag_coefficient(mach: float) -> float:
    """
    Approximated drag coefficient (Cd) vs Mach number for a blunt cylinder-like body
    (Proton first stage with side boosters).
    
    Based on general ballistic data for launch vehicle stages:
    - Subsonic (M < 0.8): ~0.4 - 0.5
    - Transonic (0.8 < M < 1.2): Sharp rise to peak ~0.9 - 1.2
    - Supersonic (M > 1.2): Gradual decay
    """
    abs_mach = abs(mach)
    
    if abs_mach < 0.8:
        # Subsonic plateau
        return 0.5
    elif 0.8 <= abs_mach < 1.2:
        # Transonic rise (linear approximation for simplicity)
        # M=0.8 -> 0.5
        # M=1.2 -> 1.1
        return 0.5 + (1.1 - 0.5) * (abs_mach - 0.8) / (1.2 - 0.8)
    elif 1.2 <= abs_mach < 5.0:
        # Supersonic decay
        # M=1.2 -> 1.1
        # M=5.0 -> 0.6
        return 1.1 - (1.1 - 0.6) * (abs_mach - 1.2) / (5.0 - 1.2)
    else:
        # Hypersonic plateau
        return 0.6
