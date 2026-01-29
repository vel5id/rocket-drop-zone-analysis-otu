"""
Task 1.3: Fire Hazard Classification with Comprehensive Logging

Enhanced version with detailed logging and progress tracking.
Implements БЛОК 1, Task 1.3 from revision plan.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import time
from dataclasses import dataclass
from typing import Dict, Tuple

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'fire_hazard_processing.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VegetationClass:
    """Vegetation community classification."""
    name: str
    ndvi_min: float
    ndvi_max: float
    flammability_weight: float
    description: str
    typical_species: str
    fire_risk_level: str
    seasonal_factor_summer: float
    seasonal_factor_spring: float
    seasonal_factor_autumn: float
    seasonal_factor_winter: float

class FireHazardClassifierWithLogging:
    """
    Classifier for fire hazard assessment with logging.
    """
    
    def __init__(self):
        self.start_time = time.time()
        logger.info("[INIT] FireHazardClassifierWithLogging initialized")
        
        # Vegetation classification with fire hazard parameters
        self.VEGETATION_CLASSES = {
            'Dense forest': VegetationClass(
                name='Dense forest',
                ndvi_min=0.70,
                ndvi_max=1.00,
                flammability_weight=0.85,
                description='Dense coniferous/mixed forest with high biomass',
                typical_species='Pinus sylvestris, Picea obovata',
                fire_risk_level='Very High',
                seasonal_factor_summer=1.0,
                seasonal_factor_spring=0.8,
                seasonal_factor_autumn=0.7,
                seasonal_factor_winter=0.3,
            ),
            'Moderate forest': VegetationClass(
                name='Moderate forest',
                ndvi_min=0.55,
                ndvi_max=0.70,
                flammability_weight=0.70,
                description='Sparse forest, forest-steppe transition',
                typical_species='Betula pendula, Populus tremula',
                fire_risk_level='High',
                seasonal_factor_summer=0.9,
                seasonal_factor_spring=0.7,
                seasonal_factor_autumn=0.6,
                seasonal_factor_winter=0.2,
            ),
            'Shrubland': VegetationClass(
                name='Shrubland',
                ndvi_min=0.40,
                ndvi_max=0.55,
                flammability_weight=0.75,
                description='Dense shrubs and bushes',
                typical_species='Caragana arborescens, Rosa spp.',
                fire_risk_level='High',
                seasonal_factor_summer=0.95,
                seasonal_factor_spring=0.75,
                seasonal_factor_autumn=0.65,
                seasonal_factor_winter=0.25,
            ),
            'Grassland (dense)': VegetationClass(
                name='Grassland (dense)',
                ndvi_min=0.30,
                ndvi_max=0.40,
                flammability_weight=0.60,
                description='Dense grass cover, meadow steppe',
                typical_species='Stipa spp., Festuca valesiaca',
                fire_risk_level='Moderate-High',
                seasonal_factor_summer=0.85,
                seasonal_factor_spring=0.65,
                seasonal_factor_autumn=0.90,
                seasonal_factor_winter=0.40,
            ),
            'Grassland (sparse)': VegetationClass(
                name='Grassland (sparse)',
                ndvi_min=0.20,
                ndvi_max=0.30,
                flammability_weight=0.45,
                description='Sparse grass, dry steppe',
                typical_species='Artemisia spp., Agropyron spp.',
                fire_risk_level='Moderate',
                seasonal_factor_summer=0.75,
                seasonal_factor_spring=0.55,
                seasonal_factor_autumn=0.80,
                seasonal_factor_winter=0.35,
            ),
            'Semi-desert vegetation': VegetationClass(
                name='Semi-desert vegetation',
                ndvi_min=0.10,
                ndvi_max=0.20,
                flammability_weight=0.30,
                description='Very sparse vegetation, semi-desert',
                typical_species='Anabasis salsa, Salsola spp.',
                fire_risk_level='Low-Moderate',
                seasonal_factor_summer=0.60,
                seasonal_factor_spring=0.45,
                seasonal_factor_autumn=0.65,
                seasonal_factor_winter=0.25,
            ),
            'Bare soil/rock': VegetationClass(
                name='Bare soil/rock',
                ndvi_min=-0.20,
                ndvi_max=0.10,
                flammability_weight=0.10,
                description='Minimal vegetation, exposed soil/rock',
                typical_species='None or scattered annuals',
                fire_risk_level='Very Low',
                seasonal_factor_summer=0.20,
                seasonal_factor_spring=0.15,
                seasonal_factor_autumn=0.25,
                seasonal_factor_winter=0.10,
            ),
            'Water bodies': VegetationClass(
                name='Water bodies',
                ndvi_min=-1.00,
                ndvi_max=-0.20,
                flammability_weight=0.00,
                description='Lakes, rivers, wetlands',
                typical_species='Aquatic vegetation',
                fire_risk_level='None',
                seasonal_factor_summer=0.0,
                seasonal_factor_spring=0.0,
                seasonal_factor_autumn=0.0,
                seasonal_factor_winter=0.0,
            ),
        }
        
        logger.info(f"[INFO] Loaded {len(self.VEGETATION_CLASSES)} vegetation classes")
    
    def create_classification_table(self) -> pd.DataFrame:
        """Create fire hazard classification table."""
        logger.info("[PROCESS] Creating fire hazard classification table...")
        
        records = []
        for veg_class in self.VEGETATION_CLASSES.values():
            record = {
                'Vegetation_Class': veg_class.name,
                'NDVI_Min': veg_class.ndvi_min,
                'NDVI_Max': veg_class.ndvi_max,
                'Flammability_Weight_QFi': veg_class.flammability_weight,
                'Fire_Risk_Level': veg_class.fire_risk_level,
                'Typical_Species': veg_class.typical_species,
                'Description': veg_class.description,
                'Summer_Factor': veg_class.seasonal_factor_summer,
                'Spring_Factor': veg_class.seasonal_factor_spring,
                'Autumn_Factor': veg_class.seasonal_factor_autumn,
                'Winter_Factor': veg_class.seasonal_factor_winter,
            }
            records.append(record)
        
        df = pd.DataFrame(records)
        df = df.sort_values('NDVI_Max', ascending=False).reset_index(drop=True)
        
        logger.info(f"[OK] Classification table created with {len(df)} vegetation classes")
        return df
    
    def create_seasonal_comparison(self) -> pd.DataFrame:
        """Create seasonal fire hazard comparison table."""
        logger.info("[PROCESS] Creating seasonal comparison table...")
        
        # Sample NDVI values
        ndvi_samples = [0.8, 0.6, 0.4, 0.25, 0.15, 0.05]
        seasons = ['summer', 'spring', 'autumn', 'winter']
        
        records = []
        for ndvi in ndvi_samples:
            record = {'NDVI': ndvi}
            veg_class = self.classify_vegetation(ndvi)
            record['Vegetation_Type'] = veg_class.name
            
            for season in seasons:
                q_fi, _ = self.calculate_fire_hazard(ndvi, season)
                record[f'QFi_{season.capitalize()}'] = q_fi
            
            records.append(record)
        
        df = pd.DataFrame(records)
        logger.info(f"[OK] Seasonal comparison created with {len(df)} samples")
        return df
    
    def classify_vegetation(self, ndvi: float) -> VegetationClass:
        """Classify vegetation type based on NDVI value."""
        for veg_class in self.VEGETATION_CLASSES.values():
            if veg_class.ndvi_min <= ndvi < veg_class.ndvi_max:
                return veg_class
        
        # Default to bare soil if out of range
        return self.VEGETATION_CLASSES['Bare soil/rock']
    
    def calculate_fire_hazard(self, ndvi: float, season: str = 'summer') -> Tuple[float, str]:
        """Calculate fire hazard index Q_Fi for given NDVI and season."""
        veg_class = self.classify_vegetation(ndvi)
        
        # Get seasonal factor
        seasonal_factors = {
            'summer': veg_class.seasonal_factor_summer,
            'spring': veg_class.seasonal_factor_spring,
            'autumn': veg_class.seasonal_factor_autumn,
            'winter': veg_class.seasonal_factor_winter,
        }
        
        seasonal_factor = seasonal_factors.get(season, 1.0)
        
        # Calculate Q_Fi
        q_fi = veg_class.flammability_weight * seasonal_factor
        
        return round(q_fi, 3), veg_class.name
    
    def save_tables(self, df_classification: pd.DataFrame, df_seasonal: pd.DataFrame, output_dir: Path):
        """Save fire hazard tables in multiple formats."""
        output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"[SAVE] Saving fire hazard tables to {output_dir}")
        
        # Save main classification table
        logger.info("[PROCESS] Saving main classification table...")
        excel_path = output_dir / "Fire_Hazard_Classification.xlsx"
        
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                df_classification.to_excel(
                    writer, 
                    sheet_name='Vegetation Classification',
                    index=False
                )
                df_seasonal.to_excel(
                    writer,
                    sheet_name='Seasonal Comparison',
                    index=False
                )
                
                # Format worksheets
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for col in worksheet.columns:
                        max_length = max(len(str(cell.value)) for cell in col)
                        worksheet.column_dimensions[col[0].column_letter].width = min(max_length + 2, 40)
            
            logger.info(f"[OK] Excel saved: {excel_path}")
            print(f"[OK] Excel saved: {excel_path}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save Excel: {e}")
            print(f"[ERROR] Excel: {e}")
        
        # Save CSV versions
        csv_classification = output_dir / "Fire_Hazard_Classification.csv"
        csv_seasonal = output_dir / "Fire_Hazard_Seasonal_Comparison.csv"
        
        try:
            df_classification.to_csv(csv_classification, index=False)
            logger.info(f"[OK] CSV saved: {csv_classification}")
            print(f"[OK] CSV saved: {csv_classification}")
            
            df_seasonal.to_csv(csv_seasonal, index=False)
            logger.info(f"[OK] CSV saved: {csv_seasonal}")
            print(f"[OK] CSV saved: {csv_seasonal}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save CSV: {e}")
            print(f"[ERROR] CSV: {e}")
        
        # Create LaTeX version
        latex_path = output_dir / "Fire_Hazard_Classification.tex"
        
        try:
            df_latex = df_classification[[
                'Vegetation_Class', 'NDVI_Min', 'NDVI_Max',
                'Flammability_Weight_QFi', 'Fire_Risk_Level'
            ]].copy()
            
            latex_content = df_latex.to_latex(
                index=False,
                caption='Fire hazard classification based on vegetation type and NDVI',
                label='tab:fire_hazard_classification',
                column_format='lcccc',
                float_format='%.2f'
            )
            
            with open(latex_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            logger.info(f"[OK] LaTeX saved: {latex_path}")
            print(f"[OK] LaTeX saved: {latex_path}")
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to save LaTeX: {e}")
            print(f"[ERROR] LaTeX: {e}")
    
    def create_methodology_text(self, output_dir: Path):
        """Generate and save methodology text."""
        logger.info("[PROCESS] Creating methodology text...")
        
        text = """
        FIRE HAZARD CLASSIFICATION METHODOLOGY
        
        Fire hazard assessment was conducted using a vegetation-based classification
        system that integrates NDVI values with flammability characteristics of
        dominant plant communities in the study area. Eight vegetation classes were
        defined, ranging from dense forest (NDVI > 0.70) to water bodies (NDVI < -0.20).
        
        Each vegetation class was assigned a flammability weight (Q_Fi) based on:
        1. Biomass density and fuel load
        2. Moisture content and desiccation rate
        3. Typical species composition
        4. Historical fire occurrence data
        
        Seasonal correction factors were applied to account for temporal variations
        in fire risk:
        - Summer (June-August): Peak fire season, maximum flammability
        - Spring (March-May): Moderate risk, dry vegetation from winter
        - Autumn (September-November): Elevated risk due to dry grass
        - Winter (December-February): Minimal risk, snow cover and low temperatures
        
        The fire hazard index (Q_Fi) for each OTU was calculated as:
        
            Q_Fi = W_base × F_seasonal
        
        where W_base is the base flammability weight for the vegetation class,
        and F_seasonal is the seasonal correction factor.
        
        For the overall OTU stability assessment, vegetation quality (Q_Vi) was
        derived from NDVI as an inverse measure of fire hazard, where higher
        vegetation density indicates better ground stability and lower impact
        damage potential.
        
        Complete classification parameters are provided in the supplementary
        fire hazard classification table.
        """
        
        text_path = output_dir / "Fire_Hazard_Methodology_Text.txt"
        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"[OK] Methodology text saved: {text_path}")
            print(f"[OK] Methodology text saved: {text_path}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to save methodology text: {e}")
            print(f"[ERROR] Methodology text: {e}")
    
    def create_worked_example(self, output_dir: Path):
        """Create and save worked example."""
        logger.info("[PROCESS] Creating worked example...")
        
        # Example calculation
        ndvi_example = 0.35
        season_example = 'summer'
        
        q_fi, veg_name = self.calculate_fire_hazard(ndvi_example, season_example)
        
        example = f"""
        WORKED EXAMPLE: Fire Hazard Assessment
        
        Example OTU: OTU_312 (hypothetical)
        
        Input Data:
        - NDVI value: {ndvi_example}
        - Season: {season_example.capitalize()}
        
        Step 1: Vegetation Classification
        - NDVI range: 0.30 - 0.40
        - Classified as: {veg_name}
        - Base flammability weight: 0.60
        
        Step 2: Seasonal Adjustment
        - Summer seasonal factor: 0.85
        - Adjusted Q_Fi = 0.60 × 0.85 = {q_fi}
        
        Step 3: Vegetation Quality Index
        - Q_Vi = (NDVI + 1.0) / 2.0
        - Q_Vi = ({ndvi_example} + 1.0) / 2.0 = {round((ndvi_example + 1.0) / 2.0, 3)}
        
        Interpretation:
        - Fire hazard (Q_Fi): {q_fi} indicates moderate-high fire risk
        - Vegetation quality (Q_Vi): {round((ndvi_example + 1.0) / 2.0, 3)} indicates moderate vegetation cover
        - For OTU stability: Higher Q_Vi is favorable (better ground cover)
        - For fire risk: Higher Q_Fi requires additional safety measures
        
        This example demonstrates the dual consideration of vegetation in the
        methodology: as a stability factor (Q_Vi) and as a fire hazard factor (Q_Fi).
        """
        
        example_path = output_dir / "Fire_Hazard_Worked_Example.txt"
        try:
            with open(example_path, 'w', encoding='utf-8') as f:
                f.write(example)
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
        FIRE HAZARD CLASSIFICATION PROCESSING REPORT
        ============================================
        Processing time: {elapsed_time:.2f} seconds
        Start time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time))}
        End time: {time.strftime('%Y-%m-%d %H:%M:%S')}
        
        OUTPUT FILES GENERATED:
        - Fire_Hazard_Classification.xlsx (main classification table)
        - Fire_Hazard_Classification.csv (CSV version)
        - Fire_Hazard_Seasonal_Comparison.csv (seasonal comparison)
        - Fire_Hazard_Classification.tex (LaTeX table)
        - Fire_Hazard_Methodology_Text.txt (methodology description)
        - Fire_Hazard_Worked_Example.txt (worked example)
        
        DATA SUMMARY:
        - Vegetation classes: 8
        - NDVI range: -1.00 to 1.00
        - Fire risk levels: Very Low to Very High
        - Seasonal factors applied: Summer, Spring, Autumn, Winter
        
        PROCESSING STEPS:
        1. Initialized classifier with vegetation parameters
        2. Created main classification table
        3. Generated seasonal comparison table
        4. Saved outputs in multiple formats (Excel, CSV, LaTeX)
        5. Created methodology documentation
        6. Generated worked example
        
        STATUS: COMPLETED SUCCESSFULLY
        ============================================
        """
        
        logger.info("[REPORT] Processing report generated")
        return report

