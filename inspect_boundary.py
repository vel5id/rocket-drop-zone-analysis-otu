
import sys
import os
import json

# Add parent dir
sys.path.insert(0, os.path.abspath("."))

from server_pipeline.simulation import run_simulation_safe

def verify_boundary():
    print("Running minimal simulation to verify boundary output...")
    # Run with small iterations and no GPU to be fast
    result = run_simulation_safe(
        iterations=10, 
        use_gpu=False,
        # Using zone preset for deterministic fast run
        zone_id="yu24_15", 
        progress_callback=lambda p, m: print(f"[{p}%] {m}")
    )
    
    result_dict = result.to_dict()
    
    if "boundaries" in result_dict:
        print("\n[SUCCESS] 'boundaries' key found in result.")
        boundaries = result_dict["boundaries"]
        print(f"Type: {type(boundaries)}")
        print(f"GeoJSON Type: {boundaries.get('type')}")
        print(f"Features: {len(boundaries.get('features', []))}")
        
        if boundaries.get('features'):
            print("First Feature Properties:", boundaries['features'][0].get('properties'))
    else:
        print("\n[FAIL] 'boundaries' key NOT found in result.")
        print("Keys present:", list(result_dict.keys()))

if __name__ == "__main__":
    verify_boundary()
