import requests
import json
import time

def test_simulation():
    url = "http://127.0.0.1:8000/api/simulation/run"
    payload = {
        "iterations": 100,
        "use_gpu": False,
        "launch_lat": 45.0,
        "launch_lon": 63.0,
        "azimuth": 90.0,
        "target_date": "2024-10-10",
        "sep_altitude": 50000.0,
        "sep_velocity": 2000.0,
        "sep_fp_angle": 30.0,
        "sep_azimuth": 5.0
    }
    
    print(f"Sending request to {url}...")
    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return
    
    job = response.json()
    job_id = job["job_id"]
    print(f"Job started: {job_id}")
    
    status_url = f"http://127.0.0.1:8000/api/simulation/status/{job_id}"
    
    while True:
        status_resp = requests.get(status_url)
        status_data = status_resp.json()
        print(f"Status: {status_data['status']}, Progress: {status_data['progress']}%")
        
        if status_data["status"] == "completed":
            print("Simulation completed successfully!")
            break
        elif status_data["status"] == "failed":
            print("Simulation failed!")
            print(status_data.get("error"))
            break
        
        time.sleep(2)

if __name__ == "__main__":
    test_simulation()
