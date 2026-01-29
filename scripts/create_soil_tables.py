"""
Task 1.2: Create Soil Coefficients Tables (Tables S2 and S3)

This script creates:
- Table S2: Bonitet correction coefficients (Q_Bi)
- Table S3: Protodyakonov strength coefficients (Q_Si)

Implements БЛОК 1, Task 1.2 from revision plan.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Dict, List


class SoilQualityCalculator:
    """
    Calculator for soil quality (bonitet) index Q_Bi.
    
    Implements the bonitet methodology for soil quality assessment
    based on national soil classification standards.
    """
    
    # Bonitet correction coefficients by soil type
    BONITET_COEFFICIENTS = {
        'Chernozem (typical)': {
            'base_score': 85,
            'texture_factor': 1.0,
            'humus_content': 6.5,
            'description': 'High fertility, optimal structure',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.95,
                'slope_5_10': 0.85,
                'slope_10_plus': 0.70,
            }
        },
        'Chernozem (leached)': {
            'base_score': 75,
            'texture_factor': 0.95,
            'humus_content': 5.5,
            'description': 'Good fertility, slight leaching',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.93,
                'slope_5_10': 0.82,
                'slope_10_plus': 0.65,
            }
        },
        'Kastanozem (dark)': {
            'base_score': 65,
            'texture_factor': 0.90,
            'humus_content': 4.0,
            'description': 'Moderate fertility, semi-arid',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.90,
                'slope_5_10': 0.78,
                'slope_10_plus': 0.60,
            }
        },
        'Kastanozem (light)': {
            'base_score': 50,
            'texture_factor': 0.85,
            'humus_content': 3.0,
            'description': 'Low-moderate fertility, arid',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.88,
                'slope_5_10': 0.75,
                'slope_10_plus': 0.55,
            }
        },
        'Solonetz': {
            'base_score': 35,
            'texture_factor': 0.70,
            'humus_content': 2.5,
            'description': 'Saline, poor structure',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.85,
                'slope_5_10': 0.70,
                'slope_10_plus': 0.50,
            }
        },
        'Solonchak': {
            'base_score': 20,
            'texture_factor': 0.60,
            'humus_content': 1.5,
            'description': 'Highly saline, very poor',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.80,
                'slope_5_10': 0.65,
                'slope_10_plus': 0.45,
            }
        },
        'Sandy soils': {
            'base_score': 25,
            'texture_factor': 0.65,
            'humus_content': 1.0,
            'description': 'Low water retention, poor fertility',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.82,
                'slope_5_10': 0.68,
                'slope_10_plus': 0.48,
            }
        },
        'Rocky outcrops': {
            'base_score': 10,
            'texture_factor': 0.40,
            'humus_content': 0.5,
            'description': 'Minimal soil development',
            'correction_factors': {
                'slope_0_3': 1.0,
                'slope_3_5': 0.75,
                'slope_5_10': 0.55,
                'slope_10_plus': 0.35,
            }
        },
    }
    
    def calculate_qbi(self, soil_type: str, slope_class: str) -> float:
        """
        Calculate Q_Bi index for given soil type and slope.
        
        Args:
            soil_type: Soil classification type
            slope_class: Slope class (e.g., 'slope_0_3')
        
        Returns:
            Q_Bi value [0, 1]
        """
        if soil_type not in self.BONITET_COEFFICIENTS:
            raise ValueError(f"Unknown soil type: {soil_type}")
        
        coef = self.BONITET_COEFFICIENTS[soil_type]
        base_score = coef['base_score']
        slope_factor = coef['correction_factors'].get(slope_class, 1.0)
        
        # Apply correction
        adjusted_score = base_score * slope_factor
        
        # Normalize to [0, 1]
        qbi = adjusted_score / 100.0
        
        return round(qbi, 3)


class SoilStrengthCalculator:
    """
    Calculator for soil strength (Protodyakonov) index Q_Si.
    
    Implements the Protodyakonov scale for rock and soil strength assessment.
    """
    
    # Protodyakonov strength coefficients
    PROTODYAKONOV_COEFFICIENTS = {
        'Very strong rocks': {
            'f_value': 15.0,
            'examples': 'Granite, basalt, quartzite',
            'description': 'Extremely hard, requires blasting',
            'compressive_strength_mpa': 150,
        },
        'Strong rocks': {
            'f_value': 10.0,
            'examples': 'Limestone, sandstone (cemented)',
            'description': 'Hard, difficult to excavate',
            'compressive_strength_mpa': 100,
        },
        'Medium rocks': {
            'f_value': 6.0,
            'examples': 'Shale, marl, soft sandstone',
            'description': 'Moderately hard',
            'compressive_strength_mpa': 60,
        },
        'Weak rocks': {
            'f_value': 3.0,
            'examples': 'Clay shale, weathered rock',
            'description': 'Soft rock, easily excavated',
            'compressive_strength_mpa': 30,
        },
        'Very weak rocks': {
            'f_value': 1.5,
            'examples': 'Highly weathered rock, hardpan',
            'description': 'Very soft, transitional to soil',
            'compressive_strength_mpa': 15,
        },
        'Hard soils': {
            'f_value': 0.8,
            'examples': 'Dense clay, compacted loam',
            'description': 'Stiff, requires mechanical excavation',
            'compressive_strength_mpa': 8,
        },
        'Medium soils': {
            'f_value': 0.5,
            'examples': 'Loam, sandy clay',
            'description': 'Moderate strength',
            'compressive_strength_mpa': 5,
        },
        'Soft soils': {
            'f_value': 0.3,
            'examples': 'Sand, loose loam',
            'description': 'Low strength, easily excavated',
            'compressive_strength_mpa': 3,
        },
    }
    
    def calculate_qsi(self, material_type: str) -> float:
        """
        Calculate Q_Si index from Protodyakonov coefficient.
        
        Args:
            material_type: Material classification
        
        Returns:
            Q_Si value [0, 1]
        """
        if material_type not in self.PROTODYAKONOV_COEFFICIENTS:
            raise ValueError(f"Unknown material type: {material_type}")
        
        f_value = self.PROTODYAKONOV_COEFFICIENTS[material_type]['f_value']
        
        # Normalize Protodyakonov scale (0.3 to 20) to [0, 1]
        # Higher f = stronger = higher Q_Si
        qsi = (f_value - 0.3) / (20.0 - 0.3)
        
        return round(qsi, 3)


def create_table_s2() -> pd.DataFrame:
    """
    Create Table S2: Bonitet correction coefficients.
    
    Returns:
        DataFrame with bonitet coefficients
    """
    calculator = SoilQualityCalculator()
    
    records = []
    for soil_type, data in calculator.BONITET_COEFFICIENTS.items():
        record = {
            'Soil_Type': soil_type,
            'Base_Bonitet_Score': data['base_score'],
            'Texture_Factor': data['texture_factor'],
            'Humus_Content_Percent': data['humus_content'],
            'Slope_0_3_deg': data['correction_factors']['slope_0_3'],
            'Slope_3_5_deg': data['correction_factors']['slope_3_5'],
            'Slope_5_10_deg': data['correction_factors']['slope_5_10'],
            'Slope_10_plus_deg': data['correction_factors']['slope_10_plus'],
            'Description': data['description'],
            'Q_Bi_Example_Flat': calculator.calculate_qbi(soil_type, 'slope_0_3'),
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    return df


def create_table_s3() -> pd.DataFrame:
    """
    Create Table S3: Protodyakonov strength coefficients.
    
    Returns:
        DataFrame with Protodyakonov coefficients
    """
    calculator = SoilStrengthCalculator()
    
    records = []
    for material_type, data in calculator.PROTODYAKONOV_COEFFICIENTS.items():
        record = {
            'Material_Type': material_type,
            'Protodyakonov_f': data['f_value'],
            'Compressive_Strength_MPa': data['compressive_strength_mpa'],
            'Examples': data['examples'],
            'Description': data['description'],
            'Q_Si_Normalized': calculator.calculate_qsi(material_type),
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    
    # Sort by strength (descending)
    df = df.sort_values('Protodyakonov_f', ascending=False).reset_index(drop=True)
    
    return df


def save_tables(df_s2: pd.DataFrame, df_s3: pd.DataFrame, output_dir: Path) -> None:
    """
    Save Tables S2 and S3 in multiple formats.
    
    Args:
        df_s2: Table S2 DataFrame
        df_s3: Table S3 DataFrame
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save Table S2
    excel_s2 = output_dir / "Table_S2_Soil_Quality_Coefficients.xlsx"
    with pd.ExcelWriter(excel_s2, engine='openpyxl') as writer:
        df_s2.to_excel(writer, sheet_name='Bonitet Coefficients', index=False)
        worksheet = writer.sheets['Bonitet Coefficients']
        
        # Set column widths
        for col in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']:
            worksheet.column_dimensions[col].width = 18
    
    df_s2.to_csv(output_dir / "Table_S2_Soil_Quality_Coefficients.csv", index=False)
    print(f"Saved Table S2: {excel_s2}")
    
    # Save Table S3
    excel_s3 = output_dir / "Table_S3_Protodyakonov_Strength.xlsx"
    with pd.ExcelWriter(excel_s3, engine='openpyxl') as writer:
        df_s3.to_excel(writer, sheet_name='Protodyakonov Scale', index=False)
        worksheet = writer.sheets['Protodyakonov Scale']
        
        for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            worksheet.column_dimensions[col].width = 22
    
    df_s3.to_csv(output_dir / "Table_S3_Protodyakonov_Strength.csv", index=False)
    print(f"Saved Table S3: {excel_s3}")
    
    # Create LaTeX versions
    latex_s2 = df_s2[['Soil_Type', 'Base_Bonitet_Score', 'Slope_0_3_deg', 
                      'Slope_5_10_deg', 'Q_Bi_Example_Flat']].to_latex(
        index=False,
        caption='Bonitet correction coefficients for soil quality assessment',
        label='tab:bonitet_coefficients',
        column_format='lcccc'
    )
    
    with open(output_dir / "Table_S2_Soil_Quality_Coefficients.tex", 'w') as f:
        f.write(latex_s2)
    
    latex_s3 = df_s3[['Material_Type', 'Protodyakonov_f', 'Compressive_Strength_MPa', 
                      'Q_Si_Normalized']].to_latex(
        index=False,
        caption='Protodyakonov strength coefficients for soil/rock assessment',
        label='tab:protodyakonov_coefficients',
        column_format='lccc'
    )
    
    with open(output_dir / "Table_S3_Protodyakonov_Strength.tex", 'w') as f:
        f.write(latex_s3)
    
    print("Saved LaTeX versions")


