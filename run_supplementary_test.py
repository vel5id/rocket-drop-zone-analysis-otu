#!/usr/bin/env python3
"""
Test script for supplementary materials package.
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("Testing Supplementary Materials Package...")
    
    # Create necessary directories
    directories = [
        "outputs/supplementary_materials",
        "outputs/supplementary_materials/tables",
        "outputs/supplementary_materials/figures",
        "outputs/supplementary_materials/data",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Check if required files exist
    required_files = [
        "scripts/supplementary_materials_package.py",
        "scripts/create_table_s7.py"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} (missing)")
    
    # Try to import and run the package
    try:
        print("\nImporting SupplementaryMaterialsPackage...")
        from scripts.supplementary_materials_package import SupplementaryMaterialsPackage
        
        print("Creating package instance...")
        package = SupplementaryMaterialsPackage()
        
        print("Testing collection methods...")
        
        # Test table collection
        print("Collecting tables...")
        tables = package.collect_tables_s1_s7()
        print(f"Collected {len(tables)} tables")
        
        # Test figure collection
        print("Collecting figures...")
        figures = package.collect_figures_s1_s2()
        print(f"Collected {len(figures)} figures")
        
        # Test additional materials
        print("Collecting additional materials...")
        additional = package.collect_additional_materials()
        print(f"Collected {len(additional)} additional materials")
        
        # Test README creation
        print("Creating README...")
        readme_path = package.create_readme_file()
        print(f"README created: {readme_path}")
        
        # Test file manifest
        print("Creating file manifest...")
        manifest_path = package.create_file_manifest()
        print(f"File manifest created: {manifest_path}")
        
        # Test ZIP archive
        print("Creating ZIP archive...")
        zip_path = package.create_zip_archive()
        print(f"ZIP archive created: {zip_path}")
        
        print("\n" + "="*70)
        print("SUCCESS: All tests passed!")
        print("="*70)
        
        return 0
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())