import sys
import os

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting import test...")

try:
    print("Importing run_pipeline...")
    from run_pipeline import run_simulation_gpu, run_simulation_standard, compute_ellipse_from_geo
    print("run_pipeline imported successfully.")

    print("Importing grid.polygon_grid...")
    from grid.polygon_grid import create_ellipse_polygon, generate_grid_in_polygons
    print("grid.polygon_grid imported successfully.")

except Exception as e:
    print(f"IMPORT ERROR: {e}")
    import traceback
    traceback.print_exc()
