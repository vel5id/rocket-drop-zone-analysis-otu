"""Matplotlib-based ellipse visualization utilities."""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse


def plot_dispersion_ellipse(ax: plt.Axes, ellipse_params: dict[str, float], **style) -> None:
    """Draw the dispersion ellipse on the provided axes."""

    ellipse = Ellipse(
        xy=(ellipse_params["center_lon"], ellipse_params["center_lat"]),
        width=2 * ellipse_params["semi_major_km"],
        height=2 * ellipse_params["semi_minor_km"],
        angle=ellipse_params["angle_deg"],
        fill=False,
        **style,
    )
    ax.add_patch(ellipse)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
