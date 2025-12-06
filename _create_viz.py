# Script to create satellite_overlay.py
code = '''"""Satellite visualization with correct ellipse orientation."""
from __future__ import annotations
import os, math, folium
from folium.plugins import HeatMap
import numpy as np
from typing import List, Dict, Any

try:
    from gee.authenticator import initialize_ee
except: 
    def initialize_ee(): pass

def create_impact_visualization(center_lat, center_lon, primary_ellipse, fragment_ellipse, impact_points, grid_cells=None, output_path="output/impact_visualization.html", satellite_date="2023-07-15", buffer_km=100):
    initialize_ee()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=8, tiles=None)
    folium.TileLayer(tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", attr="Esri", name="Satellite").add_to(m)
    folium.TileLayer(tiles="OpenStreetMap", name="Map").add_to(m)
    
    primary_grp = folium.FeatureGroup(name="Primary", show=True)
    frag_grp = folium.FeatureGroup(name="Fragments", show=False)
    ellipse_grp = folium.FeatureGroup(name="Ellipses", show=True)
    grid_grp = folium.FeatureGroup(name="Grid", show=True)
    heat_grp = folium.FeatureGroup(name="Heatmap", show=True)
    
    if primary_ellipse: _add_ellipse(ellipse_grp, primary_ellipse, "red", "Primary")
    if fragment_ellipse: _add_ellipse(ellipse_grp, fragment_ellipse, "orange", "Fragments")
    
    frag_pts = []
    for pt in impact_points:
        if pt.get("is_fragment"):
            frag_pts.append([pt["lat"], pt["lon"]])
            folium.CircleMarker([pt["lat"], pt["lon"]], radius=2, color="orange", fill=True).add_to(frag_grp)
        else:
            folium.CircleMarker([pt["lat"], pt["lon"]], radius=4, color="red", fill=True, fillOpacity=0.8).add_to(primary_grp)
    
    if frag_pts: HeatMap(frag_pts, radius=15, blur=10).add_to(heat_grp)
    if grid_cells:
        for c in grid_cells: folium.Rectangle([[c.min_lat, c.min_lon], [c.max_lat, c.max_lon]], color="cyan", weight=1, fill=False).add_to(grid_grp)
    
    for g in [primary_grp, frag_grp, ellipse_grp, grid_grp, heat_grp]: g.add_to(m)
    folium.LayerControl().add_to(m)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    m.save(output_path)
    return output_path

def _add_ellipse(grp, ellipse, color, name, npts=64):
    """Add ellipse. angle_deg is from NORTH (0=N, 45=NE, 90=E)."""
    clat, clon = ellipse["center_lat"], ellipse["center_lon"]
    a_km, b_km = ellipse["semi_major_km"], ellipse["semi_minor_km"]
    angle_north = ellipse.get("angle_deg", 0)
    
    lat_rad = math.radians(clat)
    deg_lat = 1/111.0
    deg_lon = 1/(111.0 * math.cos(lat_rad))
    
    # Convert from North to math angle (East=0, CCW)
    math_angle = math.radians(90 - angle_north)
    
    coords = []
    for t in np.linspace(0, 2*np.pi, npts):
        x = a_km * deg_lon * np.cos(t)
        y = b_km * deg_lat * np.sin(t)
        xr = x * np.cos(math_angle) - y * np.sin(math_angle)
        yr = x * np.sin(math_angle) + y * np.cos(math_angle)
        coords.append([clat + yr, clon + xr])
    
    popup_text = name + ": " + str(round(a_km, 1)) + "x" + str(round(b_km, 1)) + "km"
    folium.Polygon(coords, color=color, weight=3, fill=False, popup=popup_text).add_to(grp)
    folium.Marker([clat, clon], popup=name + " Center", 
                  icon=folium.Icon(color="red" if "Primary" in name else "orange")).add_to(grp)
'''

import os
os.makedirs('visualization', exist_ok=True)
with open('visualization/satellite_overlay.py', 'w', encoding='utf-8') as f:
    f.write(code)
print('satellite_overlay.py created successfully')
