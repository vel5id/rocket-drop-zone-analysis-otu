"""Heatmap utilities for Q_OTU surfaces."""
from __future__ import annotations

import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt


def plot_heatmap(matrix: np.ndarray, *, title: str = "Q_OTU Heatmap") -> plt.Figure:
    """Render a heatmap using seaborn."""

    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(matrix, ax=ax, cmap="viridis", vmin=0.0, vmax=1.0)
    ax.set_title(title)
    return fig
