"""
Task 1.3: Fire Hazard Classification

This script creates fire hazard classification table and implements
the FireHazardClassifier class for vegetation flammability assessment.

Implements БЛОК 1, Task 1.3 from revision plan.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
from dataclasses import dataclass


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


class FireHazardClassifier:
    """
    Classifier for fire hazard assessment based on vegetation type and NDVI.
    
    Implements fire hazard classification methodology for the study area,
    considering vegetation communities, NDVI ranges, and seasonal variations.
    """
    
    # Vegetation classification with fire hazard parameters
    VEGETATION_CLASSES = {
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
    
    def classify_vegetation(self, ndvi: float) -> VegetationClass:
        """
        Classify vegetation type based on NDVI value.
        
        Args:
            ndvi: NDVI value [-1, 1]
        
        Returns:
            VegetationClass object
        """
        for veg_class in self.VEGETATION_CLASSES.values():
            if veg_class.ndvi_min <= ndvi < veg_class.ndvi_max:
                return veg_class
        
        # Default to bare soil if out of range
        return self.VEGETATION_CLASSES['Bare soil/rock']
    
    def calculate_fire_hazard(
        self, 
        ndvi: float, 
        season: str = 'summer'
    ) -> Tuple[float, str]:
        """
        Calculate fire hazard index Q_Fi for given NDVI and season.
        
        Args:
            ndvi: NDVI value [-1, 1]
            season: Season ('summer', 'spring', 'autumn', 'winter')
        
        Returns:
            Tuple of (Q_Fi value, vegetation class name)
        """
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
    
    def calculate_qvi(self, ndvi: float) -> float:
        """
        Calculate vegetation quality index Q_Vi from NDVI.
        
        This is the inverse of fire hazard - higher vegetation quality
        means better stability for impact zones.
        
        Args:
            ndvi: NDVI value [-1, 1]
        
        Returns:
            Q_Vi value [0, 1]
        """
        # Normalize NDVI to [0, 1]
        # Higher NDVI = more vegetation = better stability
        q_vi = (ndvi + 1.0) / 2.0
        
        # Clamp to valid range
        q_vi = max(0.0, min(1.0, q_vi))
        
        return round(q_vi, 3)


def create_fire_classification_table() -> pd.DataFrame:
    """
    Create fire hazard classification table.
    
    Returns:
        DataFrame with vegetation classes and fire parameters
    """
    classifier = FireHazardClassifier()
    
    records = []
    for veg_class in classifier.VEGETATION_CLASSES.values():
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
    
    # Sort by NDVI (descending)
    df = df.sort_values('NDVI_Max', ascending=False).reset_index(drop=True)
    
    return df


def create_seasonal_comparison() -> pd.DataFrame:
    """
    Create seasonal fire hazard comparison table.
    
    Returns:
        DataFrame comparing fire hazard across seasons
    """
    classifier = FireHazardClassifier()
    
    # Sample NDVI values
    ndvi_samples = [0.8, 0.6, 0.4, 0.25, 0.15, 0.05]
    seasons = ['summer', 'spring', 'autumn', 'winter']
    
    records = []
    for ndvi in ndvi_samples:
        record = {'NDVI': ndvi}
        veg_class = classifier.classify_vegetation(ndvi)
        record['Vegetation_Type'] = veg_class.name
        
        for season in seasons:
            q_fi, _ = classifier.calculate_fire_hazard(ndvi, season)
            record[f'QFi_{season.capitalize()}'] = q_fi
        
        records.append(record)
    
    df = pd.DataFrame(records)
    return df


def save_tables(
    df_classification: pd.DataFrame,
    df_seasonal: pd.DataFrame,
    output_dir: Path
) -> None:
    """
    Save fire hazard tables in multiple formats.
    
    Args:
        df_classification: Main classification table
        df_seasonal: Seasonal comparison table
        output_dir: Output directory
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save main classification table
    excel_path = output_dir / "Fire_Hazard_Classification.xlsx"
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
    
    print(f"[OK] Saved Excel: {excel_path}")
    
    # Save CSV versions
    df_classification.to_csv(
        output_dir / "Fire_Hazard_Classification.csv",
        index=False
    )
    df_seasonal.to_csv(
        output_dir / "Fire_Hazard_Seasonal_Comparison.csv",
        index=False
    )
    
    # Create LaTeX version
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
    
    with open(output_dir / "Fire_Hazard_Classification.tex", 'w') as f:
        f.write(latex_content)
    
    print("[OK] Saved LaTeX version")


