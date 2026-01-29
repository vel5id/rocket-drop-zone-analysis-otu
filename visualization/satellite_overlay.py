"""Satellite visualization with multi-index GeoJSON layers."""
from __future__ import annotations
import os, math, folium, json
from folium.plugins import HeatMap
import numpy as np
from typing import List, Dict, Any, Optional, Tuple

try:
    from gee.authenticator import initialize_ee
except: 
    def initialize_ee(): pass

try:
    from gee.fao_soil_zones import fetch_fao_soil_zones, get_bonitet_color
    HAS_FAO_SOIL = True
except ImportError:
    HAS_FAO_SOIL = False
    def fetch_fao_soil_zones(*args, **kwargs): return None
    def get_bonitet_color(b): return "#CCCCCC"


# Color schemes for different indices
def _get_otu_color(val):
    """OTU: Green (stable) -> Red (unstable)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 0.25: return '#ff0000'
    if val < 0.50: return '#ff8800'
    if val < 0.75: return '#88ff00'
    return '#00aa00'


# ============================================================================
# RELATIVE NORMALIZATION COLOR FUNCTIONS (continuous gradient based on min/max)
# ============================================================================

def _interpolate_color(val: float, min_val: float, max_val: float, colors: List[str]) -> str:
    """Interpolate between colors based on normalized value."""
    if val is None or (isinstance(val, float) and np.isnan(val)): 
        return None
    
    # Normalize to 0-1
    if max_val == min_val:
        norm = 0.5
    else:
        norm = (val - min_val) / (max_val - min_val)
    norm = max(0.0, min(1.0, norm))
    
    # Find color segment
    n_segments = len(colors) - 1
    segment = int(norm * n_segments)
    segment = min(segment, n_segments - 1)
    
    # Interpolate within segment
    local_t = (norm * n_segments) - segment
    
    c1 = colors[segment]
    c2 = colors[segment + 1]
    
    # Parse hex colors
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    
    # Interpolate
    r = int(r1 + (r2 - r1) * local_t)
    g = int(g1 + (g2 - g1) * local_t)
    b = int(b1 + (b2 - b1) * local_t)
    
    return f'#{r:02x}{g:02x}{b:02x}'


# Color gradients for relative normalization
COLOR_GRADIENTS = {
    'otu': ['#ff0000', '#ff4400', '#ff8800', '#ffcc00', '#88ff00', '#00aa00'],  # Red -> Green
    'ndvi': ['#8B4513', '#DAA520', '#9ACD32', '#228B22', '#006400'],  # Brown -> Green
    'q_si': ['#ff0000', '#ff8800', '#ffcc00', '#00aaff', '#0044ff'],  # Red -> Blue
    'q_bi': ['#888888', '#aa88aa', '#8844aa', '#6622aa', '#440088'],  # Gray -> Purple
    'q_relief': ['#ff6600', '#ffaa00', '#dddd66', '#44aaaa', '#008888'],  # Orange -> Teal
    'q_fire': ['#ff0000', '#ff6600', '#aaaa00', '#66aa00', '#00aa00'],  # Red -> Green
    'slope': ['#00aa00', '#88ff00', '#ffaa00', '#ff6600', '#ff0000'],  # Green -> Red
    'bonitet': ['#89CFF0', '#FFB6C1', '#90EE90', '#40E0D0'],  # Paper colors
}


def create_relative_color_func(prop_name: str, data_min: float, data_max: float):
    """Create a color function with relative normalization based on data range."""
    gradient = COLOR_GRADIENTS.get(prop_name, COLOR_GRADIENTS['otu'])
    
    def color_func(val):
        return _interpolate_color(val, data_min, data_max, gradient)
    
    return color_func


def compute_data_ranges(geojson_data: Dict) -> Dict[str, Tuple[float, float]]:
    """Compute min/max for each property in GeoJSON for relative normalization."""
    ranges = {}
    
    if not geojson_data or 'features' not in geojson_data:
        return ranges
    
    # Collect all values for each property
    prop_values = {}
    for feat in geojson_data['features']:
        props = feat.get('properties', {})
        for key, val in props.items():
            if isinstance(val, (int, float)) and not (isinstance(val, float) and np.isnan(val)):
                if key not in prop_values:
                    prop_values[key] = []
                prop_values[key].append(val)
    
    # Compute ranges
    for key, values in prop_values.items():
        if values:
            ranges[key] = (min(values), max(values))
    
    return ranges

def _get_ndvi_color(val):
    """NDVI: Brown (bare) -> Green (vegetated)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 0.2: return '#8B4513'   # Brown - bare
    if val < 0.4: return '#DAA520'   # Goldenrod
    if val < 0.6: return '#9ACD32'   # Yellow-green
    if val < 0.8: return '#228B22'   # Forest green
    return '#006400'                 # Dark green

