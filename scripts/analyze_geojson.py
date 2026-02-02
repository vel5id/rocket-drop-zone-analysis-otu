import json
import numpy as np
import sys
from collections import Counter
from pathlib import Path

def analyze_geojson(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"Error: File {file_path} not found.")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    features = data.get('features', [])
    total_features = len(features)
    print(f"Total Features: {total_features}")

    if total_features == 0:
        return

    # Properties to analyze
    props_to_check = ['q_otu', 'q_vi', 'q_si', 'q_bi', 'q_relief']
    missing_data_counts = Counter()
    chunks_with_missing_data = 0
    
    values = {prop: [] for prop in props_to_check}
    
    for feat in features:
        props = feat.get('properties', {})
        
        # Check missing_data
        missing = props.get('missing_data', [])
        # Handle string representation if it was saved as string, usually it's list
        if isinstance(missing, str):
             # Try to parse if it looks like a list string "['ndvi']"
             if missing.startswith('[') and missing.endswith(']'):
                 try:
                     missing = eval(missing)
                 except:
                     pass
        
        if missing and isinstance(missing, list) and len(missing) > 0:
            chunks_with_missing_data += 1
            missing_data_counts.update(missing)
            
        for prop in props_to_check:
            val = props.get(prop)
            values[prop].append(val)

    print("\n--- Statistics ---")
    for prop in props_to_check:
        arr = values[prop]
        valid_arr = [x for x in arr if x is not None and not (isinstance(x, float) and np.isnan(x))]
        none_count = len(arr) - len(valid_arr)
        
        if valid_arr:
            np_arr = np.array(valid_arr, dtype=float)
            print(f"{prop}: Min={np.min(np_arr):.4f}, Max={np.max(np_arr):.4f}, Mean={np.mean(np_arr):.4f}, NaNs/Nones={none_count}")
        else:
            print(f"{prop}: ALL Invalid/None")

    print("\n--- Missing Data Analysis ---")
    if chunks_with_missing_data > 0:
        print(f"Chunks with missing data flags: {chunks_with_missing_data} / {total_features}")
        print("Missing components breakdown:", dict(missing_data_counts))
    else:
        print("No missing data flags found on any chunk.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_geojson(sys.argv[1])
    else:
        print("Usage: analyze_geojson.py <path_to_geojson>")
