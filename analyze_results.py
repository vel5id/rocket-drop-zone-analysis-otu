"""Analyze the results from the full OTU calculation."""
import json
import sys

# Load results
with open('output/otu/otu_2024-09-09.geojson', 'r') as f:
    data = json.load(f)

features = data['features']
total = len(features)

print("="*70)
print(f"OTU CALCULATION RESULTS ANALYSIS ({total} chunks)")
print("="*70)

# Extract values
q_vi_values = [f['properties']['q_vi'] for f in features]
q_otu_values = [f['properties']['q_otu'] for f in features]
missing_data_counts = {'ndvi': 0, 'soil': 0, 'relief': 0}

for f in features:
    missing = f['properties'].get('missing_data', [])
    if isinstance(missing, str):
        # Handle string representation
        missing = eval(missing) if missing.startswith('[') else []
    for item in missing:
        if item in missing_data_counts:
            missing_data_counts[item] += 1

# NDVI Statistics
ndvi_valid = [v for v in q_vi_values if v > 0]
print(f"\nNDVI Statistics:")
print(f"  Valid chunks:  {len(ndvi_valid)}/{total} ({100*len(ndvi_valid)/total:.1f}%)")
if ndvi_valid:
    print(f"  Min:   {min(ndvi_valid):.4f}")
    print(f"  Max:   {max(ndvi_valid):.4f}")
    print(f"  Mean:  {sum(ndvi_valid)/len(ndvi_valid):.4f}")

# OTU Statistics
print(f"\nOTU Statistics:")
print(f"  Min:   {min(q_otu_values):.4f}")
print(f"  Max:   {max(q_otu_values):.4f}")
print(f"  Mean:  {sum(q_otu_values)/total:.4f}")

# Missing Data
print(f"\nMissing Data:")
print(f"  NDVI:   {missing_data_counts['ndvi']}/{total} ({100*missing_data_counts['ndvi']/total:.1f}%)")
print(f"  Soil:   {missing_data_counts['soil']}/{total} ({100*missing_data_counts['soil']/total:.1f}%)")
print(f"  Relief: {missing_data_counts['relief']}/{total} ({100*missing_data_counts['relief']/total:.1f}%)")

# Success criteria
print(f"\n" + "="*70)
if len(ndvi_valid) > total * 0.9:
    print("✅ EXCELLENT: >90% chunks have valid NDVI data")
elif len(ndvi_valid) > total * 0.7:
    print("✅ GOOD: >70% chunks have valid NDVI data")
else:
    print(f"⚠️  WARNING: Only {100*len(ndvi_valid)/total:.1f}% chunks have valid NDVI")

print(f"\nOutput file: output/otu/otu_2024-09-09.geojson")
print(f"Total size: {total} chunks processed successfully")
print("="*70)