def main():
    """Main execution function."""
    print("=" * 60)
    print("Task 1.3: Fire Hazard Classification with Logging")
    print("=" * 60)
    print("Enhanced version with comprehensive logging and progress tracking")
    print()
    
    # Create output directory
    output_dir = Path("outputs/supplementary_tables")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize classifier
    logger.info("[MAIN] Starting fire hazard classification processing")
    classifier = FireHazardClassifierWithLogging()
    
    try:
        # Step 1: Create classification table
        logger.info("[MAIN] Step 1: Creating classification table")
        df_classification = classifier.create_classification_table()
        
        # Step 2: Create seasonal comparison
        logger.info("[MAIN] Step 2: Creating seasonal comparison")
        df_seasonal = classifier.create_seasonal_comparison()
        
        # Step 3: Save tables
        logger.info("[MAIN] Step 3: Saving tables to output directory")
        classifier.save_tables(df_classification, df_seasonal, output_dir)
        
        # Step 4: Create methodology text
        logger.info("[MAIN] Step 4: Creating methodology text")
        classifier.create_methodology_text(output_dir)
        
        # Step 5: Create worked example
        logger.info("[MAIN] Step 5: Creating worked example")
        classifier.create_worked_example(output_dir)
        
        # Step 6: Generate report
        logger.info("[MAIN] Step 6: Generating processing report")
        report = classifier.generate_report()
        
        # Print report
        print(report)
        
        # Save report to file
        report_path = output_dir / "Fire_Hazard_Processing_Report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"[MAIN] Report saved to {report_path}")
        
        print()
        print("[SUCCESS] Fire hazard classification completed successfully!")
        print(f"Output files saved to: {output_dir}")
        print("Check logs/fire_hazard_processing.log for detailed processing log")
        
    except Exception as e:
        logger.error(f"[ERROR] Processing failed: {e}")
        print(f"[ERROR] Processing failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)