def _get_soil_strength_color(val):
    """Q_Si: Red (weak) -> Blue (strong)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 0.25: return '#ff0000'
    if val < 0.50: return '#ff8800'
    if val < 0.75: return '#00aaff'
    return '#0044ff'

def _get_soil_quality_color(val):
    """Q_Bi: Gray (poor) -> Purple (rich)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 0.25: return '#888888'
    if val < 0.50: return '#aa88aa'
    if val < 0.75: return '#8844aa'
    return '#440088'

def _get_relief_color(val):
    """Q_Relief: Orange (unfavorable) -> Teal (favorable)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 0.25: return '#ff6600'
    if val < 0.50: return '#ffaa00'
    if val < 0.75: return '#44aaaa'
    return '#008888'

def _get_fire_risk_color(val):
    """Q_Fire: Red (high risk) -> Green (low risk)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 0.25: return '#ff0000'
    if val < 0.50: return '#ff6600'
    if val < 0.75: return '#aaaa00'
    return '#00aa00'

def _get_slope_color(val):
    """Slope: Green (flat) -> Red (steep)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 5: return '#00aa00'      # Flat
    if val < 15: return '#88ff00'     # Gentle
    if val < 30: return '#ffaa00'     # Moderate
    if val < 45: return '#ff6600'     # Steep
    return '#ff0000'                  # Very steep

def _get_aspect_color(val):
    """Aspect: Smooth color wheel gradient for 8 directions.
    
    Uses HSL color wheel where:
    - N (0°) = Blue (hue=240)
    - E (90°) = Yellow (hue=60)  
    - S (180°) = Red (hue=0)
    - W (270°) = Green (hue=120)
    
    Smoothly interpolates between all compass directions.
    """
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    
    # Normalize angle to 0-360
    angle = val % 360
    
    # Map compass angle to hue (color wheel)
    # N=0° -> Blue (hue=240°)
    # E=90° -> Yellow (hue=60°)
    # S=180° -> Red (hue=0°)
    # W=270° -> Green (hue=120°)
    # The mapping is: hue = (240 - angle) % 360, but we need smooth wrap
    
    # Custom mapping for intuitive compass colors
    # Shift so N=blue, go clockwise through cyan, green, yellow, orange, red, magenta, back to blue
    hue = (240 - angle * 0.667) % 360  # Scale and shift for nice gradient
    
    # Convert HSL to RGB (saturation=80%, lightness=50%)
    import colorsys
    h = hue / 360.0
    s = 0.75
    l = 0.5
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    
    return f'#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'


def create_impact_visualization(
    center_lat,
    center_lon,
    primary_ellipse,
    fragment_ellipse,
    impact_points,
    grid_cells=None,
    otu_data: Optional[Dict[str, float]] = None,
    full_data: Optional[List[Dict[str, float]]] = None,
    output_path="output/impact_visualization.html",
    satellite_date="2023-07-15",
    buffer_km=100,
    geojson_path: Optional[str] = None,
    use_relative_colors: bool = True,  # use continuous gradient based on data range
    raw_polygons: Optional[List[List[Tuple[float, float]]]] = None,  # Raw shapefile polygons
):
    """Create interactive map with 7 switchable index layers.
    
    Args:
        use_relative_colors: If True, use continuous color gradient based on 
                            actual min/max of data. If False, use fixed discrete classes.
        raw_polygons: List of polygon coordinate lists [(lat, lon), ...] from shapefiles.
                      If provided, these are drawn instead of ellipse approximations.
    """
    initialize_ee()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles=None)
    
    # Base layers
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Satellite"
    ).add_to(m)
    folium.TileLayer(tiles="OpenStreetMap", name="Map").add_to(m)
    
    # Zone boundaries (raw polygons or ellipses)
    zone_grp = folium.FeatureGroup(name="Zone Boundaries", show=True)
    if raw_polygons:
        # Use raw shapefile polygons
        polygon_names = ["Zone 15", "Zone 25"] if len(raw_polygons) >= 2 else [f"Zone {i+1}" for i in range(len(raw_polygons))]
        polygon_colors = ["red", "orange", "blue", "green"]
        for i, poly in enumerate(raw_polygons):
            color = polygon_colors[i % len(polygon_colors)]
            _add_raw_polygon(zone_grp, poly, color, polygon_names[i] if i < len(polygon_names) else f"Polygon {i+1}")
    else:
        # Use ellipse approximations
        if primary_ellipse: _add_ellipse(zone_grp, primary_ellipse, "red", "Primary")
        if fragment_ellipse: _add_ellipse(zone_grp, fragment_ellipse, "orange", "Fragments")
    zone_grp.add_to(m)
    
    
    # Impact heatmap (only for Monte Carlo mode, skip for shapefiles)
    if not raw_polygons:
        heat_grp = folium.FeatureGroup(name="Impact Heatmap", show=True)
        frag_pts = [[pt["lat"], pt["lon"]] for pt in impact_points if pt.get("is_fragment")]
        if frag_pts:
            HeatMap(frag_pts, radius=15, blur=10).add_to(heat_grp)
        heat_grp.add_to(m)
    
    # Load GeoJSON data
    geojson_data = None
    if geojson_path and os.path.exists(geojson_path):
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
    elif grid_cells and full_data:
        # Build GeoJSON from data
        features = []
        for i, c in enumerate(grid_cells):
            if i >= len(full_data): break
            props = full_data[i]
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [c.min_lon, c.min_lat], [c.max_lon, c.min_lat],
                        [c.max_lon, c.max_lat], [c.min_lon, c.max_lat],
                        [c.min_lon, c.min_lat]
                    ]]
                },
                "properties": props
            }
            features.append(feature)
        geojson_data = {"type": "FeatureCollection", "features": features}
    
    if geojson_data:
        # Compute data ranges for relative normalization
        data_ranges = compute_data_ranges(geojson_data) if use_relative_colors else {}
        
        # Property mappings: (name, property, gradient_key, default_fixed_func, show)
        layer_defs = [
            ("1. OTU Index", "q_otu", "otu", _get_otu_color, True),
            ("2. NDVI", "q_ndvi", "ndvi", _get_ndvi_color, False),
            ("3. Soil Strength (Q_Si)", "q_si", "q_si", _get_soil_strength_color, False),
            ("4. Soil Quality (Q_Bi)", "q_bi", "q_bi", _get_soil_quality_color, False),
            ("5. Relief (Q_Relief)", "q_relief", "q_relief", _get_relief_color, False),
            ("6. Fire Risk", "q_fire", "q_fire", _get_fire_risk_color, False),
            ("7. Slope", "slope", "slope", _get_slope_color, False),
            ("8. Aspect", "aspect", "aspect", _get_aspect_color, False),
        ]
        
        for layer_name, prop_name, grad_key, fixed_func, show in layer_defs:
            # Check if property exists in data
            if geojson_data["features"] and prop_name not in geojson_data["features"][0].get("properties", {}):
                continue
            
            # Choose color function based on mode
            if use_relative_colors and prop_name in data_ranges:
                min_v, max_v = data_ranges[prop_name]
                color_func = create_relative_color_func(grad_key, min_v, max_v)
            else:
                color_func = fixed_func
            
            layer = folium.GeoJson(
                geojson_data,
                name=layer_name,
                show=show,
                style_function=lambda f, cf=color_func, pn=prop_name: {
                    'fillColor': cf(f['properties'].get(pn)),
                    'color': 'none',
                    'fillOpacity': 0.7 if cf(f['properties'].get(pn)) else 0,
                    'weight': 0
                },
                tooltip=folium.GeoJsonTooltip(
                    fields=[prop_name],
                    aliases=[layer_name.split('. ')[-1] + ':'],
                    localize=True
                )
            )
            layer.add_to(m)
    
    # Multi-index legend
    legend_html = """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:10px;border:2px solid grey;border-radius:8px;font-size:10px;max-width:300px;max-height:400px;overflow-y:auto;">
    <b style="font-size:12px;">Index Legends</b>
    <hr style="margin:5px 0;">
    
    <b>OTU (Stability)</b><br>
    <span style="background:#00aa00;color:white;padding:0 5px;">0.75-1.0 High</span>
    <span style="background:#88ff00;padding:0 5px;">0.50-0.75</span>
    <span style="background:#ff8800;color:white;padding:0 5px;">0.25-0.50</span>
    <span style="background:#ff0000;color:white;padding:0 5px;">0-0.25 Low</span>
    <hr style="margin:5px 0;">
    
    <b>NDVI (Vegetation)</b><br>
    <span style="background:#006400;color:white;padding:0 5px;">0.8-1.0</span>
    <span style="background:#228B22;color:white;padding:0 5px;">0.6-0.8</span>
    <span style="background:#9ACD32;padding:0 5px;">0.4-0.6</span>
    <span style="background:#DAA520;padding:0 5px;">0.2-0.4</span>
    <span style="background:#8B4513;color:white;padding:0 5px;">0-0.2</span>
    <hr style="margin:5px 0;">
    
    <b>Slope (degrees)</b><br>
    <span style="background:#00aa00;color:white;padding:0 5px;">&lt;5</span>
    <span style="background:#88ff00;padding:0 5px;">5-15</span>
    <span style="background:#ffaa00;padding:0 5px;">15-30</span>
    <span style="background:#ff6600;color:white;padding:0 5px;">30-45</span>
    <span style="background:#ff0000;color:white;padding:0 5px;">&gt;45</span>
    <hr style="margin:5px 0;">
    
    <b>Aspect (Exposure)</b><br>
    <span style="background:#0088ff;color:white;padding:0 5px;">N</span>
    <span style="background:#ffcc00;padding:0 5px;">E</span>
    <span style="background:#ff4400;color:white;padding:0 5px;">S</span>
    <span style="background:#00aa44;color:white;padding:0 5px;">W</span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    m.save(output_path)
    return output_path


