"""
Quick test script for FAO soil zones visualization.
Generates a map with soil zones similar to the paper's 'Картограмма бонитета почв'.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from visualization.satellite_overlay import create_fao_soil_visualization

# Test with mock data (no GEE required)
if __name__ == "__main__":
    print("Testing FAO Soil Zones Visualization...")
    
    # Sample ellipse data (like from Monte Carlo simulation)
    primary_ellipse = {
        "center_lat": 46.8,
        "center_lon": 66.5,
        "semi_major_km": 42.0,
        "semi_minor_km": 28.0,
        "angle_deg": 45.0,
    }
    
    fragment_ellipse = {
        "center_lat": 46.5,
        "center_lon": 65.8,
        "semi_major_km": 35.0,
        "semi_minor_km": 22.0,
        "angle_deg": 48.0,
    }
    
    output_path = create_fao_soil_visualization(
        center_lat=46.6,
        center_lon=66.0,
        primary_ellipse=primary_ellipse,
        fragment_ellipse=fragment_ellipse,
        output_path="output/fao_soil_zones_test.html",
        use_mock=True,  # Use mock data for quick test
    )
    
    if output_path:
        print(f"\n✅ Success! Open in browser: {output_path}")
    else:
        print("\n❌ Failed to create visualization")
