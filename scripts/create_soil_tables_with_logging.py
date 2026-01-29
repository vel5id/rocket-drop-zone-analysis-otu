"""
Task 1.2: Soil Coefficients Tables with Comprehensive Logging

Enhanced version with detailed logging and progress tracking.
Implements БЛОК 1, Task 1.2 from revision plan.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import time

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'soil_tables_processing.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SoilTablesGenerator:
    """Class for generating soil coefficient tables with logging."""
    
    def __init__(self):
        self.start_time = time.time()
        logger.info("[INIT] SoilTablesGenerator initialized")
    
    def create_soil_quality_table(self) -> pd.DataFrame:
        """Create Table S2: Soil Quality (Bonitet) Coefficients."""
        logger.info("[PROCESS] Creating Table S2: Soil Quality Coefficients")
        
        # Soil quality classes based on bonitet methodology
        soil_classes = [
            {
                'Soil_Class': 'I - Excellent',
                'Description': 'Chernozem, deep, well-structured',
                'Bonitet_Score': 90,
                'QBi_Coefficient': 1.00,
                'Typical_Locations': 'Northern Kazakhstan steppe',
                'Suitability': 'Optimal for all uses',
                'Color_Code': '#2E8B57',  # Sea green
            },
            {
                'Soil_Class': 'II - Very Good',
                'Description': 'Dark chestnut, moderate depth',
                'Bonitet_Score': 80,
                'QBi_Coefficient': 0.85,
                'Typical_Locations': 'Central Kazakhstan',
                'Suitability': 'Very good for agriculture',
                'Color_Code': '#3CB371',  # Medium sea green
            },
            {
                'Soil_Class': 'III - Good',
                'Description': 'Chestnut, some limitations',
                'Bonitet_Score': 70,
                'QBi_Coefficient': 0.70,
                'Typical_Locations': 'Southern steppe regions',
                'Suitability': 'Good with management',
                'Color_Code': '#90EE90',  # Light green
            },
            {
                'Soil_Class': 'IV - Moderate',
                'Description': 'Light chestnut, shallow',
                'Bonitet_Score': 60,
                'QBi_Coefficient': 0.55,
                'Typical_Locations': 'Semi-desert transition',
                'Suitability': 'Moderate, requires improvement',
                'Color_Code': '#FFD700',  # Gold
            },
            {
                'Soil_Class': 'V - Poor',
                'Description': 'Brown semi-desert, saline',
                'Bonitet_Score': 50,
                'QBi_Coefficient': 0.40,
                'Typical_Locations': 'Aral Sea region',
                'Suitability': 'Limited use',
                'Color_Code': '#FFA500',  # Orange
            },
            {
                'Soil_Class': 'VI - Very Poor',
                'Description': 'Desert, highly saline, rocky',
                'Bonitet_Score': 40,
                'QBi_Coefficient': 0.25,
                'Typical_Locations': 'Betpak-Dala desert',
                'Suitability': 'Very limited, restoration needed',
                'Color_Code': '#FF6347',  # Tomato red
            },
            {
                'Soil_Class': 'VII - Unsuitable',
                'Description': 'Bare rock, salt flats, dunes',
                'Bonitet_Score': 30,
                'QBi_Coefficient': 0.10,
                'Typical_Locations': 'Moyynkum desert',
                'Suitability': 'Not suitable for impact',
                'Color_Code': '#DC143C',  # Crimson
            },
        ]
        
        df = pd.DataFrame(soil_classes)
        logger.info(f"[OK] Table S2 created with {len(df)} soil classes")
        return df
    
    def create_soil_strength_table(self) -> pd.DataFrame:
        """Create Table S3: Protodyakonov Strength Coefficients."""
        logger.info("[PROCESS] Creating Table S3: Soil Strength Coefficients")
        
        # Protodyakonov strength scale for engineering geology
        strength_classes = [
            {
                'Strength_Class': 'I - Extremely Strong',
                'Protodyakonov_Index': 20,
                'QSi_Coefficient': 1.00,
                'Rock_Types': 'Granite, basalt, quartzite',
                'Compressive_Strength_MPa': '>250',
                'Typical_Formations': 'Bedrock outcrops',
                'Excavation_Difficulty': 'Very difficult - blasting required',
                'Color_Code': '#00008B',  # Dark blue
            },
            {
                'Strength_Class': 'II - Very Strong',
                'Protodyakonov_Index': 15,
                'QSi_Coefficient': 0.85,
                'Rock_Types': 'Limestone, sandstone, shale',
                'Compressive_Strength_MPa': '100-250',
                'Typical_Formations': 'Consolidated sedimentary',
                'Excavation_Difficulty': 'Difficult - heavy equipment',
                'Color_Code': '#4169E1',  # Royal blue
            },
            {
                'Strength_Class': 'III - Strong',
                'Protodyakonov_Index': 10,
                'QSi_Coefficient': 0.70,
                'Rock_Types': 'Weathered rock, hard clay',
                'Compressive_Strength_MPa': '50-100',
                'Typical_Formations': 'Weathered bedrock',
                'Excavation_Difficulty': 'Moderate - excavator',
                'Color_Code': '#87CEEB',  # Sky blue
            },
            {
                'Strength_Class': 'IV - Medium',
                'Protodyakonov_Index': 8,
                'QSi_Coefficient': 0.55,
                'Rock_Types': 'Dense clay, cemented sand',
                'Compressive_Strength_MPa': '25-50',
                'Typical_Formations': 'Alluvial deposits',
                'Excavation_Difficulty': 'Easy - backhoe',
                'Color_Code': '#98FB98',  # Pale green
            },
            {
                'Strength_Class': 'V - Weak',
                'Protodyakonov_Index': 5,
                'QSi_Coefficient': 0.40,
                'Rock_Types': 'Soft clay, loose sand',
                'Compressive_Strength_MPa': '10-25',
                'Typical_Formations': 'Floodplain sediments',
                'Excavation_Difficulty': 'Very easy - shovel',
                'Color_Code': '#FFD700',  # Gold
            },
            {
                'Strength_Class': 'VI - Very Weak',
                'Protodyakonov_Index': 3,
                'QSi_Coefficient': 0.25,
                'Rock_Types': 'Peat, organic soil, silt',
                'Compressive_Strength_MPa': '5-10',
                'Typical_Formations': 'Wetlands, marshes',
                'Excavation_Difficulty': 'Extremely easy - manual',
                'Color_Code': '#FFA500',  # Orange
            },
            {
                'Strength_Class': 'VII - Unconsolidated',
                'Protodyakonov_Index': 1,
                'QSi_Coefficient': 0.10,
                'Rock_Types': 'Sand dunes, gravel',
                'Compressive_Strength_MPa': '<5',
                'Typical_Formations': 'Desert, river banks',
                'Excavation_Difficulty': 'No equipment needed',
                'Color_Code': '#FF6347',  # Tomato red
            },
        ]
        
        df = pd.DataFrame(strength_classes)
        logger.info(f"[OK] Table S3 created with {len(df)} strength classes")
        return df
    
    def save_tables(self, df_quality: pd.DataFrame, df_strength: pd.DataFrame, output_dir: Path):
        """Save tables in multiple formats."""
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[SAVE] Saving tables to {output_dir}")
        
        # Save Table S2 (Soil Quality)
        logger.info("[PROCESS] Saving Table S2...")
        excel_path_s2 = output_dir / "Table_S2_Soil_Quality_Coefficients.xlsx"
        csv_path_s2 = output_dir / "Table_S2_Soil_Quality_Coefficients.csv"
        tex_path_s2 = output_dir / "Table_S2_Soil_Quality_Coefficients.tex"
        
        try:
            # Excel
            with pd.ExcelWriter(excel_path_s2, engine='openpyxl') as writer:
                df_quality.to_excel(writer, sheet_name='Soil Quality', index=False)
                worksheet = writer.sheets['Soil Quality']
                for col in range(1, len(df_quality.columns) + 1):
                    worksheet.column_dimensions[chr(64 + col)].width = 20
            logger.info(f"[OK] Excel saved: {excel_path_s2}")
            print(f"[OK] Excel saved: {excel_path_s2}")
            
            # CSV
            df_quality.to_csv(csv_path_s2, index=False, encoding='utf-8')
            logger.info(f"[OK] CSV saved: {csv_path_s2}")
            print(f"[OK] CSV saved: {csv_path_s2}")
            
            # LaTeX
            df_latex = df_quality[['Soil_Class', 'Bonitet_Score', 'QBi_Coefficient', 'Description']].copy()
            latex_content = df_latex.to_latex(
                index=False,
                caption='Soil quality coefficients based on bonitet methodology',
                label='tab:soil_quality_coefficients',
                column_format='lccc',
                escape=False
            )
            with open(tex_path_s2, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            logger.info(f"[OK] LaTeX saved: {tex_path_s2}")
            print(f"[OK] LaTeX saved: {tex_path_s2}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save Table S2: {e}")
            print(f"[ERROR] Table S2: {e}")
        
        # Save Table S3 (Soil Strength)
        logger.info("[PROCESS] Saving Table S3...")
        excel_path_s3 = output_dir / "Table_S3_Protodyakonov_Strength.xlsx"
        csv_path_s3 = output_dir / "Table_S3_Protodyakonov_Strength.csv"
        tex_path_s3 = output_dir / "Table_S3_Protodyakonov_Strength.tex"
        
        try:
            # Excel
            with pd.ExcelWriter(excel_path_s3, engine='openpyxl') as writer:
                df_strength.to_excel(writer, sheet_name='Soil Strength', index=False)
                worksheet = writer.sheets['Soil Strength']
                for col in range(1, len(df_strength.columns) + 1):
                    worksheet.column_dimensions[chr(64 + col)].width = 20
            logger.info(f"[OK] Excel saved: {excel_path_s3}")
            print(f"[OK] Excel saved: {excel_path_s3}")
            
            # CSV
            df_strength.to_csv(csv_path_s3, index=False, encoding='utf-8')
            logger.info(f"[OK] CSV saved: {csv_path_s3}")
            print(f"[OK] CSV saved: {csv_path_s3}")
            
            # LaTeX
            df_latex = df_strength[['Strength_Class', 'Protodyakonov_Index', 'QSi_Coefficient', 'Rock_Types']].copy()
            latex_content = df_latex.to_latex(
                index=False,
                caption='Soil strength coefficients based on Protodyakonov scale',
                label='tab:soil_strength_coefficients',
                column_format='lccc',
                escape=False
            )
            with open(tex_path_s3, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            logger.info(f"[OK] LaTeX saved: {tex_path_s3}")
            print(f"[OK] LaTeX saved: {tex_path_s3}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save Table S3: {e}")
            print(f"[ERROR] Table S3: {e}")
    
    def create_worked_example(self, output_dir: Path):
        """Create worked example for soil calculation."""
        logger.info("[PROCESS] Creating worked example...")
        
        example_text = """
        WORKED EXAMPLE: Soil Quality and Strength Calculation
        
        Example OTU: OTU_215 (hypothetical)
        
        Input Data:
        - Soil type: Chestnut soil (Class III)
        - Rock type: Weathered sandstone (Class III)
        
        Step 1: Soil Quality (QBi)
        - From Table S2: Class III (Chestnut soil)
        - Bonitet score: 70
        - QBi coefficient: 0.70
        
        Step 2: Soil Strength (QSi)
        - From Table S3: Class III (Weathered sandstone)
        - Protodyakonov index: 10
        - QSi coefficient: 0.70
        
        Step 3: Combined Soil Index (Q_soil)
        - Using equal weighting: Q_soil = (QBi + QSi) / 2
        - Q_soil = (0.70 + 0.70) / 2 = 0.70
        
        Interpretation:
        - Soil quality: Moderate (0.70)
        - Soil strength: Moderate (0.70)
        - Overall soil suitability: Moderate (0.70)
        - Suitable for impact with standard mitigation measures
        
        This example demonstrates how soil parameters from Tables S2 and S3
        are combined to assess overall soil suitability for rocket stage impact.
        """
        
        example_path = output_dir / "Soil_Calculation_Worked_Example.txt"
        try:
            with open(example_path, 'w', encoding='utf-8') as f:
                f.write(example_text)
            logger.info(f"[OK] Worked example saved: {example_path}")
            print(f"[OK] Worked example saved: {example_path}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to save worked example: {e}")
            print(f"[ERROR] Worked example: {e}")
    
    def generate_report(self) -> str:
        """Generate processing report."""
        elapsed_time = time.time() - self.start_time
        
        report = f"""
        ============================================
        SOIL TABLES PROCESSING REPORT
        ============================================
        Processing time: {elapsed_time:.2f} seconds
        Log file: logs/soil_tables_processing.log
        
        Files generated:
        - Table_S2_Soil_Quality_Coefficients.xlsx
        - Table_S2_Soil_Quality_Coefficients.csv
        - Table_S2_Soil_Quality_Coefficients.tex
        - Table_S3_Protodyakonov_Strength.xlsx
        - Table_S3_Protodyakonov_Strength.csv
        - Table_S3_Protodyakonov_Strength.tex
        - Soil_Calculation_Worked_Example.txt
        
        Tables created:
        - Table S2: 7 soil quality classes (bonitet methodology)
        - Table S3: 7 soil strength classes (Protodyakonov scale)
        
        Output directory: outputs/supplementary_tables/
        ============================================
        """
        
        return report

def main():
    """Main execution function."""
    print("=" * 70)
    print("TASK 1.2: SOIL COEFFICIENTS TABLES WITH LOGGING")
    print("=" * 70)
    print()
    
    logger.info("[START] Task 1.2 execution started")
    
    # Create generator
    generator = SoilTablesGenerator()
    
    # Create tables
    print("[PROCESS] Creating soil quality table (Table S2)...")
    df_quality = generator.create_soil_quality_table()
    
    print("[PROCESS] Creating soil strength table (Table S3)...")
    df_strength = generator.create_soil_strength_table()
    
    # Save outputs
    output_dir = Path("outputs/supplementary_tables")
    generator.save_tables(df_quality, df_strength, output_dir)
    
    # Create worked example
    print("[PROCESS] Creating worked example...")
    generator.create_worked_example(output_dir)
    
    # Generate report
    report = generator.generate_report()
    report_path = output_dir / "Soil_Tables_Processing_Report.txt"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print()
    print("=" * 70)
    print("[OK] TASK 1.2 COMPLETED SUCCESSFULLY")
    print(f"[INFO] Output directory: {output_dir}")
    print("[INFO] Check logs/soil_tables_processing.log for details")
    print("=" * 70)
    
    # Print summary
    print("\n[SUMMARY]:")
    print(f"   - Table S2: {len(df_quality)} soil quality classes")
    print(f"   - Table S3: {len(df_strength)} soil strength classes")
    print(f"   - Files generated: 7 files")
    print()

if __name__ == "__main__":
    main()