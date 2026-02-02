import json

# Load and check first feature
with open('output/otu/otu_2024-09-09.geojson', 'r') as f:
    data = json.load(f)

print("="*70)
print("GeoJSON Format Check")
print("="*70)

feature = data['features'][0]
props = feature['properties']

print("\nProperties in GeoJSON:")
for key in sorted(props.keys()):
    val = props[key]
    if isinstance(val, float):
        print(f"  {key}: {val:.4f}")
    else:
        print(f"  {key}: {val}")

print("\n" + "="*70)
print("Expected by Frontend:")
print("="*70)
print("  id: string")
print("  q_vi: number (NDVI)")
print("  q_si: number (Soil Strength)")
print("  q_bi: number (Soil Quality)")
print("  q_relief: number (Relief)")
print("  q_otu: number (OTU Index)")
print("  missing_data: array")

print("\n" + "="*70)
print("Comparison:")
print("="*70)

required = ['id', 'q_vi', 'q_si', 'q_bi', 'q_relief', 'q_otu', 'missing_data']
for key in required:
    if key in props:
        print(f"  ✅ {key}: {type(props[key]).__name__}")
    else:
        print(f"  ❌ {key}: MISSING")
