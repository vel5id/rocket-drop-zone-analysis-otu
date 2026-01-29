import uvicorn
import os
import sys

# Add the project root to sys.path to ensure modules are found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print(f"Starting backend server from: {os.getcwd()}")
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
