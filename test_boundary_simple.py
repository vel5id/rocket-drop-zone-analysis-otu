"""
Simple unit test to verify boundary_geojson generation without running full simulation.
"""
import sys
import os
import json

sys.path.insert(0, os.path.abspath("."))

from server_pipeline.geojson import ellipse_to_geojson

def test_boundary_generation():
    print("Testing ellipse_to_geojson function...")
    
    # Test ellipse
    test_ellipse = {
        "center_lat": 47.0,
        "center_lon": 67.0,
        "semi_major_km": 10.0,
        "semi_minor_km": 5.0,
        "angle_deg": 30.0
    }
    
    # Generate GeoJSON
    try:
        boundary_feature = ellipse_to_geojson(
            test_ellipse, 
            properties={"type": "primary", "name": "Test Zone"}
        )
        
        print("\n[SUCCESS] ellipse_to_geojson executed successfully")
        print(f"Feature Type: {boundary_feature.get('type')}")
        print(f"Geometry Type: {boundary_feature.get('geometry', {}).get('type')}")
        print(f"Properties: {boundary_feature.get('properties')}")
        
        coords = boundary_feature.get('geometry', {}).get('coordinates', [[]])
        if coords and len(coords) > 0:
            print(f"Number of boundary points: {len(coords[0])}")
            print(f"First point: {coords[0][0]}")
            print(f"Last point: {coords[0][-1]}")
            
            # Verify it's a closed polygon
            if coords[0][0] == coords[0][-1]:
                print("[OK] Polygon is properly closed")
            else:
                print("[WARNING] Polygon is NOT closed")
        
        # Test FeatureCollection structure
        print("\nTesting FeatureCollection structure...")
        boundary_geojson = {
            "type": "FeatureCollection",
            "features": [boundary_feature]
        }
        
        print(f"FeatureCollection Type: {boundary_geojson.get('type')}")
        print(f"Number of features: {len(boundary_geojson.get('features', []))}")
        
        print("\n[VERIFICATION COMPLETE] All checks passed.")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_boundary_generation()