def create_worked_example() -> str:
    """
    Create a worked example demonstrating the calculation.
    
    Returns:
        Formatted text with example
    """
    calc_qbi = SoilQualityCalculator()
    calc_qsi = SoilStrengthCalculator()
    
    example = """
### Worked Example: Soil Index Calculation

**Example OTU:** OTU_245 (hypothetical)

**Step 1: Soil Quality (Q_Bi)**
- Soil type: Kastanozem (dark)
- Base bonitet score: 65
- Slope class: 3-5 degrees
- Slope correction factor: 0.90
- Adjusted score: 65 × 0.90 = 58.5
- Q_Bi = 58.5 / 100 = 0.585

**Step 2: Soil Strength (Q_Si)**
- Material type: Medium soils (loam, sandy clay)
- Protodyakonov coefficient (f): 0.5
- Normalization: (0.5 - 0.3) / (20.0 - 0.3) = 0.010
- Q_Si = 0.010

**Step 3: Combined Soil Index**
- Weight for Q_Bi: k_Bi = 0.3
- Weight for Q_Si: k_Si = 0.4
- Soil component = (k_Bi × Q_Bi) + (k_Si × Q_Si)
- Soil component = (0.3 × 0.585) + (0.4 × 0.010)
- Soil component = 0.176 + 0.004 = 0.180

This example demonstrates how soil characteristics contribute to the overall
OTU stability index (Q_OTU). The methodology is fully reproducible using
Tables S2 and S3.
"""
    
    return example


def main():
    """Main execution function."""
    print("=" * 70)
    print("Task 1.2: Creating Soil Coefficients Tables (S2 and S3)")
    print("=" * 70)
    print()
    
    # Create tables
    print("Creating Table S2 (Bonitet coefficients)...")
    df_s2 = create_table_s2()
    print(f"Table S2 created with {len(df_s2)} soil types")
    
    print("Creating Table S3 (Protodyakonov coefficients)...")
    df_s3 = create_table_s3()
    print(f"Table S3 created with {len(df_s3)} material types")
    
    # Save outputs
    output_dir = Path("outputs/supplementary_tables")
    save_tables(df_s2, df_s3, output_dir)
    
    # Create worked example
    example_text = create_worked_example()
    example_path = output_dir / "Soil_Calculation_Worked_Example.txt"
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(example_text)
    
    print(f"Saved worked example: {example_path}")
    
    print()
    print("=" * 70)
    print("Task 1.2 COMPLETED")
    print(f"Output files created in: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
