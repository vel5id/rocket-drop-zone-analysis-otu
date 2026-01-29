"""Generate lightweight OTU visualization using GeoJSON."""
import sys
sys.path.insert(0, '.')
import folium
import json

# Load OTU data
with open('output/otu/otu_2024-09-09.geojson', 'r') as f:
    otu_data = json.load(f)

# Get center
features = otu_data['features']
if features:
    coords = features[len(features)//2]['geometry']['coordinates'][0]
    center = [sum(c[1] for c in coords)/len(coords), sum(c[0] for c in coords)/len(coords)]
else:
    center = [47.0, 66.5]

print(f"Center: {center}")
print(f"Features: {len(features)}")

# Create map
m = folium.Map(location=center, zoom_start=7, tiles='OpenStreetMap')

# Satellite layer
folium.TileLayer(
    tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attr="Esri",
    name="Satellite"
).add_to(m)

# Color function
def get_color(val):
    if val is None: return '#808080'
    if val < 0.25: return '#ff0000'
    if val < 0.50: return '#ff8800'
    if val < 0.75: return '#88ff00'
    return '#00aa00'

# Add OTU layer as GeoJSON (much faster than individual rectangles!)
folium.GeoJson(
    otu_data,
    name="OTU Index",
    style_function=lambda f: {
        'fillColor': get_color(f['properties'].get('q_otu')),
        'color': 'none',
        'fillOpacity': 0.7,
        'weight': 0
    },
    tooltip=folium.GeoJsonTooltip(
        fields=['q_otu', 'q_ndvi', 'q_si', 'q_bi', 'q_relief'],
        aliases=['OTU:', 'NDVI:', 'Soil Strength:', 'Soil Quality:', 'Relief:'],
        localize=True
    )
).add_to(m)

# Legend HTML
legend_html = """
<div style="position:fixed;bottom:50px;left:50px;z-index:1000;background:white;padding:12px;border:2px solid grey;border-radius:8px;font-size:11px;">
<b style="font-size:13px;">OTU Classification</b>
<table style="margin-top:8px;border-collapse:collapse;width:100%;">
<tr style="background:#f0f0f0;"><th style="padding:4px;border:1px solid #ccc;">Range</th><th style="padding:4px;border:1px solid #ccc;">Class</th><th style="padding:4px;border:1px solid #ccc;">Color</th></tr>
<tr><td style="padding:4px;border:1px solid #ccc;">0.75-1.0</td><td style="padding:4px;border:1px solid #ccc;">High Stability</td><td style="padding:4px;border:1px solid #ccc;background:#00aa00;"></td></tr>
<tr><td style="padding:4px;border:1px solid #ccc;">0.50-0.75</td><td style="padding:4px;border:1px solid #ccc;">Moderate</td><td style="padding:4px;border:1px solid #ccc;background:#88ff00;"></td></tr>
<tr><td style="padding:4px;border:1px solid #ccc;">0.25-0.50</td><td style="padding:4px;border:1px solid #ccc;">Low</td><td style="padding:4px;border:1px solid #ccc;background:#ff8800;"></td></tr>
<tr><td style="padding:4px;border:1px solid #ccc;">0.0-0.25</td><td style="padding:4px;border:1px solid #ccc;">Unstable</td><td style="padding:4px;border:1px solid #ccc;background:#ff0000;"></td></tr>
</table>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Layer control
folium.LayerControl().add_to(m)

# Save
m.save('output/otu_simple.html')
print('Saved: output/otu_simple.html')

import os
size_mb = os.path.getsize('output/otu_simple.html') / (1024*1024)
print(f'File size: {size_mb:.1f} MB')
