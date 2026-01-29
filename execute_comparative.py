#!/usr/bin/env python3
"""
Execute comparative cost analysis and generate all output files.
"""
import sys
import os
import subprocess

def check_and_install_packages():
    """Check if required packages are installed."""
    required = ['numpy', 'pandas', 'matplotlib', 'seaborn', 'openpyxl']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✓ {pkg} is installed")
        except ImportError:
            missing.append(pkg)
            print(f"✗ {pkg} is missing")
    
    if missing:
        print(f"\nInstalling missing packages: {missing}")
        for pkg in missing:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
                print(f"  Installed {pkg}")
            except subprocess.CalledProcessError:
                print(f"  Failed to install {pkg}")
                return False
    return True

def main():
    print("=" * 70)
    print("EXECUTING TASK 5.3: COMPARATIVE COST ANALYSIS")
    print("=" * 70)
    
    # Check packages
    print("\n1. Checking dependencies...")
    if not check_and_install_packages():
        print("Failed to install required packages. Exiting.")
        return 1
    
    # Import and run main function
    print("\n2. Importing comparative analysis module...")
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from scripts.comparative_cost_analysis import main as comparative_main
    except ImportError as e:
        print(f"Failed to import module: {e}")
        return 1
    
    print("\n3. Running comparative analysis...")
    try:
        comparative_main()
        print("\n4. Analysis completed successfully!")
        
        # Check output files
        output_dir = "outputs/economic/comparative"
        expected_files = [
            "Comparative_Cost_Analysis.xlsx",
            "Cost_Comparison_Charts.png", 
            "Comparative_Analysis_Report.md"
        ]
        
        print(f"\n5. Verifying output files in {output_dir}:")
        for file in expected_files:
            path = os.path.join(output_dir, file)
            if os.path.exists(path):
                size = os.path.getsize(path)
                print(f"   ✓ {file} ({size:,} bytes)")
            else:
                print(f"   ✗ {file} (missing)")
        
        return 0
        
    except Exception as e:
        print(f"\nError during analysis: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())