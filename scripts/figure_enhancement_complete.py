"""
Task 3.1-3.2: Figure Quality Standards and Map Enhancement

Implements БЛОК 3, Tasks 3.1-3.2 from revision plan.
Provides tools for enhancing scientific figures to publication standards.
Includes functions for adding north arrows, scale bars, colorblind-friendly palettes, etc.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path
import logging
import sys
from typing import Tuple, List, Dict, Any, Optional
import colorsys

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'figure_enhancement.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class FigureEnhancer:
    """
    Enhances scientific figures to publication standards.
    Implements MDPI Aerospace figure requirements.
    """
    
    # Publication standards
    PUBLICATION_STANDARDS = {
        'font_size_min': 10,          # Minimum font size (pt)
        'dpi': 300,                   # Resolution for publication
        'line_width_min': 1.0,        # Minimum line width
        'marker_size_min': 6,         # Minimum marker size
        'colorbar_font_size': 10,     # Colorbar font size
        'legend_font_size': 10,       # Legend font size
        'axis_label_font_size': 12,   # Axis label font size
        'title_font_size': 14,        # Title font size
        'tick_label_font_size': 10,   # Tick label font size
    }
    
    # ColorBrewer colorblind-friendly palettes
    COLORBLIND_PALETTES = {
        'sequential': {
            'viridis': plt.cm.viridis,
            'plasma': plt.cm.plasma,
            'inferno': plt.cm.inferno,
            'magma': plt.cm.magma,
            'cividis': plt.cm.cividis,  # Specifically designed for colorblindness
        },
        'diverging': {
            'RdBu': plt.cm.RdBu,
            'PiYG': plt.cm.PiYG,
            'PRGn': plt.cm.PRGn,
            'BrBG': plt.cm.BrBG,
            'PuOr': plt.cm.PuOr,
        },
        'qualitative': {
            'Set2': plt.cm.Set2,
            'Set3': plt.cm.Set3,
            'tab20': plt.cm.tab20,
            'tab20c': plt.cm.tab20c,
            'Paired': plt.cm.Paired,
        }
    }
    
    # Hatching patterns for accessibility
    HATCHING_PATTERNS = [
        '',          # No hatch (solid)
        '////',      # Diagonal right
        '\\\\\\\\',  # Diagonal left
        '++++',      # Cross
        'xxxx',      # Cross diagonal
        '....',      # Dots
        '***',       # Stars
        'oo',        # Circles
    ]
    
    def __init__(self):
        logger.info("[INIT] FigureEnhancer initialized with publication standards")
        logger.info(f"[INFO] Font size minimum: {self.PUBLICATION_STANDARDS['font_size_min']}pt")
        logger.info(f"[INFO] DPI: {self.PUBLICATION_STANDARDS['dpi']}")
    
    def apply_publication_style(self, fig: plt.Figure = None, ax: plt.Axes = None) -> Tuple[plt.Figure, plt.Axes]:
        """
        Apply publication style to figure and axes.
        Returns enhanced figure and axes.
        """
        logger.info("[PROCESS] Applying publication style")
        
        if fig is None:
            fig = plt.gcf()
        if ax is None:
            ax = plt.gca()
        
        # Set figure DPI
        fig.set_dpi(self.PUBLICATION_STANDARDS['dpi'])
        
        # Apply font sizes
        self._apply_font_sizes(ax)
        
        # Enhance lines and markers
        self._enhance_lines_and_markers(ax)
        
        # Ensure sufficient contrast
        self._ensure_contrast(fig, ax)
        
        logger.info("[OK] Publication style applied")
        return fig, ax
    
    def _apply_font_sizes(self, ax: plt.Axes):
        """Apply minimum font sizes to all text elements."""
        # Title
        title = ax.get_title()
        if title:
            ax.set_title(title, fontsize=self.PUBLICATION_STANDARDS['title_font_size'])
        
        # Axis labels
        xlabel = ax.get_xlabel()
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=self.PUBLICATION_STANDARDS['axis_label_font_size'])
        
        ylabel = ax.get_ylabel()
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=self.PUBLICATION_STANDARDS['axis_label_font_size'])
        
        # Tick labels
        ax.tick_params(axis='both', which='major', 
                      labelsize=self.PUBLICATION_STANDARDS['tick_label_font_size'])
        
        # Legend
        legend = ax.get_legend()
        if legend:
            plt.setp(legend.get_texts(), fontsize=self.PUBLICATION_STANDARDS['legend_font_size'])
    
    def _enhance_lines_and_markers(self, ax: plt.Axes):
        """Enhance lines and markers for visibility."""
        lines = ax.get_lines()
        for line in lines:
            # Increase line width if too thin
            if line.get_linewidth() < self.PUBLICATION_STANDARDS['line_width_min']:
                line.set_linewidth(self.PUBLICATION_STANDARDS['line_width_min'])
            
            # Increase marker size if too small
            marker = line.get_marker()
            if marker and marker != 'None':
                marker_size = line.get_markersize()
                if marker_size < self.PUBLICATION_STANDARDS['marker_size_min']:
                    line.set_markersize(self.PUBLICATION_STANDARDS['marker_size_min'])
    
    def _ensure_contrast(self, fig: plt.Figure, ax: plt.Axes):
        """Ensure sufficient contrast between elements."""
        # Set figure facecolor to white for better contrast
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        # Ensure grid is visible but not distracting
        if ax.xaxis._gridOnMajor or ax.yaxis._gridOnMajor:
            ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    def add_north_arrow(self, ax: plt.Axes, 
                       location: str = 'upper right',
                       size: float = 0.1,
                       pad: float = 0.05,
                       color: str = 'black') -> mpatches.FancyArrowPatch:
        """
        Add a north arrow to the map.
        
        Parameters:
        -----------
        ax : matplotlib.axes.Axes
            Axes to add arrow to
        location : str
            Location: 'upper right', 'upper left', 'lower right', 'lower left'
        size : float
            Size of arrow as fraction of axes width
        pad : float
            Padding from axes edge
        color : str
            Arrow color
        
        Returns:
        --------
        arrow : matplotlib.patches.FancyArrowPatch
            The north arrow patch
        """
        logger.info(f"[PROCESS] Adding north arrow at {location}")
        
        # Get axes limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        
        # Calculate position based on location
        if location == 'upper right':
            x = xlim[1] - x_range * (size + pad)
            y = ylim[1] - y_range * (size + pad)
            dx = 0
            dy = -y_range * size
        elif location == 'upper left':
            x = xlim[0] + x_range * pad
            y = ylim[1] - y_range * (size + pad)
            dx = 0
            dy = -y_range * size
        elif location == 'lower right':
            x = xlim[1] - x_range * (size + pad)
            y = ylim[0] + y_range * pad
            dx = 0
            dy = y_range * size
        elif location == 'lower left':
            x = xlim[0] + x_range * pad
            y = ylim[0] + y_range * pad
            dx = 0
            dy = y_range * size
        else:
            raise ValueError(f"Unknown location: {location}")
        
        # Create arrow
        arrow = mpatches.FancyArrowPatch(
            (x, y), (x + dx, y + dy),
            arrowstyle='->,head_width=0.4,head_length=0.4',
            color=color,
            linewidth=2,
            zorder=10
        )
        
        ax.add_patch(arrow)
        
        # Add 'N' label
        label_x = x + dx * 0.5
        label_y = y + dy * 1.1
        ax.text(label_x, label_y, 'N', 
               ha='center', va='bottom',
               fontsize=self.PUBLICATION_STANDARDS['font_size_min'],
               fontweight='bold',
               color=color)
        
        logger.info("[OK] North arrow added")
        return arrow
    
    def add_scale_bar(self, ax: plt.Axes,
                     length_km: float = 10,
                     location: str = 'lower right',
                     color: str = 'black',
                     linewidth: float = 2) -> Line2D:
        """
        Add a scale bar to the map.
        
        Parameters:
        -----------
        ax : matplotlib.axes.Axes
            Axes to add scale bar to
        length_km : float
            Length of scale bar in kilometers
        location : str
            Location: 'upper right', 'upper left', 'lower right', 'lower left'
        color : str
            Scale bar color
        linewidth : float
            Line width
        
        Returns:
        --------
        scale_bar : matplotlib.lines.Line2D
            The scale bar line
        """
        logger.info(f"[PROCESS] Adding {length_km} km scale bar at {location}")
        
        # Get axes limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        x_range = xlim[1] - xlim[0]
        y_range = ylim[1] - ylim[0]
        
        # Calculate position (assuming map is in meters, 1 unit = 1 meter)
        # Convert km to meters
        length_m = length_km * 1000
        
        # Calculate position based on location
        pad_x = x_range * 0.05
        pad_y = y_range * 0.05
        
        if location == 'lower right':
            x_start = xlim[1] - pad_x - length_m
            x_end = xlim[1] - pad_x
            y = ylim[0] + pad_y
        elif location == 'lower left':
            x_start = xlim[0] + pad_x
            x_end = xlim[0] + pad_x + length_m
            y = ylim[0] + pad_y
        elif location == 'upper right':
            x_start = xlim[1] - pad_x - length_m
            x_end = xlim[1] - pad_x
            y = ylim[1] - pad_y
        elif location == 'upper left':
            x_start = xlim[0] + pad_x
            x_end = xlim[0] + pad_x + length_m
            y = ylim[1] - pad_y
        else:
            raise ValueError(f"Unknown location: {location}")
        
        # Create scale bar line
        scale_bar = Line2D([x_start, x_end], [y, y],
                          color=color, linewidth=linewidth, zorder=10)
        ax.add_line(scale_bar)
        
        # Add perpendicular lines at ends
        end_length = y_range * 0.01
        left_end = Line2D([x_start, x_start], [y - end_length, y + end_length],
                         color=color, linewidth=linewidth, zorder=10)
        right_end = Line2D([x_end, x_end], [y - end_length, y + end_length],
                          color=color, linewidth=linewidth, zorder=10)
        ax.add_line(left_end)
        ax.add_line(right_end)
        
        # Add label
        label_x = (x_start + x_end) / 2
        label_y = y - end_length * 2
        ax.text(label_x, label_y, f'{length_km} km',
               ha='center', va='top',
               fontsize=self.PUBLICATION_STANDARDS['font_size_min'],
               color=color)
        
        logger.info("[OK] Scale bar added")
        return scale_bar
    
    def create_colorblind_friendly_cmap(self, n_colors: int = 10,
                                       palette_type: str = 'sequential',
                                       palette_name: str = 'viridis') -> plt.cm:
        """
        Create a colorblind-friendly colormap.
        
        Parameters:
        -----------
        n_colors : int
            Number of colors in the colormap
        palette_type : str
            Type of palette: 'sequential', 'diverging', or 'qualitative'
        palette_name : str
            Name of palette (see COLORBLIND_PALETTES)
        
        Returns:
        --------
        cmap : matplotlib.colors.Colormap
            Colorblind-friendly colormap
        """
        logger.info(f"[PROCESS] Creating colorblind-friendly colormap: {palette_name}")
        
        if palette_type not in self.COLORBLIND_PALETTES:
            raise ValueError(f"Unknown palette type: {palette_type}. "
                           f"Available: {list(self.COLORBLIND_PALETTES.keys())}")
        
        if palette_name not in self.COLORBLIND_PALETTES[palette_type]:
            available = list(self.COLORBLIND_PALETTES[palette_type].keys())
            raise ValueError(f"Unknown palette name: {palette_name}. "
                           f"Available for {palette_type}: {available}")
        
        cmap = self.COLORBLIND_PALETTES[palette_type][palette_name]
        
        # For sequential palettes, ensure we use the full range
        if palette_type == 'sequential':
            colors = cmap(np.linspace(0.1, 0.9, n_colors))
        elif palette_type == 'diverging':
            colors = cmap(np.linspace(0, 1, n_colors))
        else:  # qualitative
            colors = cmap(np.linspace(0, 1, n_colors))
        
        logger.info(f"[OK] Colorblind-friendly colormap created with {n_colors} colors")
        return colors
    
    def add_hatching_for_accessibility(self, ax: plt.Axes,
                                      patches: List[mpatches.Patch] = None,
                                      pattern_cycle: List[str] = None):
        """
        Add hatching patterns to patches for accessibility.
        
        Parameters:
        -----------
        ax : matplotlib.axes.Axes
            Axes containing patches
        patches : List[matplotlib.patches.Patch], optional
            List of patches to add hatching to. If None, uses ax.patches
        pattern_cycle : List[str], optional
            List of hatching patterns to cycle through
        """
        logger.info("[PROCESS] Adding hatching patterns for accessibility")
        
        if patches is None:
            patches = ax.patches
        
        if pattern_cycle is None:
            pattern_cycle = self.HATCHING_PATTERNS
        
        if not patches:
            logger.warning("[WARNING] No patches found to add hatching to")
            return
        
        # Apply hatching patterns
        for i, patch in enumerate(patches):
            pattern = pattern_cycle[i % len(pattern_cycle)]
            patch.set_hatch(pattern)
            # Also set edge color for better visibility
            if patch.get_edgecolor() == (0.0, 0.0, 0.0, 0.0):  # Transparent
                patch.set_edgecolor('black')
            patch.set_linewidth(0.5)
        
        logger.info(f"[OK] Hatching patterns added to {len(patches)} patches")
    
    def enhance_existing_figure(self, fig_path: str, output_path: str = None,
                               add_north_arrow: bool = True,
                               add_scale_bar: bool = True,
                               apply_colorblind_palette: bool = True,
                               add_hatching: bool = True) -> str:
        """
        Enhance an existing figure file.
        
        Parameters:
        -----------
        fig_path : str
            Path to existing figure file
        output_path : str, optional
            Output path. If None, adds '_enhanced' suffix
        add_north_arrow : bool
            Whether to add north arrow
        add_scale_bar : bool
            Whether to add scale bar
        apply_colorblind_palette : bool
            Whether to apply colorblind-friendly palette
        add_hatching : bool
            Whether to add hatching patterns
        
        Returns:
        --------
        output_path : str
            Path to enhanced figure
        """
        logger.info(f"[PROCESS] Enhancing existing figure: {fig_path}")
        
        # Load the figure
        try:
            # Note: This is a