# Individual legends for each index
LEGENDS = {
    "q_otu": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">OTU Index (Stability)</b><br><br>
    <span style="background:#00aa00;color:white;padding:2px 8px;margin:2px;">0.75-1.0 High</span><br>
    <span style="background:#88ff00;padding:2px 8px;margin:2px;">0.50-0.75</span><br>
    <span style="background:#ff8800;color:white;padding:2px 8px;margin:2px;">0.25-0.50</span><br>
    <span style="background:#ff0000;color:white;padding:2px 8px;margin:2px;">0-0.25 Low</span>
    </div>
    """,
    "q_ndvi": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">NDVI (Vegetation)</b><br><br>
    <span style="background:#006400;color:white;padding:2px 8px;margin:2px;">0.8-1.0 Dense</span><br>
    <span style="background:#228B22;color:white;padding:2px 8px;margin:2px;">0.6-0.8</span><br>
    <span style="background:#9ACD32;padding:2px 8px;margin:2px;">0.4-0.6</span><br>
    <span style="background:#DAA520;padding:2px 8px;margin:2px;">0.2-0.4</span><br>
    <span style="background:#8B4513;color:white;padding:2px 8px;margin:2px;">0-0.2 Bare</span>
    </div>
    """,
    "q_si": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">Soil Strength (Q_Si)</b><br><br>
    <span style="background:#0044ff;color:white;padding:2px 8px;margin:2px;">0.75-1.0 Strong</span><br>
    <span style="background:#00aaff;padding:2px 8px;margin:2px;">0.50-0.75</span><br>
    <span style="background:#ff8800;color:white;padding:2px 8px;margin:2px;">0.25-0.50</span><br>
    <span style="background:#ff0000;color:white;padding:2px 8px;margin:2px;">0-0.25 Weak</span>
    </div>
    """,
    "q_bi": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">Soil Quality (Q_Bi)</b><br><br>
    <span style="background:#440088;color:white;padding:2px 8px;margin:2px;">0.75-1.0 Rich</span><br>
    <span style="background:#8844aa;color:white;padding:2px 8px;margin:2px;">0.50-0.75</span><br>
    <span style="background:#aa88aa;padding:2px 8px;margin:2px;">0.25-0.50</span><br>
    <span style="background:#888888;color:white;padding:2px 8px;margin:2px;">0-0.25 Poor</span>
    </div>
    """,
    "q_relief": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">Relief (Q_Relief)</b><br><br>
    <span style="background:#008888;color:white;padding:2px 8px;margin:2px;">0.75-1.0 Favorable</span><br>
    <span style="background:#44aaaa;padding:2px 8px;margin:2px;">0.50-0.75</span><br>
    <span style="background:#ffaa00;padding:2px 8px;margin:2px;">0.25-0.50</span><br>
    <span style="background:#ff6600;color:white;padding:2px 8px;margin:2px;">0-0.25 Unfavorable</span>
    </div>
    """,
    "q_fire": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">Fire Risk (Q_Fire)</b><br><br>
    <span style="background:#00aa00;color:white;padding:2px 8px;margin:2px;">0.75-1.0 Low Risk</span><br>
    <span style="background:#aaaa00;padding:2px 8px;margin:2px;">0.50-0.75</span><br>
    <span style="background:#ff6600;color:white;padding:2px 8px;margin:2px;">0.25-0.50</span><br>
    <span style="background:#ff0000;color:white;padding:2px 8px;margin:2px;">0-0.25 High Risk</span>
    </div>
    """,
    "slope": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">Slope (degrees)</b><br><br>
    <span style="background:#00aa00;color:white;padding:2px 8px;margin:2px;">&lt;5° Flat</span><br>
    <span style="background:#88ff00;padding:2px 8px;margin:2px;">5-15° Gentle</span><br>
    <span style="background:#ffaa00;padding:2px 8px;margin:2px;">15-30° Moderate</span><br>
    <span style="background:#ff6600;color:white;padding:2px 8px;margin:2px;">30-45° Steep</span><br>
    <span style="background:#ff0000;color:white;padding:2px 8px;margin:2px;">&gt;45° Very Steep</span>
    </div>
    """,
    "aspect": """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:12px;">
    <b style="font-size:14px;">Aspect (8 Directions)</b><br><br>
    <div style="display:flex;flex-wrap:wrap;gap:4px;">
    <span style="background:#1f5fbf;color:white;padding:2px 8px;border-radius:3px;">N (0°)</span>
    <span style="background:#3fbfbf;color:white;padding:2px 8px;border-radius:3px;">NE (45°)</span>
    <span style="background:#5fbf1f;color:white;padding:2px 8px;border-radius:3px;">E (90°)</span>
    <span style="background:#bfbf1f;padding:2px 8px;border-radius:3px;">SE (135°)</span>
    <span style="background:#bf5f1f;color:white;padding:2px 8px;border-radius:3px;">S (180°)</span>
    <span style="background:#bf1f5f;color:white;padding:2px 8px;border-radius:3px;">SW (225°)</span>
    <span style="background:#5f1fbf;color:white;padding:2px 8px;border-radius:3px;">W (270°)</span>
    <span style="background:#1f3fbf;color:white;padding:2px 8px;border-radius:3px;">NW (315°)</span>
    </div>
    <br><i style="font-size:10px;">Smooth gradient between directions</i>
    </div>
    """
}

# Index layer definitions: (display_name, property_name, color_func, filename_suffix)
INDEX_LAYERS = [
    ("OTU Index", "q_otu", _get_otu_color, "otu"),
    ("NDVI", "q_ndvi", _get_ndvi_color, "ndvi"),
    ("Soil Strength (Q_Si)", "q_si", _get_soil_strength_color, "soil_strength"),
    ("Soil Quality (Q_Bi)", "q_bi", _get_soil_quality_color, "soil_quality"),
    ("Relief (Q_Relief)", "q_relief", _get_relief_color, "relief"),
    ("Fire Risk", "q_fire", _get_fire_risk_color, "fire_risk"),
    ("Slope", "slope", _get_slope_color, "slope"),
    ("Aspect", "aspect", _get_aspect_color, "aspect"),
]


def create_individual_index_visualizations(
    center_lat,
    center_lon,
    primary_ellipse,
    fragment_ellipse,
    impact_points,
    grid_cells=None,
    full_data: Optional[List[Dict[str, float]]] = None,
    output_dir="output/indices",
    geojson_path: Optional[str] = None,
    raw_polygons: Optional[List[List[Tuple[float, float]]]] = None,  # Raw shapefile polygons
) -> List[str]:
    """Create separate HTML files for each index visualization.
    
    Args:
        raw_polygons: If provided, draw real polygon boundaries instead of ellipses.
    
    Returns list of created file paths.
    """
    initialize_ee()
    
    # Load or build GeoJSON data
    geojson_data = None
    if geojson_path and os.path.exists(geojson_path):
        with open(geojson_path, 'r') as f:
            geojson_data = json.load(f)
    elif grid_cells and full_data:
        features = []
        for i, c in enumerate(grid_cells):
            if i >= len(full_data): break
            props = full_data[i]
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[
                        [c.min_lon, c.min_lat], [c.max_lon, c.min_lat],
                        [c.max_lon, c.max_lat], [c.min_lon, c.max_lat],
                        [c.min_lon, c.min_lat]
                    ]]
                },
                "properties": props
            }
            features.append(feature)
        geojson_data = {"type": "FeatureCollection", "features": features}
    
    if not geojson_data:
        print("No GeoJSON data available for visualization")
        return []
    
    os.makedirs(output_dir, exist_ok=True)
    created_files = []
    
    for display_name, prop_name, color_func, filename_suffix in INDEX_LAYERS:
        # Check if property exists in data
        if not geojson_data["features"]:
            continue
        if prop_name not in geojson_data["features"][0].get("properties", {}):
            print(f"Skipping {display_name}: property '{prop_name}' not found in data")
            continue
        
        # Create map for this index
        m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles=None)
        
        # Base layers
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri", name="Satellite"
        ).add_to(m)
        folium.TileLayer(tiles="OpenStreetMap", name="Map").add_to(m)
        
        # Zone boundaries (raw polygons or ellipses)
        zone_grp = folium.FeatureGroup(name="Zone Boundaries", show=True)
        if raw_polygons:
            polygon_names = ["Zone 15", "Zone 25"] if len(raw_polygons) >= 2 else [f"Zone {i+1}" for i in range(len(raw_polygons))]
            polygon_colors = ["red", "orange", "blue", "green"]
            for i, poly in enumerate(raw_polygons):
                color = polygon_colors[i % len(polygon_colors)]
                _add_raw_polygon(zone_grp, poly, color, polygon_names[i] if i < len(polygon_names) else f"Polygon {i+1}")
        else:
            if primary_ellipse: _add_ellipse(zone_grp, primary_ellipse, "red", "Primary")
            if fragment_ellipse: _add_ellipse(zone_grp, fragment_ellipse, "orange", "Fragments")
        zone_grp.add_to(m)
        
        # Impact heatmap (only for Monte Carlo mode, skip for shapefiles)
        if not raw_polygons:
            heat_grp = folium.FeatureGroup(name="Impact Heatmap", show=True)
            frag_pts = [[pt["lat"], pt["lon"]] for pt in impact_points if pt.get("is_fragment")]
            if frag_pts:
                HeatMap(frag_pts, radius=15, blur=10).add_to(heat_grp)
            heat_grp.add_to(m)
        
        # Index layer
        layer = folium.GeoJson(
            geojson_data,
            name=display_name,
            show=True,
            style_function=lambda f, cf=color_func, pn=prop_name: {
                'fillColor': cf(f['properties'].get(pn)),
                'color': 'none',
                'fillOpacity': 0.7 if cf(f['properties'].get(pn)) else 0,
                'weight': 0
            },
            tooltip=folium.GeoJsonTooltip(
                fields=[prop_name],
                aliases=[display_name + ':'],
                localize=True
            )
        )
        layer.add_to(m)
        
        # Add index-specific legend
        if prop_name in LEGENDS:
            m.get_root().html.add_child(folium.Element(LEGENDS[prop_name]))
        
        # Layer control
        folium.LayerControl(collapsed=False).add_to(m)
        
        # Save
        output_path = os.path.join(output_dir, f"index_{filename_suffix}.html")
        m.save(output_path)
        created_files.append(output_path)
        print(f"Created: {output_path}")
    
    return created_files


def create_ballistic_points_visualization(
    center_lat,
    center_lon,
    primary_ellipse,
    fragment_ellipse,
    impact_points,
    output_path="output/indices/ballistic_modeling.html",
) -> str:
    """Create visualization showing ballistic modeling points that form ellipses.
    
    Shows individual impact points from Monte Carlo simulation with ellipses overlay,
    demonstrating the statistical basis for dispersion ellipse construction.
    
    Returns path to created file.
    """
    initialize_ee()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles=None)
    
    # Base layers
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Satellite"
    ).add_to(m)
    folium.TileLayer(tiles="OpenStreetMap", name="Map").add_to(m)
    
    # Primary body impact points (non-fragments)
    primary_pts_grp = folium.FeatureGroup(name="Primary Body Impacts", show=True)
    primary_pts = [pt for pt in impact_points if not pt.get("is_fragment", False)]
    for pt in primary_pts:
        folium.CircleMarker(
            location=[pt["lat"], pt["lon"]],
            radius=3,
            color='#cc0000',
            fill=True,
            fillColor='#ff0000',
            fillOpacity=0.7,
            weight=1,
            popup=f"Primary: ({pt['lat']:.4f}, {pt['lon']:.4f})"
        ).add_to(primary_pts_grp)
    primary_pts_grp.add_to(m)
    
    # Fragment impact points
    fragment_pts_grp = folium.FeatureGroup(name="Fragment Impacts", show=True)
    fragment_pts = [pt for pt in impact_points if pt.get("is_fragment", False)]
    for pt in fragment_pts:
        folium.CircleMarker(
            location=[pt["lat"], pt["lon"]],
            radius=2,
            color='#cc6600',
            fill=True,
            fillColor='#ff8800',
            fillOpacity=0.6,
            weight=1,
            popup=f"Fragment: ({pt['lat']:.4f}, {pt['lon']:.4f})"
        ).add_to(fragment_pts_grp)
    fragment_pts_grp.add_to(m)
    
    # Ellipses overlay
    ellipse_grp = folium.FeatureGroup(name="Dispersion Ellipses (3σ)", show=True)
    if primary_ellipse: _add_ellipse(ellipse_grp, primary_ellipse, "red", "Primary 3σ")
    if fragment_ellipse: _add_ellipse(ellipse_grp, fragment_ellipse, "orange", "Fragments 3σ")
    ellipse_grp.add_to(m)
    
    # Impact heatmap (optional, can toggle)
    heat_grp = folium.FeatureGroup(name="Density Heatmap", show=False)
    all_pts = [[pt["lat"], pt["lon"]] for pt in impact_points]
    if all_pts:
        HeatMap(all_pts, radius=12, blur=8, max_zoom=10).add_to(heat_grp)
    heat_grp.add_to(m)
    
    # Statistics legend
    n_primary = len(primary_pts)
    n_fragments = len(fragment_pts)
    n_total = len(impact_points)
    
    primary_info = ""
    if primary_ellipse:
        primary_info = f"""
        <b>Primary Ellipse:</b><br>
        Center: {primary_ellipse['center_lat']:.4f}°, {primary_ellipse['center_lon']:.4f}°<br>
        Size: {primary_ellipse['semi_major_km']:.1f} × {primary_ellipse['semi_minor_km']:.1f} km<br>
        Angle: {primary_ellipse.get('angle_deg', 0):.1f}°<br><br>
        """
    
    fragment_info = ""
    if fragment_ellipse:
        fragment_info = f"""
        <b>Fragment Ellipse:</b><br>
        Center: {fragment_ellipse['center_lat']:.4f}°, {fragment_ellipse['center_lon']:.4f}°<br>
        Size: {fragment_ellipse['semi_major_km']:.1f} × {fragment_ellipse['semi_minor_km']:.1f} km<br>
        Angle: {fragment_ellipse.get('angle_deg', 0):.1f}°<br>
        """
    
    legend_html = f"""
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:11px;max-width:280px;">
    <b style="font-size:14px;">Ballistic Modeling Results</b><br>
    <hr style="margin:8px 0;">
    
    <b>Monte Carlo Simulation:</b><br>
    <span style="color:#ff0000;">●</span> Primary impacts: {n_primary}<br>
    <span style="color:#ff8800;">●</span> Fragment impacts: {n_fragments}<br>
    Total points: {n_total}<br><br>
    
    {primary_info}
    {fragment_info}
    
    <hr style="margin:8px 0;">
    <i style="font-size:10px;">Ellipses show 3σ dispersion bounds<br>
    based on statistical analysis of<br>
    Monte Carlo trajectory simulations</i>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    m.save(output_path)
    print(f"Created: {output_path}")
    
    return output_path


def _add_ellipse(grp, ellipse, color, name, npts=64):
    """Add ellipse polygon."""
    clat, clon = ellipse["center_lat"], ellipse["center_lon"]
    a_km, b_km = ellipse["semi_major_km"], ellipse["semi_minor_km"]
    angle_north = ellipse.get("angle_deg", 0)
    
    lat_rad = math.radians(clat)
    deg_lat = 1/111.0
    deg_lon = 1/(111.0 * math.cos(lat_rad))
    math_angle = math.radians(90 - angle_north)
    
    coords = []
    for t in np.linspace(0, 2*np.pi, npts):
        x = a_km * deg_lon * np.cos(t)
        y = b_km * deg_lat * np.sin(t)
        xr = x * np.cos(math_angle) - y * np.sin(math_angle)
        yr = x * np.sin(math_angle) + y * np.cos(math_angle)
        coords.append([clat + yr, clon + xr])
    
    popup_text = f"{name}: {a_km:.1f}x{b_km:.1f}km"
    folium.Polygon(coords, color=color, weight=3, fill=False, popup=popup_text).add_to(grp)
    folium.Marker([clat, clon], popup=f"{name} Center", 
                  icon=folium.Icon(color="red" if "Primary" in name else "orange")).add_to(grp)


def _add_raw_polygon(grp, polygon_coords, color, name, fill=False):
    """
    Add a raw polygon from shapefile coordinates (no PCA ellipse conversion).
    
    Args:
        grp: Folium FeatureGroup to add to
        polygon_coords: List of (lat, lon) tuples from shapefile
        color: Polygon border color
        name: Name for popup
        fill: Whether to fill the polygon
    """
    # Convert to folium format [lat, lon]
    coords = [[pt[0], pt[1]] for pt in polygon_coords]
    
    # Calculate center for marker
    center_lat = np.mean([pt[0] for pt in polygon_coords])
    center_lon = np.mean([pt[1] for pt in polygon_coords])
    
    # Calculate approximate area
    # Simple shoelace formula approximation
    n = len(polygon_coords)
    area_km2 = 0
    for i in range(n):
        j = (i + 1) % n
        lat1, lon1 = polygon_coords[i]
        lat2, lon2 = polygon_coords[j]
        # Convert to km
        x1 = lon1 * 111 * np.cos(np.radians(center_lat))
        y1 = lat1 * 111
        x2 = lon2 * 111 * np.cos(np.radians(center_lat))
        y2 = lat2 * 111
        area_km2 += x1 * y2 - x2 * y1
    area_km2 = abs(area_km2) / 2
    
    popup_text = f"{name}: ~{area_km2:.0f} km²"
    folium.Polygon(
        coords, 
        color=color, 
        weight=3, 
        fill=fill,
        fillColor=color,
        fillOpacity=0.2 if fill else 0,
        popup=popup_text
    ).add_to(grp)
    
    folium.Marker(
        [center_lat, center_lon], 
        popup=f"{name} Center",
        icon=folium.Icon(color="red" if "15" in name or "Primary" in name else "orange")
    ).add_to(grp)


def create_fao_soil_visualization(
    center_lat: float,
    center_lon: float,
    primary_ellipse: Optional[Dict] = None,
    fragment_ellipse: Optional[Dict] = None,
    impact_points: Optional[List[Dict]] = None,
    output_path: str = "output/fao_soil_zones.html",
    cache_dir: str = "output/gee_cache",
    use_mock: bool = False,
) -> str:
    """
    Create visualization with FAO soil zone polygons like the paper's 'Картограмма бонитета почв'.
    
    This produces irregular zone polygons colored by bonitet (soil fertility) class:
    - Light blue: 0-5 bonitet (21% of Yu-24 zone - saline soils)
    - Pink: 5.1-10 bonitet (27% - calcisols)
    - Light green: 10.1-15 bonitet (50% - kastanozems)
    - Turquoise: 15.1-20 bonitet (2% - chernozems)
    
    Args:
        center_lat, center_lon: Map center coordinates
        primary_ellipse: Primary stage dispersion ellipse
        fragment_ellipse: Fragment dispersion ellipse  
        impact_points: Monte Carlo impact points
        output_path: Path for output HTML file
        cache_dir: Cache directory for soil data
        use_mock: Force use of mock data (for testing)
        
    Returns:
        Path to created HTML file
    """
    initialize_ee()
    
    # Determine bounding box from ellipses
    if primary_ellipse:
        # Calculate bbox from ellipse extent
        a_km = max(primary_ellipse.get("semi_major_km", 50), 
                   fragment_ellipse.get("semi_major_km", 30) if fragment_ellipse else 30)
        lat_deg = a_km / 111.0
        lon_deg = a_km / (111.0 * math.cos(math.radians(center_lat)))
        
        min_lat = center_lat - lat_deg * 1.2
        max_lat = center_lat + lat_deg * 1.2
        min_lon = center_lon - lon_deg * 1.2
        max_lon = center_lon + lon_deg * 1.2
    else:
        # Default bbox around center (~ 100km)
        min_lat, max_lat = center_lat - 1, center_lat + 1
        min_lon, max_lon = center_lon - 1.5, center_lon + 1.5
    
    bbox = (min_lat, min_lon, max_lat, max_lon)
    
    # Fetch FAO soil zones
    print(f"\n[FAO Soil Zones] Fetching for bbox: {bbox}")
    if use_mock or not HAS_FAO_SOIL:
        from gee.fao_soil_zones import _generate_mock_soil_zones
        soil_data = _generate_mock_soil_zones(bbox)
    else:
        soil_data = fetch_fao_soil_zones(bbox, scale_m=1000, cache_dir=cache_dir)
    
    if not soil_data:
        print("  [WARN] No soil data available")
        return None
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles=None)
    
    # Base layers
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Satellite"
    ).add_to(m)
    folium.TileLayer(tiles="OpenStreetMap", name="Map").add_to(m)
    
    # FAO Soil Zones layer
    soil_group = folium.FeatureGroup(name="Soil Bonitet Zones (FAO)", show=True)
    
    folium.GeoJson(
        soil_data,
        name="Soil Zones",
        style_function=lambda f: {
            'fillColor': f['properties'].get('color', '#CCCCCC'),
            'color': '#333333',
            'weight': 1,
            'fillOpacity': 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['soil_name', 'bonitet', 'stability_class'],
            aliases=['Тип почвы:', 'Бонитет:', 'Устойчивость:'],
            localize=True
        )
    ).add_to(soil_group)
    soil_group.add_to(m)
    
    # Ellipses overlay
    if primary_ellipse or fragment_ellipse:
        ellipse_grp = folium.FeatureGroup(name="Dispersion Ellipses", show=True)
        if primary_ellipse:
            _add_ellipse(ellipse_grp, primary_ellipse, "red", "Primary 3σ")
        if fragment_ellipse:
            _add_ellipse(ellipse_grp, fragment_ellipse, "orange", "Fragments 3σ")
        ellipse_grp.add_to(m)
    
    # Impact heatmap (if points provided)
    if impact_points:
        heat_grp = folium.FeatureGroup(name="Impact Heatmap", show=False)
        pts = [[pt["lat"], pt["lon"]] for pt in impact_points if pt.get("is_fragment")]
        if pts:
            HeatMap(pts, radius=15, blur=10).add_to(heat_grp)
        heat_grp.add_to(m)
    
    # Legend matching paper's style
    legend_html = """
    <div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:15px;border:2px solid grey;border-radius:8px;font-size:11px;max-width:280px;">
    <b style="font-size:14px;">Картограмма бонитета почв</b><br>
    <i>Зона Ю-24 (Soil Bonitet Map)</i>
    <hr style="margin:8px 0;">
    
    <b>Балл бонитета:</b><br>
    <span style="background:#89CFF0;padding:2px 12px;margin:2px;display:inline-block;">от 0 до 5.0</span>
    <span style="font-size:10px;">(S=540 кв.км – 21%)</span><br>
    
    <span style="background:#FFB6C1;padding:2px 12px;margin:2px;display:inline-block;">от 5.1 до 10.0</span>
    <span style="font-size:10px;">(S=628 кв.км – 27%)</span><br>
    
    <span style="background:#90EE90;padding:2px 12px;margin:2px;display:inline-block;">от 10.1 до 15.0</span>
    <span style="font-size:10px;">(S=570 кв.км – 50%)</span><br>
    
    <span style="background:#40E0D0;padding:2px 12px;margin:2px;display:inline-block;">от 15.1 до 20.0</span>
    <span style="font-size:10px;">(S=39 кв.км – 2%)</span>
    
    <hr style="margin:8px 0;">
    <i style="font-size:10px;">Источник: FAO HWSD v2.0<br>
    Масштаб: 1:1,000,000</i>
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Save
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    m.save(output_path)
    print(f"  [SAVED] FAO soil zones map: {output_path}")
    
    return output_path

