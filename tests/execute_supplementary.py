#!/usr/bin/env python3
"""
Execute the supplementary materials package creation.
"""

import sys
import os
import subprocess

def main():
    print("=" * 70)
    print("Executing Supplementary Materials Package Creation")
    print("Task 3.9 from IMPLEMENTATION_ROADMAP.md")
    print("=" * 70)
    
    # First, create Table S7 if it doesn't exist
    table_s7_path = "outputs/supplementary_tables/Table_S7_Economic_Cost_Breakdown.xlsx"
    if not os.path.exists(table_s7_path):
        print("\nCreating Table S7: Economic Cost Breakdown...")
        result = subprocess.run([sys.executable, "scripts/create_table_s7.py"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("Table S7 created successfully.")
        else:
            print(f"Warning: Table S7 creation failed: {result.stderr}")
    
    # Check for Figure S2
    figure_s2_path = "outputs/figures/Figure_S2_Validation_Workflow.png"
    if not os.path.exists(figure_s2_path):
        print("\nWarning: Figure S2 not found. Creating placeholder...")
        # Create a simple placeholder figure
        try:
            from PIL import Image, ImageDraw, ImageFont
            img = Image.new('RGB', (800, 600), color='white')
            d = ImageDraw.Draw(img)
            # Add text
            try:
                font = ImageFont.truetype("arial.ttf", 40)
            except:
                font = ImageFont.load_default()
            d.text((100, 250), "Figure S2: Validation Workflow\n(Placeholder - to be generated)", 
                  fill='black', font=font)
            img.save(figure_s2_path)
            print(f"Created placeholder: {figure_s2_path}")
        except Exception as e:
            print(f"Could not create placeholder: {e}")
    
    # Now run the main supplementary materials package
    print("\n" + "=" * 70)
    print("Running Supplementary Materials Package Creator...")
    print("=" * 70)
    
    result = subprocess.run([sys.executable, "scripts/supplementary_materials_package.py"], 
                          capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    if result.returncode == 0:
        print("\n" + "=" * 70)
        print("SUCCESS: Supplementary materials package created!")
        print("=" * 70)
        
        # Check output files
        output_files = [
            "outputs/Supplementary_Materials.zip",
            "outputs/supplementary_materials/README.md",
            "outputs/supplementary_materials/File_Manifest.xlsx",
            "outputs/supplementary_materials/completion_report.json"
        ]
        
        for file in output_files:
            if os.path.exists(file):
                size = os.path.getsize(file) / (1024*1024)
                print(f"✓ {file} ({size:.2f} MB)")
            else:
                print(f"✗ {file} (missing)")
        
        return 0
    else:
        print(f"\nERROR: Supplementary materials package creation failed. Return code: {result.returncode}")
        return 1

if __name__ == "__main__":
    sys.exit(main())