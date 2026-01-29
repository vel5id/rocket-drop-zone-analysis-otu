#!/usr/bin/env python3
"""
Table S7: Economic Cost Breakdown

This script generates Supplementary Table S7: Economic Cost Breakdown
for the Rocket Drop Zone Analysis OTU pipeline.

Reference: IMPLEMENTATION_ROADMAP.md lines 401-474 (Task 3.9)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EconomicCostTableGenerator:
    """Generate Table S7: Economic Cost Breakdown."""
    
    def __init__(self, output_dir: str = "outputs/supplementary_tables"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Define cost components and their descriptions
        self.cost_components = {
            'vegetation_loss': {
                'description': 'Vegetation restoration after impact',
                'unit_cost_usd_per_ha': 8000.0,
                'unit_cost_kzt_per_ha': 8000.0 * 450,  # 1 USD = 450 KZT
                'formula': 'CVi = nVi × QVmi × vri × CnVi',
                'dependence': 'Q_VI (Vegetation Index)',
                'literature': 'Kazakhstan Ministry of Ecology (2023)',
                'notes': 'Higher NDVI = lower restoration cost'
            },
            'soil_degradation': {
                'description': 'Soil quality restoration (biological)',
                'unit_cost_usd_per_ha': 4000.0,
                'unit_cost_kzt_per_ha': 4000.0 * 450,
                'formula': 'CQBi = CBn × kBi × QBn',
                'dependence': 'Q_BI (Biodiversity Index)',
                'literature': 'SoilGrids 2.0 (2022)',
                'notes': 'Based on soil organic carbon loss'
            },
            'soil_strength': {
                'description': 'Soil mechanical restoration',
                'unit_cost_usd_per_ha': 3000.0,
                'unit_cost_kzt_per_ha': 3000.0 * 450,
                'formula': 'CQPi = Cp × kn × Qnp',
                'dependence': 'Q_SI (Soil Strength Index)',
                'literature': 'Protodyakonov (1962)',
                'notes': 'Compaction and crater filling'
            },
            'fire_risk': {
                'description': 'Fire suppression and restoration',
                'unit_cost_usd_per_ha': 5000.0,
                'unit_cost_kzt_per_ha': 5000.0 * 450,
                'formula': 'CFi = kF × QFi',
                'dependence': 'Q_Fire (Fire Hazard Index)',
                'literature': 'Kazakhstan Emergency Services (2024)',
                'notes': 'Hydrated fuel ignition risk'
            },
            'contamination': {
                'description': 'Toxic fuel cleanup',
                'unit_cost_usd_per_ha': 4000.0,
                'unit_cost_kzt_per_ha': 4000.0 * 450,
                'formula': 'CCont = kT × Area × Depth',
                'dependence': 'Impact intensity',
                'literature': 'NASA Safety Standard (2021)',
                'notes': 'UDMH/N2O4 remediation'
            },
            'mechanical_damage': {
                'description': 'Impact crater repair',
                'unit_cost_usd_per_ha': 2500.0,
                'unit_cost_kzt_per_ha': 2500.0 * 450,
                'formula': 'CMech = kM × Volume',
                'dependence': 'Kinetic energy',
                'literature': 'Space Debris Mitigation Guidelines',
                'notes': 'Based on 30,600 kg Proton-M stage'
            },
            'monitoring': {
                'description': 'Post-impact environmental monitoring',
                'unit_cost_usd_per_ha': 1500.0,
                'unit_cost_kzt_per_ha': 1500.0 * 450,
                'formula': 'CMon = kMon × Duration',
                'dependence': 'Regulatory requirements',
                'literature': 'Kazakhstan Space Agency (2023)',
                'notes': '5-year monitoring period'
            }
        }
        
        # Example OTU scenario data
        self.example_scenarios = {
            'low_stability': {
                'q_vi': 0.2,
                'q_si': 0.15,
                'q_bi': 0.1,
                'q_fire': 0.8,
                'area_ha': 100.0,
                'description': 'Low stability OTU (Q_OTU = 0.15)'
            },
            'medium_stability': {
                'q_vi': 0.5,
                'q_si': 0.45,
                'q_bi': 0.4,
                'q_fire': 0.3,
                'area_ha': 100.0,
                'description': 'Medium stability OTU (Q_OTU = 0.45)'
            },
            'high_stability': {
                'q_vi': 0.8,
                'q_si': 0.75,
                'q_bi': 0.7,
                'q_fire': 0.1,
                'area_ha': 100.0,
                'description': 'High stability OTU (Q_OTU = 0.75)'
            }
        }
    
    def calculate_component_cost(self, component: str, scenario: Dict[str, float]) -> Dict[str, float]:
        """Calculate cost for a specific component in a scenario."""
        comp = self.cost_components[component]
        
        # Calculate cost based on component type
        if component == 'vegetation_loss':
            # CVi = base_cost * (1 - Q_VI)
            cost_usd = comp['unit_cost_usd_per_ha'] * (1 - scenario['q_vi']) * scenario['area_ha']
        elif component == 'soil_degradation':
            # CQBi = base_cost * (1 - Q_BI)
            cost_usd = comp['unit_cost_usd_per_ha'] * (1 - scenario['q_bi']) * scenario['area_ha']
        elif component == 'soil_strength':
            # CQPi = base_cost * (1 - Q_SI)
            cost_usd = comp['unit_cost_usd_per_ha'] * (1 - scenario['q_si']) * scenario['area_ha']
        elif component == 'fire_risk':
            # CFi = base_cost * Q_Fire
            cost_usd = comp['unit_cost_usd_per_ha'] * scenario['q_fire'] * scenario['area_ha']
        else:
            # Fixed cost per hectare for other components
            cost_usd = comp['unit_cost_usd_per_ha'] * scenario['area_ha']
        
        cost_kzt = cost_usd * 450  # Convert to KZT
        
        return {
            'cost_usd': cost_usd,
            'cost_kzt': cost_kzt,
            'cost_per_ha_usd': cost_usd / scenario['area_ha'],
            'cost_per_ha_kzt': cost_kzt / scenario['area_ha']
        }
    
    def generate_main_table(self) -> pd.DataFrame:
        """Generate main economic cost breakdown table."""
        records = []
        
        for comp_id, comp_data in self.cost_components.items():
            record = {
                'Component': comp_id.replace('_', ' ').title(),
                'Description': comp_data['description'],
                'Unit Cost (USD/ha)': f"${comp_data['unit_cost_usd_per_ha']:,.0f}",
                'Unit Cost (KZT/ha)': f"{comp_data['unit_cost_kzt_per_ha']:,.0f} KZT",
                'Formula': comp_data['formula'],
                'Dependence': comp_data['dependence'],
                'Literature Source': comp_data['literature'],
                'Notes': comp_data['notes']
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        return df
    
    def generate_scenario_comparison(self) -> pd.DataFrame:
        """Generate scenario comparison table."""
        records = []
        
        for scenario_id, scenario_data in self.example_scenarios.items():
            total_usd = 0
            total_kzt = 0
            
            # Calculate costs for each component
            component_costs = {}
            for comp_id in self.cost_components.keys():
                costs = self.calculate_component_cost(comp_id, scenario_data)
                component_costs[comp_id] = costs
                total_usd += costs['cost_usd']
                total_kzt += costs['cost_kzt']
            
            # Add summary row
            record = {
                'Scenario': scenario_data['description'],
                'Q_VI': scenario_data['q_vi'],
                'Q_SI': scenario_data['q_si'],
                'Q_BI': scenario_data['q_bi'],
                'Q_Fire': scenario_data['q_fire'],
                'Area (ha)': scenario_data['area_ha'],
                'Vegetation Cost (USD)': f"${component_costs['vegetation_loss']['cost_usd']:,.0f}",
                'Soil Cost (USD)': f"${component_costs['soil_degradation']['cost_usd'] + component_costs['soil_strength']['cost_usd']:,.0f}",
                'Fire Cost (USD)': f"${component_costs['fire_risk']['cost_usd']:,.0f}",
                'Other Costs (USD)': f"${component_costs['contamination']['cost_usd'] + component_costs['mechanical_damage']['cost_usd'] + component_costs['monitoring']['cost_usd']:,.0f}",
                'Total Cost (USD)': f"${total_usd:,.0f}",
                'Total Cost (KZT)': f"{total_kzt:,.0f} KZT",
                'Cost per ha (USD)': f"${total_usd / scenario_data['area_ha']:,.0f}"
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        return df
    
    def generate_cost_distribution(self) -> pd.DataFrame:
        """Generate cost distribution table for medium stability scenario."""
        scenario = self.example_scenarios['medium_stability']
        records = []
        
        for comp_id, comp_data in self.cost_components.items():
            costs = self.calculate_component_cost(comp_id, scenario)
            
            record = {
                'Component': comp_id.replace('_', ' ').title(),
                'Cost (USD)': costs['cost_usd'],
                'Cost (KZT)': costs['cost_kzt'],
                'Percentage of Total': None,  # Will calculate after
                'Cost per ha (USD)': costs['cost_per_ha_usd'],
                'Cost per ha (KZT)': costs['cost_per_ha_kzt']
            }
            records.append(record)
        
        # Calculate percentages
        df = pd.DataFrame(records)
        total_usd = df['Cost (USD)'].sum()
        df['Percentage of Total'] = (df['Cost (USD)'] / total_usd * 100).round(1)
        
        return df
    
    def export_all_tables(self):
        """Export all tables to Excel, CSV, and LaTeX formats."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Generate tables
        main_table = self.generate_main_table()
        scenario_table = self.generate_scenario_comparison()
        distribution_table = self.generate_cost_distribution()
        
        # Create Excel file with multiple sheets
        excel_path = self.output_dir / f"Table_S7_Economic_Cost_Breakdown.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            main_table.to_excel(writer, sheet_name='Cost Components', index=False)
            scenario_table.to_excel(writer, sheet_name='Scenario Comparison', index=False)
            distribution_table.to_excel(writer, sheet_name='Cost Distribution', index=False)
            
            # Add metadata sheet
            metadata = pd.DataFrame([
                {'Field': 'Table Number', 'Value': 'S7'},
                {'Field': 'Title', 'Value': 'Economic Cost Breakdown'},
                {'Field': 'Description', 'Value': 'Detailed breakdown of restoration costs for rocket stage impact zones'},
                {'Field': 'Generated', 'Value': datetime.now().isoformat()},
                {'Field': 'Exchange Rate', 'Value': '1 USD = 450 KZT (Kazakhstani Tenge)'},
                {'Field': 'Area Unit', 'Value': 'Hectares (ha)'},
                {'Field': 'Reference', 'Value': 'IMPLEMENTATION_ROADMAP.md Task 3.9'}
            ])
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        logger.info(f"Excel table saved to {excel_path}")
        
        # Export CSV files
        main_table.to_csv(self.output_dir / "Table_S7_Cost_Components.csv", index=False)
        scenario_table.to_csv(self.output_dir / "Table_S7_Scenario_Comparison.csv", index=False)
        distribution_table.to_csv(self.output_dir / "Table_S7_Cost_Distribution.csv", index=False)
        
        # Export LaTeX tables
        self.export_latex_tables(main_table, scenario_table, distribution_table)
        
        # Generate summary report
        self.generate_summary_report(main_table, scenario_table, distribution_table)
        
        return excel_path
    
    def export_latex_tables(self, main_table, scenario_table, distribution_table):
        """Export tables to LaTeX format."""
        # Main table
        latex_main = main_table.to_latex(index=False, caption='Economic Cost Components', label='tab:s7-cost-components')
        with open(self.output_dir / "Table_S7_Cost_Components.tex", 'w') as f:
            f.write(latex_main)
        
        # Scenario table
        latex_scenario = scenario_table.to_latex(index=False, caption='Scenario Cost Comparison', label='tab:s7-scenario-comparison')
        with open(self.output_dir / "Table_S7_Scenario_Comparison.tex", 'w') as f:
            f.write(latex_scenario)
        
        # Distribution table
        latex_dist = distribution_table.to_latex(index=False, caption='Cost Distribution (Medium Stability)', label='tab:s7-cost-distribution')
        with open(self.output_dir / "Table_S7_Cost_Distribution.tex", 'w') as f:
            f.write(latex_dist)
        
        logger.info("LaTeX tables exported")
    
    def generate_summary_report(self, main_table, scenario_table, distribution_table):
        """Generate a summary report in Markdown format."""
        report_path = self.output_dir / "Table_S7_Summary_Report.md"
        
        with open(report_path, 'w') as f:
            f.write("# Table S7: Economic Cost Breakdown\n\n")
            f.write(f"**Generated:** {datetime.now().isoformat()}\n\n")
            
            f.write("## Overview\n")
            f.write("This table provides a detailed breakdown of restoration costs for rocket stage impact zones.\n\n")
            
            f.write("## Key Findings\n")
            
            # Extract key numbers
            medium_scenario = scenario_table[scenario_table['Scenario'].str.contains('Medium')].iloc[0]
            total_cost = medium_scenario['Total Cost (USD)']
            
            f.write(f"- **Total restoration cost for medium stability OTU:** {total_cost}\n")
            f.write(f"- **Number of cost components analyzed:** {len(main_table)}\n")
            f.write(f"- **Exchange rate used:** 1 USD = 450 KZT\n\n")
            
            f.write("## Cost Components\n")
            f.write("The following cost components are included:\n\n")
            
            for _, row in main_table.iterrows():
                f.write(f"### {row['Component']}\n")
                f.write(f"- **Description:** {row['Description']}\n")
                f.write(f"- **Unit Cost:** {row['Unit Cost (USD/ha)']} ({row['Unit Cost (KZT/ha')]})\n")
                f.write(f"- **Formula:** {row['Formula']}\n")
                f.write(f"- **Dependence:** {row['Dependence']}\n\n")
            
            f.write("## Files Generated\n")
            f.write("- `Table_S7_Economic_Cost_Breakdown.xlsx` (Excel with multiple sheets)\n")
            f.write("- `Table_S7_Cost_Components.csv` (CSV format)\n")
            f.write("- `Table_S7_Scenario_Comparison.csv` (CSV format)\n")
            f.write("- `Table_S7_Cost_Distribution.csv` (CSV format)\n")
            f.write("- `Table_S7_Cost_Components.tex` (LaTeX format)\n")
            f.write("- `Table_S7_Scenario_Comparison.tex` (LaTeX format)\n")
            f.write("- `Table_S7_Cost_Distribution.tex` (LaTeX format)\n")
            f.write("- `Table_S7_Summary_Report.md` (This report)\n")
        
        logger.info(f"Summary report saved to {report_path}")
    
    def run(self):
        """Execute the table generation pipeline."""
        logger.info("Starting Table S7 generation...")
        
        try:
            excel_path = self.export_all_tables()
            logger.info(f"Table S7 generation completed successfully: {excel_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating Table S7: {e}")
            return False


def main():
    """Main entry point."""
    generator = EconomicCostTableGenerator()
    success = generator.run()
    
    if success:
        print("Table S7 generation completed successfully.")
        print(f"Output files saved to: {generator.output_dir}")
        return 0
    else:
        print("Table S7 generation failed.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
