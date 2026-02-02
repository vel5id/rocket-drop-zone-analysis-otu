"""Test what property names reduceRegions returns for relief data (slope + water)."""
import ee

ee.Initialize(project="qgis-forest-vladimirfominov49")

test_point = ee.Geometry.Point([66.01, 47.01])
test_region = test_point.buffer(500)

print("Testing Relief data property names...")

# Load relief data
dem = ee.Image("USGS/SRTMGL1_003")
slope = ee.Terrain.products(dem).select("slope")
water = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")

# Combine
combined = slope.addBands(water)

print(f"\nBand names in combined image: {combined.bandNames().getInfo()}")

# Create test feature
fc = ee.FeatureCollection([
    ee.Feature(test_region, {'chunk_id': 'test_001'})
])

# Reduce
reduced = combined.reduceRegions(
    collection=fc,
    reducer=ee.Reducer.mean(),
    scale=30,
)

result = reduced.getInfo()
props = result['features'][0]['properties']

print(f"\nProperties returned by reduceRegions:")
for key, val in props.items():
    if key != 'chunk_id':
        print(f"  {key}: {val}")

print("\n✅ Use these property names in calculator.py!")
