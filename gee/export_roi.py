import os
import geemap
import ee

# Known GEE project ID for this workflow
PROJECT_ID = "qgis-forest-vladimirfominov49"

def initialize_ee():
    """Initialize Earth Engine, authenticating if necessary, using the known project ID."""
    try:
        ee.Initialize(project=PROJECT_ID)
        print(f"Earth Engine initialized with project {PROJECT_ID}")
    except Exception as e:
        print("Earth Engine not initialized or authentication required. Attempting authentication...")
        try:
            ee.Authenticate()
            ee.Initialize(project=PROJECT_ID)
            print(f"Authenticated and initialized Earth Engine with project {PROJECT_ID}")
        except Exception as auth_err:
            raise RuntimeError(f"Failed to authenticate Earth Engine: {auth_err}") from e

# Ensure data directory exists (relative to this script)
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
if not os.path.isdir(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

# Path to the GeoJSON defining the region of interest
geojson_path = os.path.join(DATA_DIR, "burned_roi.geojson")
if not os.path.isfile(geojson_path):
    # Create a minimal dummy GeoJSON if the file is missing (for testing purposes)
    dummy_geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [63.3, 45.7],
                            [63.4, 45.7],
                            [63.4, 45.8],
                            [63.3, 45.8],
                            [63.3, 45.7]
                        ]
                    ]
                }
            }
        ]
    }
    import json
    with open(geojson_path, "w", encoding="utf-8") as f:
        json.dump(dummy_geojson, f, ensure_ascii=False, indent=2)
    print(f"Created dummy GeoJSON at {geojson_path}")

# Main execution
if __name__ == "__main__":
    initialize_ee()
    # Convert the GeoJSON to an Earth Engine FeatureCollection
    ee_object = geemap.geojson_to_ee(geojson_path)

    # Define the export task to an asset in the known project
    export_task = ee.batch.Export.table.toAsset(
        collection=ee_object,
        description="testassets",
        assetId=f"projects/{PROJECT_ID}/assets/burned_roi"
    )
    export_task.start()
    print("Export task started: testassets ->", f"projects/{PROJECT_ID}/assets/burned_roi")
