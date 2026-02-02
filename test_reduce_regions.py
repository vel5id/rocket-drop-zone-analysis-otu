"""Test reduceRegions to see what property names are returned."""
import ee

ee.Initialize(project="qgis-forest-vladimirfominov49")

from datetime import datetime, timedelta

target_date = "2024-09-09"
target_dt = datetime.strptime(target_date, "%Y-%m-%d")
window = 14
start_dt = target_dt - timedelta(days=window)
end_dt = target_dt + timedelta(days=window)

# Test point
test_point = ee.Geometry.Point([66.01, 47.01])
test_region = test_point.buffer(500)

print("Testing reduceRegions property names...")

# Query S2
s2 = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(test_region)
    .filterDate(start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"))
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
)

# Mask
def mask_clouds(image):
    scl = image.select("SCL")
    mask = scl.eq(3).Or(scl.eq(4)).Or(scl.eq(5)).Or(scl.eq(6)).Or(scl.eq(7))
    return image.updateMask(mask)

s2_masked = s2.map(mask_clouds)
composite = s2_masked.median()

# Test 1: With .rename("NDVI")
print("\n1. Testing with .rename('NDVI')...")
ndvi_renamed = composite.normalizedDifference(['B8', 'B4']).rename("NDVI")

fc = ee.FeatureCollection([
    ee.Feature(test_region, {'chunk_id': 'test_001'})
])

reduced_renamed = ndvi_renamed.reduceRegions(
    collection=fc,
    reducer=ee.Reducer.mean(),
    scale=30,
    tileScale=4
)

result_renamed = reduced_renamed.getInfo()
print(f"   Properties: {result_renamed['features'][0]['properties']}")

# Test 2: Without rename
print("\n2. Testing WITHOUT rename...")
ndvi_no_rename = composite.normalizedDifference(['B8', 'B4'])

reduced_no_rename = ndvi_no_rename.reduceRegions(
    collection=fc,
    reducer=ee.Reducer.mean(),
    scale=30,
    tileScale=4
)

result_no_rename = reduced_no_rename.getInfo()
print(f"   Properties: {result_no_rename['features'][0]['properties']}")

# Test 3: With unmask(0.0)
print("\n3. Testing with .unmask(0.0)...")
ndvi_unmasked = composite.normalizedDifference(['B8', 'B4']).rename("NDVI").unmask(0.0)

reduced_unmasked = ndvi_unmasked.reduceRegions(
    collection=fc,
    reducer=ee.Reducer.mean(),
    scale=30,
    tileScale=4
)

result_unmasked = reduced_unmasked.getInfo()
print(f"   Properties: {result_unmasked['features'][0]['properties']}")

print("\n✅ Check which property name contains the NDVI value!")
