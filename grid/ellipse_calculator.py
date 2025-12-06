"""Helpers for computing statistical dispersion ellipses from point clouds."""
from __future__ import annotations

import numpy as np

try:
    from scipy.stats import chi2
except ImportError:
    chi2 = None


def _chi2_ppf(confidence: float) -> float:
    """Get chi-squared percentile point function for 2 DOF."""
    if chi2 is not None:
        return float(chi2.ppf(confidence, df=2))
    lookup = {
        0.950: 5.991,
        0.990: 9.210,
        0.997: 11.829,
        0.999: 13.816,
    }
    return lookup.get(round(confidence, 3), 11.829)


def compute_dispersion_ellipse(impact_points: np.ndarray, confidence: float = 0.997) -> dict[str, float]:
    """
    Compute dispersion ellipse from point cloud using PCA.
    
    The ellipse is computed by:
    1. Finding the center (mean) of the point cloud
    2. Computing covariance matrix
    3. Finding principal axes via eigendecomposition
    4. Scaling axes by chi-squared value for confidence level
    
    Args:
        impact_points: (N, 2) array of [lat, lon] coordinates
        confidence: Confidence level (default 0.997 = 3σ)
    
    Returns:
        Dictionary with center, axes (in km), and rotation angle
    """
    if impact_points.ndim != 2 or impact_points.shape[1] != 2:
        raise ValueError("impact_points must be shaped (N, 2)")
    
    n_points = len(impact_points)
    if n_points < 2:
        # Single point - return minimal ellipse
        return {
            "center_lat": float(impact_points[0, 0]),
            "center_lon": float(impact_points[0, 1]),
            "semi_major_km": 1.0,
            "semi_minor_km": 1.0,
            "angle_deg": 0.0,
        }

    # 1. Center is mean of all points
    center = np.mean(impact_points, axis=0)
    center_lat, center_lon = center
    
    # 2. Center the data
    centered = impact_points - center
    
    # 3. Covariance matrix
    cov = np.cov(centered.T)
    
    # Handle degenerate case
    if np.isscalar(cov) or cov.shape == ():
        cov = np.array([[float(cov), 0], [0, float(cov)]])
    
    # 4. Eigendecomposition - get principal axes
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    
    # Sort by eigenvalue (largest first = major axis)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = eigenvalues[order]
    eigenvectors = eigenvectors[:, order]
    
    # 5. Chi-squared scaling for confidence ellipse
    chi_val = _chi2_ppf(confidence)
    
    # Semi-axes in DEGREES (standard deviations scaled by chi-squared)
    semi_major_deg = np.sqrt(max(eigenvalues[0], 0) * chi_val)
    semi_minor_deg = np.sqrt(max(eigenvalues[1], 0) * chi_val)
    
    # 6. Convert degrees to kilometers
    # At this latitude (~47°N), adjust for Earth's curvature
    lat_rad = np.radians(center_lat)
    km_per_deg_lat = 111.0  # ~constant
    km_per_deg_lon = 111.0 * np.cos(lat_rad)  # varies with latitude
    
    # The eigenvectors give direction, we need to account for lat/lon scaling
    # For simplicity, use average conversion
    km_per_deg = (km_per_deg_lat + km_per_deg_lon) / 2
    
    semi_major_km = semi_major_deg * km_per_deg
    semi_minor_km = semi_minor_deg * km_per_deg
    
    # 7. Rotation angle from major eigenvector
    # eigenvectors[:, 0] is the major axis direction
    # In lat/lon space: [0] is lat (N-S), [1] is lon (E-W)
    # Angle is measured from East (positive lon), counter-clockwise
    major_vec = eigenvectors[:, 0]
    
    # Compute angle: atan2(lat_component, lon_component)
    # This gives angle from East axis
    # We want angle from North, so adjust
    angle_from_east = np.degrees(np.arctan2(major_vec[0], major_vec[1]))
    
    # Convert to angle from North (geographic convention: 0=N, 90=E)
    angle_from_north = 90.0 - angle_from_east
    
    # Normalize to [-180, 180]
    while angle_from_north > 180:
        angle_from_north -= 360
    while angle_from_north < -180:
        angle_from_north += 360

    return {
        "center_lat": float(center_lat),
        "center_lon": float(center_lon),
        "semi_major_km": float(semi_major_km),
        "semi_minor_km": float(semi_minor_km),
        "angle_deg": float(angle_from_north),
    }
