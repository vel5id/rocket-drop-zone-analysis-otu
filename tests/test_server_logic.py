
import sys
import os
import threading
import time
import traceback

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print(f"Current CWD: {os.getcwd()}")
sys.path.insert(0, os.getcwd())
print(f"Sys Path: {sys.path[:3]}")

try:
    print("Attempting import of server_pipeline.simulation...")
    from server_pipeline.simulation import run_simulation_safe
    print("Import SUCCESS.")
except ImportError as e:
    print(f"Import FAILED: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error during import: {e}")
    traceback.print_exc()
    sys.exit(1)

def progress_callback(pct, msg):
    print(f"CB: [{pct}%] {msg}", flush=True)

print("Starting simulation test execution...")
try:
    start = time.time()
    result = run_simulation_safe(
        iterations=10, 
        use_gpu=False, 
        progress_callback=progress_callback
    )
    print(f"Simulation completed in {time.time() - start:.2f}s")
    if result:
        print(f"Result stats: {result.stats}")
    else:
        print("Result is None!")
except Exception as e:
    print(f"Simulation execution CRASHED: {e}")
    traceback.print_exc()

print("Test script finished.")
