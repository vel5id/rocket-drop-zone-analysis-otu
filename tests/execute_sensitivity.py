import subprocess
import sys
import os

def run_script(script_path):
    """Run a Python script using venv_311 python."""
    venv_python = "venv_311\\Scripts\\python.exe"
    if not os.path.exists(venv_python):
        print(f"ERROR: Virtual environment not found at {venv_python}")
        return False
    
    cmd = [venv_python, script_path]
    print(f"Running: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("STDOUT:")
        print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        print(f"Return code: {result.returncode}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Script failed with return code {e.returncode}")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        return False

if __name__ == "__main__":
    scripts = [
        "scripts/sensitivity_analysis_oat.py",
        "scripts/sensitivity_analysis_monte_carlo_complete.py",
        "scripts/sensitivity_analysis_sobol_complete.py"
    ]
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"WARNING: Script {script} not found, skipping")
            continue
        
        print(f"\n{'='*60}")
        print(f"Executing: {script}")
        print(f"{'='*60}")
        
        success = run_script(script)
        if not success:
            print(f"Failed to execute {script}")
            sys.exit(1)
    
    print("\n" + "="*60)
    print("All sensitivity analysis scripts executed successfully!")
    print("="*60)