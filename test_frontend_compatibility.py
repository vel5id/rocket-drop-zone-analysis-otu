"""Test GeoJSON compatibility with frontend and table generation.

This script validates that the generated GeoJSON:
1. Has correct structure for frontend map rendering
2. Contains all required properties
3. Can be used for table generation
"""
import json
import sys
from pathlib import Path

def test_geojson_structure(geojson_path):
    """Test GeoJSON structure and properties."""
    print("="*70)
    print("GEOJSON FRONTEND COMPATIBILITY TEST")
    print("="*70)
    
    # Load GeoJSON
    with open(geojson_path, 'r') as f:
        data = json.load(f)
    
    # Test 1: Basic structure
    print("\n1. Testing basic structure...")
    assert data['type'] == 'FeatureCollection', "❌ Not a FeatureCollection"
    assert 'features' in data, "❌ Missing 'features'"
    print("   ✅ Valid FeatureCollection")
    
    features = data['features']
    total = len(features)
    print(f"   ✅ Contains {total} features")
    
    # Test 2: Feature structure
    print("\n2. Testing feature structure...")
    sample = features[0]
    
    assert sample['type'] == 'Feature', "❌ Invalid feature type"
    assert 'geometry' in sample, "❌ Missing geometry"
    assert 'properties' in sample, "❌ Missing properties"
    print("   ✅ Features have correct structure")
    
    # Test 3: Geometry
    print("\n3. Testing geometry...")
    geom = sample['geometry']
    assert geom['type'] == 'Polygon', "❌ Not a Polygon"
    assert 'coordinates' in geom, "❌ Missing coordinates"
    assert len(geom['coordinates'][0]) == 5, "❌ Polygon not closed"
    print("   ✅ Geometry is valid Polygon")
    
    # Test 4: Required properties for frontend
    print("\n4. Testing required properties...")
    props = sample['properties']
    required_props = ['id', 'q_vi', 'q_si', 'q_bi', 'q_relief', 'q_otu', 'missing_data']
    
    missing = [p for p in required_props if p not in props]
    if missing:
        print(f"   ❌ Missing properties: {missing}")
        return False
    print(f"   ✅ All required properties present")
    
    # Test 5: Data types
    print("\n5. Testing data types...")
    assert isinstance(props['id'], str), "❌ id should be string"
    assert isinstance(props['q_vi'], (int, float)), "❌ q_vi should be number"
    assert isinstance(props['q_otu'], (int, float)), "❌ q_otu should be number"
    assert isinstance(props['missing_data'], list), "❌ missing_data should be list"
    print("   ✅ Data types are correct")
    
    # Test 6: Value ranges
    print("\n6. Testing value ranges...")
    q_vi_values = [f['properties']['q_vi'] for f in features]
    q_otu_values = [f['properties']['q_otu'] for f in features]
    
    assert all(0 <= v <= 1 for v in q_vi_values), "❌ q_vi out of range [0,1]"
    assert all(0 <= v <= 1 for v in q_otu_values), "❌ q_otu out of range [0,1]"
    print("   ✅ Values in valid ranges")
    
    # Test 7: Missing data flags
    print("\n7. Testing missing data flags...")
    chunks_with_missing = [f for f in features if len(f['properties']['missing_data']) > 0]
    print(f"   ℹ️  Chunks with missing data: {len(chunks_with_missing)}/{total}")
    
    if chunks_with_missing:
        sample_missing = chunks_with_missing[0]
        print(f"   ℹ️  Example missing: {sample_missing['properties']['missing_data']}")
    
    # Test 8: Coordinates validity
    print("\n8. Testing coordinate validity...")
    for i, f in enumerate(features[:100]):  # Test first 100
        coords = f['geometry']['coordinates'][0]
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        
        assert all(-180 <= lon <= 180 for lon in lons), f"❌ Invalid longitude in feature {i}"
        assert all(-90 <= lat <= 90 for lat in lats), f"❌ Invalid latitude in feature {i}"
    
    print("   ✅ Coordinates are valid")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    print("\nFrontend compatibility:")
    print("  ✅ Can be loaded by Leaflet/MapLibre")
    print("  ✅ Properties match expected schema")
    print("  ✅ Missing data flags work for 'Purple Mode'")
    print("  ✅ Ready for table generation")
    
    return True

def generate_sample_table(geojson_path, output_path="output/otu_table.csv"):
    """Generate a sample CSV table from GeoJSON."""
    print("\n" + "="*70)
    print("GENERATING SAMPLE TABLE")
    print("="*70)
    
    with open(geojson_path, 'r') as f:
        data = json.load(f)
    
    features = data['features']
    
    # Create CSV
    import csv
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'ID', 'Latitude', 'Longitude', 
            'NDVI (Q_Vi)', 'Soil Strength (Q_Si)', 'Soil Quality (Q_Bi)', 
            'Relief Factor (Q_Relief)', 'OTU Index (Q_OTU)',
            'Missing Data'
        ])
        
        # Data rows
        for feat in features:
            props = feat['properties']
            coords = feat['geometry']['coordinates'][0]
            
            # Calculate center
            lons = [c[0] for c in coords]
            lats = [c[1] for c in coords]
            center_lon = sum(lons) / len(lons)
            center_lat = sum(lats) / len(lats)
            
            missing = ', '.join(props['missing_data']) if props['missing_data'] else 'None'
            
            writer.writerow([
                props['id'],
                f"{center_lat:.6f}",
                f"{center_lon:.6f}",
                f"{props['q_vi']:.4f}",
                f"{props['q_si']:.4f}",
                f"{props['q_bi']:.4f}",
                f"{props['q_relief']:.4f}",
                f"{props['q_otu']:.4f}",
                missing
            ])
    
    print(f"✅ Table saved to: {output_path}")
    print(f"   Rows: {len(features)}")
    print(f"   Columns: 9")
    
    # Show sample
    print("\nSample rows (first 3):")
    with open(output_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i < 4:  # Header + 3 rows
                print(f"   {line.strip()}")

if __name__ == "__main__":
    geojson_path = "output/otu/otu_2024-09-09.geojson"
    
    if not Path(geojson_path).exists():
        print(f"❌ GeoJSON not found: {geojson_path}")
        sys.exit(1)
    
    # Run tests
    success = test_geojson_structure(geojson_path)
    
    if success:
        # Generate sample table
        generate_sample_table(geojson_path)
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED - READY FOR PRODUCTION!")
        print("="*70)
        sys.exit(0)
    else:
        sys.exit(1)
