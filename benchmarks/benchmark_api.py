import time
import requests
import multiprocessing
import os
import signal
import subprocess

def run_server():
    # Start the server
    os.environ["PYTHONPATH"] = "."
    process = subprocess.Popen(["python3", "api/main.py"], env=os.environ)
    return process

def test_endpoint():
    url = "http://127.0.0.1:8000/api/simulation/run"
    payload = {
        "iterations": 10,
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

    # Wait for server to start
    for i in range(10):
        try:
            requests.get("http://127.0.0.1:8000/api/health")
            break
        except:
            time.sleep(1)

    start_time = time.perf_counter()
    iterations = 20
    for i in range(iterations):
        # Change something to avoid hash collision if we want to see file creation overhead
        payload["iterations"] = 10 + i
        requests.post(url, json=payload)
    end_time = time.perf_counter()

    avg_time = (end_time - start_time) / iterations
    print(f"Average response time for /api/simulation/run: {avg_time:.6f} seconds")

if __name__ == "__main__":
    server_process = run_server()
    try:
        test_endpoint()
    finally:
        server_process.terminate()
        server_process.wait()
