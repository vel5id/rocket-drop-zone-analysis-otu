"""Diagnostic script to check what GEE actually returns for NDVI.

This script bypasses the calculator and directly queries GEE to see:
1. How many images are found
2. What bands are available
3. If NDVI calculation works at all
"""
import ee
from datetime import datetime, timedelta

# Initialize GEE
try:
    ee.Initialize(project="qgis-forest-vladimirfominov49")
    print("✅ GEE Initialized")
except:
    ee.Authenticate()
    ee.Initialize(project="qgis-forest-vladimirfominov49")
    print("✅ GEE Authenticated & Initialized")

# Test parameters
target_date = "2024-09-09"
target_dt = datetime.strptime(target_date, "%Y-%m-%d")
window = 14
start_dt = target_dt - timedelta(days=window)
end_dt = target_dt + timedelta(days=window)

# Test point (center of our test area)
test_point = ee.Geometry.Point([66.01, 47.01])
test_region = test_point.buffer(500)

print(f"\n{'='*60}")
print(f"DIAGNOSTIC TEST: {target_date}")
print(f"{'='*60}")
print(f"Date range: {start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}")
print(f"Test point: [66.01, 47.01]")

# Query Sentinel-2
s2 = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(test_region)
    .filterDate(start_dt.strftime("%Y-%m-%d"), end_dt.strftime("%Y-%m-%d"))
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 30))
)

img_count = s2.size().getInfo()
print(f"\n1. Images found: {img_count}")

if img_count == 0:
    print("   ❌ NO IMAGES FOUND!")
    print("   Trying wider window (60 days)...")
    
    start_wide = (target_dt - timedelta(days=60)).strftime("%Y-%m-%d")
    end_wide = (target_dt + timedelta(days=60)).strftime("%Y-%m-%d")
    
    s2_wide = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(test_region)
        .filterDate(start_wide, end_wide)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
    )
    
    img_count_wide = s2_wide.size().getInfo()
    print(f"   Wider window: {img_count_wide} images")
    
    if img_count_wide > 0:
        s2 = s2_wide
        img_count = img_count_wide
    else:
        print("   ❌ STILL NO IMAGES. Region might not be covered by Sentinel-2.")
        exit(1)

# Get first image to check bands
first_img = s2.first()
bands = first_img.bandNames().getInfo()
print(f"\n2. Available bands: {bands}")

if 'B8' not in bands or 'B4' not in bands:
    print("   ❌ B8 or B4 missing! Cannot calculate NDVI.")
    exit(1)

print("   ✅ B8 and B4 present")

# Test 1: No masking
print("\n3. Testing NDVI WITHOUT masking...")
composite_no_mask = s2.median()
ndvi_no_mask = composite_no_mask.normalizedDifference(['B8', 'B4'])

try:
    result_no_mask = ndvi_no_mask.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=test_region,
        scale=30
    ).getInfo()
    
    ndvi_val = result_no_mask.get('nd')
    print(f"   NDVI (no mask): {ndvi_val}")
    
    if ndvi_val is None:
        print("   ❌ NULL even without masking!")
    else:
        print(f"   ✅ Got value: {ndvi_val:.4f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: With SCL masking (relaxed)
print("\n4. Testing NDVI WITH relaxed SCL mask...")

def mask_clouds_relaxed(image):
    scl = image.select("SCL")
    mask = scl.eq(3).Or(scl.eq(4)).Or(scl.eq(5)).Or(scl.eq(6)).Or(scl.eq(7))
    return image.updateMask(mask)

s2_masked = s2.map(mask_clouds_relaxed)
composite_masked = s2_masked.median()
ndvi_masked = composite_masked.normalizedDifference(['B8', 'B4'])

try:
    result_masked = ndvi_masked.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=test_region,
        scale=30
    ).getInfo()
    
    ndvi_val_masked = result_masked.get('nd')
    print(f"   NDVI (with mask): {ndvi_val_masked}")
    
    if ndvi_val_masked is None:
        print("   ❌ NULL with masking! Mask is removing all data.")
    else:
        print(f"   ✅ Got value: {ndvi_val_masked:.4f}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check SCL distribution
print("\n5. Checking SCL class distribution...")
try:
    scl_img = s2.first().select('SCL')
    scl_stats = scl_img.reduceRegion(
        reducer=ee.Reducer.frequencyHistogram(),
        geometry=test_region,
        scale=30
    ).getInfo()
    
    print(f"   SCL classes present: {scl_stats.get('SCL', {})}")
except Exception as e:
    print(f"   ⚠️  Could not get SCL stats: {e}")

print(f"\n{'='*60}")
print("DIAGNOSTIC COMPLETE")
print(f"{'='*60}")
