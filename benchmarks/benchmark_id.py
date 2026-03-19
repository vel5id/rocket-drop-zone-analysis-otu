import time
from telemetry import generate_analysis_id

def benchmark_generate_id():
    config = {
        "iterations": 1000,
        "use_gpu": False,
        "launch_lat": -2.0,
        "launch_lon": 45.0,
        "azimuth": 90.0,
        "target_date": "2023-10-27",
        "start_date": "2023-10-01",
        "end_date": "2023-10-31",
        "sep_altitude": 100000,
        "sep_velocity": 2000,
        "sep_fp_angle": 15,
        "sep_azimuth": 90,
        "hurricane_mode": False,
        "cloud_threshold": 0.5,
        "zone_id": "test-zone"
    }

    start_time = time.perf_counter()
    iterations = 1000
    for i in range(iterations):
        generate_analysis_id(config)
    end_time = time.perf_counter()

    avg_time = (end_time - start_time) / iterations
    print(f"Average time for generate_analysis_id: {avg_time:.6f} seconds")

if __name__ == "__main__":
    benchmark_generate_id()
