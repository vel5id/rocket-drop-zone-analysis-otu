"""
Test script to run the economic worked example.
This simulates the execution of create_economic_worked_example.py
without requiring the full virtual environment activation.
"""
import sys
import os
from pathlib import Path

# Add the scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import the main module
from scripts.create_economic_worked_example import (
    create_otu_245_data,
    create_hypothetical_scenario,
    calculate_detailed_breakdown,
    export_excel_file,
    create_visualizations,
    create_scenario_description,
    create_manuscript_section
)

def test_components():
    """Test individual components of the worked example."""
    print("Testing OTU_245 data creation...")
    otu_data = create_otu_245_data()
    print(f"  OTU data shape: {otu_data.shape}")
    print(f"  Values: {otu_data.flatten()}")
    
    print("\nTesting scenario creation...")
    scenario = create_hypothetical_scenario()
    print(f"  Scenario: {scenario['name']}")
    print(f"  Mass: {scenario['mass_kg']} kg")
    
    print("\nTesting damage calculation...")
    damage, breakdown_df = calculate_detailed_breakdown(otu_data)
    print(f"  Total KZT: {damage['grand_total_kzt']:,.0f}")
    print(f"  Total USD: {damage['grand_total_usd']:,.0f}")
    
    print("\nBreakdown DataFrame:")
    print(breakdown_df.to_string())
    
    return otu_data, scenario, damage, breakdown_df

def generate_outputs():
    """Generate all output files."""
    print("\n" + "="*60)
    print("Generating all output files...")
    print("="*60)
    
    # Create output directory
    output_dir = Path("outputs/economic")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate data
    otu_data = create_otu_245_data()
    scenario = create_hypothetical_scenario()
    damage, breakdown_df = calculate_detailed_breakdown(otu_data)
    
    # Export Excel file
    excel_path = output_dir / "OTU_245_Worked_Example.xlsx"
    print(f"\n1. Exporting Excel file: {excel_path}")
    export_excel_file(breakdown_df, scenario, damage, excel_path)
    
    # Create visualizations
    print(f"\n2. Creating visualizations in: {output_dir}")
    create_visualizations(damage, breakdown_df, output_dir)
    
    # Create scenario description
    scenario_path = output_dir / "OTU_245_Scenario_Description.md"
    print(f"\n3. Creating scenario description: {scenario_path}")
    create_scenario_description(scenario, damage, scenario_path)
    
    # Create manuscript section
    manuscript_path = output_dir / "Economic_Worked_Example.md"
    print(f"\n4. Creating manuscript section: {manuscript_path}")
    create_manuscript_section(damage, scenario, breakdown_df, manuscript_path)
    
    print("\n" + "="*60)
    print("ALL FILES GENERATED SUCCESSFULLY")
    print("="*60)
    
    # List generated files
    print("\nGenerated files:")
    for file in output_dir.glob("*"):
        print(f"  - {file.relative_to('outputs/economic')}")
    
    return True

if __name__ == "__main__":
    try:
        # Test components first
        print("Starting Task 5.2 Worked Example Test")
        print("="*60)
        
        test_components()
        
        # Generate outputs
        success = generate_outputs()
        
        if success:
            print("\n✅ Task 5.2 test completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Task 5.2 test failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)