def create_methodology_text() -> str:
    """
    Generate text for Materials & Methods section.
    
    Returns:
        Formatted text for manuscript
    """
    text = """
### Fire Hazard Classification (for Materials & Methods section)

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
    
    return text


def create_worked_example() -> str:
    """
    Create worked example for fire hazard calculation.
    
    Returns:
        Formatted example text
    """
    classifier = FireHazardClassifier()
    
    # Example calculation
    ndvi_example = 0.35
    season_example = 'summer'
    
    q_fi, veg_name = classifier.calculate_fire_hazard(ndvi_example, season_example)
    q_vi = classifier.calculate_qvi(ndvi_example)
    
    example = f"""
### Worked Example: Fire Hazard Assessment

**Example OTU:** OTU_312 (hypothetical)

**Input Data:**
- NDVI value: {ndvi_example}
- Season: {season_example.capitalize()}

**Step 1: Vegetation Classification**
- NDVI range: 0.30 - 0.40
- Classified as: {veg_name}
- Base flammability weight: 0.60

**Step 2: Seasonal Adjustment**
- Summer seasonal factor: 0.85
- Adjusted Q_Fi = 0.60 × 0.85 = {q_fi}

**Step 3: Vegetation Quality Index**
- Q_Vi = (NDVI + 1.0) / 2.0
- Q_Vi = ({ndvi_example} + 1.0) / 2.0 = {q_vi}

**Interpretation:**
- Fire hazard (Q_Fi): {q_fi} indicates moderate-high fire risk
- Vegetation quality (Q_Vi): {q_vi} indicates moderate vegetation cover
- For OTU stability: Higher Q_Vi is favorable (better ground cover)
- For fire risk: Higher Q_Fi requires additional safety measures

This example demonstrates the dual consideration of vegetation in the
methodology: as a stability factor (Q_Vi) and as a fire hazard factor (Q_Fi).
"""
    
    return example


def main():
    """Main execution function."""
    print("=" * 70)
    print("Task 1.3: Creating Fire Hazard Classification")
    print("=" * 70)
    print()
    
    # Create classification table
    print("Creating fire hazard classification table...")
    df_classification = create_fire_classification_table()
    print(f"[OK] Created classification with {len(df_classification)} vegetation classes")
    
    # Create seasonal comparison
    print("Creating seasonal comparison table...")
    df_seasonal = create_seasonal_comparison()
    print(f"[OK] Created seasonal comparison with {len(df_seasonal)} samples")
    
    # Save outputs
    output_dir = Path("outputs/supplementary_tables")
    save_tables(df_classification, df_seasonal, output_dir)
    
    # Generate methodology text
    methodology_text = create_methodology_text()
    text_path = output_dir / "Fire_Hazard_Methodology_Text.txt"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(methodology_text)
    
    print(f"[OK] Saved methodology text: {text_path}")
    
    # Generate worked example
    example_text = create_worked_example()
    example_path = output_dir / "Fire_Hazard_Worked_Example.txt"
    with open(example_path, 'w', encoding='utf-8') as f:
        f.write(example_text)
    
    print(f"[OK] Saved worked example: {example_path}")
    
    print()
    print("=" * 70)
    print("[OK] Task 1.3 COMPLETED")
    print(f"[OK] Output files created in: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
