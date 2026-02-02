"""
Debug script to compare backend GeoJSON format with frontend expectations.
"""
import json
import sys

print("="*70)
print("NDVI DEBUG: Backend vs Frontend Format Check")
print("="*70)

# 1. Check backend GeoJSON format
print("\n1. Checking backend GeoJSON (run_otu_full.py output)...")
try:
    with open('output/otu/otu_2024-09-09.geojson', 'r') as f:
        # Read first 1000 chars to avoid loading huge file
        content = f.read(1000)
        # Find first feature
        start = content.find('"properties"')
        if start > 0:
            snippet = content[start:start+500]
            print(f"   Sample properties: {snippet[:200]}...")
            
            # Check for key properties
            has_q_vi = '"q_vi"' in snippet
            has_q_ndvi = '"q_ndvi"' in snippet
            has_id = '"id"' in snippet
            has_grid_id = '"grid_id"' in snippet
            
            print(f"\n   Property names found:")
            print(f"     ✅ q_vi: {has_q_vi}")
            print(f"     ❌ q_ndvi: {has_q_ndvi}")
            print(f"     ✅ id: {has_id}")
            print(f"     ❌ grid_id: {has_grid_id}")
except FileNotFoundError:
    print("   ❌ File not found! Run 'py run_otu_full.py' first")
    sys.exit(1)

# 2. Check test GeoJSON
print("\n2. Checking test GeoJSON...")
try:
    with open('output/otu/test_otu.geojson', 'r') as f:
        test_data = json.load(f)
        props = test_data['features'][0]['properties']
        print(f"   Properties: {list(props.keys())}")
        print(f"   Sample values:")
        for key in ['id', 'q_vi', 'q_si', 'q_bi', 'q_relief', 'q_otu']:
            if key in props:
                print(f"     {key}: {props[key]}")
except FileNotFoundError:
    print("   ⚠️  Test file not found")

# 3. Check what frontend expects
print("\n3. Checking frontend TypeScript types...")
try:
    with open('gui/src/types.ts', 'r') as f:
        content = f.read()
        # Find OTUCellProperties
        start = content.find('export interface OTUCellProperties')
        if start > 0:
            end = content.find('}', start)
            interface = content[start:end+1]
            print(f"   {interface}")
except FileNotFoundError:
    print("   ⚠️  types.ts not found")

# 4. Check mock data format
print("\n4. Checking mock data format...")
try:
    with open('gui/src/mockSimulation.ts', 'r') as f:
        content = f.read()
        # Find properties object
        start = content.find('properties: {')
        if start > 0:
            end = content.find('},', start)
            props_block = content[start:end+2]
            print(f"   Mock properties:")
            print(f"   {props_block[:300]}...")
except FileNotFoundError:
    print("   ⚠️  mockSimulation.ts not found")

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)

print("""
If backend uses 'q_vi' but frontend shows N/A, possible causes:

1. ❌ Frontend is using MOCK data (not real backend)
   → Check if "DEMO" badge is shown in header
   → Backend must be running: py run_server.py

2. ❌ API response has different property names
   → Check server_pipeline/simulation.py
   → Check how OTU grid is converted to dict

3. ❌ Frontend TypeScript interface mismatch
   → Check gui/src/types.ts OTUCellProperties
   → Must match backend property names

4. ❌ Popup code uses wrong property names
   → Check gui/src/components/map/LeafletMap.tsx
   → Line ~159: props.q_vi?.toFixed(3)

NEXT STEPS:
1. Start backend: py run_server.py
2. Start frontend: run_frontend.bat
3. Check for "DEMO" badge (should NOT be there)
4. Run simulation and check popup
""")
