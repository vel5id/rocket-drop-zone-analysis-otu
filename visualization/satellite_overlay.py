"""Satellite visualization with multi-index GeoJSON layers."""
from __future__ import annotations
import os, math, folium, json
from folium.plugins import HeatMap
import numpy as np
from typing import List, Dict, Any, Optional

try:
    from gee.authenticator import initialize_ee
except: 
    def initialize_ee(): pass


# Color schemes for different indices
def _get_otu_color(val):
    """OTU: Green (stable) -> Red (unstable)"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    if val < 0.25: return '#ff0000'
    if val < 0.50: return '#ff8800'
    if val < 0.75: return '#88ff00'
    return '#00aa00'

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
    """Aspect: North=Blue, East=Yellow, South=Red, West=Green"""
    if val is None or (isinstance(val, float) and np.isnan(val)): return None
    # 0/360=N, 90=E, 180=S, 270=W
    if val < 45 or val >= 315: return '#0088ff'   # North - blue
    if val < 135: return '#ffcc00'                 # East - yellow  
    if val < 225: return '#ff4400'                 # South - red
    return '#00aa44'                               # West - green


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
):
    """Create interactive map with 7 switchable index layers."""
    initialize_ee()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles=None)
    
    # Base layers
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Esri", name="Satellite"
    ).add_to(m)
    folium.TileLayer(tiles="OpenStreetMap", name="Map").add_to(m)
    
    # Ellipses
    ellipse_grp = folium.FeatureGroup(name="Ellipses", show=True)
    if primary_ellipse: _add_ellipse(ellipse_grp, primary_ellipse, "red", "Primary")
    if fragment_ellipse: _add_ellipse(ellipse_grp, fragment_ellipse, "orange", "Fragments")
    ellipse_grp.add_to(m)
    
    # Impact heatmap
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
        # Layer definitions: (name, property, color_func, show_by_default)
        layers = [
            ("1. OTU Index", "q_otu", _get_otu_color, True),
            ("2. NDVI", "q_ndvi", _get_ndvi_color, False),
            ("3. Soil Strength (Q_Si)", "q_si", _get_soil_strength_color, False),
            ("4. Soil Quality (Q_Bi)", "q_bi", _get_soil_quality_color, False),
            ("5. Relief (Q_Relief)", "q_relief", _get_relief_color, False),
            ("6. Fire Risk", "q_fire", _get_fire_risk_color, False),
            ("7. Slope", "slope", _get_slope_color, False),
            ("8. Aspect", "aspect", _get_aspect_color, False),
        ]
        
        for layer_name, prop_name, color_func, show in layers:
            # Check if property exists in data
            if geojson_data["features"] and prop_name not in geojson_data["features"][0].get("properties", {}):
                continue
            
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
    <b style="font-size:14px;">Aspect (Exposure)</b><br><br>
    <span style="background:#0088ff;color:white;padding:2px 8px;margin:2px;">North (N)</span><br>
    <span style="background:#ffcc00;padding:2px 8px;margin:2px;">East (E)</span><br>
    <span style="background:#ff4400;color:white;padding:2px 8px;margin:2px;">South (S)</span><br>
    <span style="background:#00aa44;color:white;padding:2px 8px;margin:2px;">West (W)</span>
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
) -> List[str]:
    """Create separate HTML files for each index visualization.
    
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
        
        # Ellipses
        ellipse_grp = folium.FeatureGroup(name="Ellipses", show=True)
        if primary_ellipse: _add_ellipse(ellipse_grp, primary_ellipse, "red", "Primary")
        if fragment_ellipse: _add_ellipse(ellipse_grp, fragment_ellipse, "orange", "Fragments")
        ellipse_grp.add_to(m)
        
        # Impact heatmap
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
