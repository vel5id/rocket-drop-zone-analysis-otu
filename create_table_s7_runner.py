#!/usr/bin/env python3
"""
Runner script for Table S7 creation.
"""

import subprocess
import sys
import os

def main():
    print("Creating Table S7: Economic Cost Breakdown...")
    
    # Run the table S7 generator
    result = subprocess.run([sys.executable, "scripts/create_table_s7.py"], 
                          capture_output=True, text=True)
    
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("Table S7 created successfully!")
        
        # Check if files were created
        output_dir = "outputs/supplementary_tables"
        expected_files = [
            "Table_S7_Economic_Cost_Breakdown.xlsx",
            "Table_S7_Cost_Components.csv",
            "Table_S7_Scenario_Comparison.csv",
            "Table_S7_Cost_Distribution.csv",
            "Table_S7_Cost_Components.tex",
            "Table_S7_Scenario_Comparison.tex",
            "Table_S7_Cost_Distribution.tex"
        ]
        
        for file in expected_files:
            filepath = os.path.join(output_dir, file)
            if os.path.exists(filepath):
                print(f"✓ {file}")
            else:
                print(f"✗ {file} (missing)")
        
        return 0
    else:
        print(f"Failed to create Table S7. Return code: {result.returncode}")
        return 1

if __name__ == "__main__":
    sys.exit(main())