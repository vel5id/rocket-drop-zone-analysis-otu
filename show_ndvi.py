"""Show NDVI values from the generated GeoJSON."""
import json

with open('output/otu/otu_2024-09-09.geojson', 'r') as f:
    data = json.load(f)

print("NDVI Values for test chunks:")
print("="*50)

for i, feat in enumerate(data['features'][:6]):
    props = feat['properties']
    chunk_id = props['id']
    q_vi = props['q_vi']
    q_otu = props['q_otu']
    missing = props.get('missing_data', [])
    
    status = "❌ MISSING" if "ndvi" in missing else "✅ OK"
    
    print(f"{chunk_id}: NDVI={q_vi:.4f}, OTU={q_otu:.3f} {status}")

print("="*50)
print(f"\nTotal chunks in file: {len(data['features'])}")
