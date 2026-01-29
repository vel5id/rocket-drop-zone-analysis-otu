"""
Task 3.9: Supplementary Materials Package

Implements БЛОК 3, Task 3.9 from revision plan.
Creates a comprehensive supplementary materials package including:
1. All Tables S1-S7
2. All Figures S1-S2
3. README with file descriptions
4. ZIP archive for distribution
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
import sys
import time
import json
import shutil
import zipfile
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'supplementary_materials_package.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SupplementaryMaterialsPackage:
    """
    Creates supplementary materials package for OTU methodology.
    """
    
    def __init__(self):
        self.start_time = time.time()
        logger.info("[INIT] SupplementaryMaterialsPackage initialized")
        
        # Define directories
        self.base_dir = Path("outputs")
        self.supplementary_dir = self.base_dir / "supplementary_materials"
        self.supplementary_dir.mkdir(parents=True, exist_ok=True)
        
        # Subdirectories
        self.tables_dir = self.supplementary_dir / "tables"
        self.figures_dir = self.supplementary_dir / "figures"
        self.data_dir = self.supplementary_dir / "data"
        
        for dir_path in [self.tables_dir, self.figures_dir, self.data_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # File inventory
        self.file_inventory = []
        
        logger.info("[INFO] Supplementary materials package creator ready")
    
    def collect_tables_s1_s7(self):
        """Collect all supplementary tables S1-S7."""
        logger.info("[COLLECT] Collecting supplementary tables S1-S7")
        
        tables = [
            {
                "number": "S1",
                "name": "Sentinel-2 Scene Metadata",
                "description": "Complete list of Sentinel-2 scenes used in the analysis with acquisition dates, cloud cover, and quality flags.",
                "expected_files": [
                    "Table_S1_Sentinel2_Scenes.xlsx",
                    "Table_S1_Sentinel2_Scenes.csv",
                    "Table_S1_Sentinel2_Scenes.tex"
                ]
            },
            {
                "number": "S2",
                "name": "Soil Quality Coefficients (Bonitet)",
                "description": "Bonitet correction coefficients for different soil types used in Q_SI calculation.",
                "expected_files": [
                    "Table_S2_Soil_Quality_Coefficients.xlsx",
                    "Table_S2_Soil_Quality_Coefficients.csv",
                    "Table_S2_Soil_Quality_Coefficients.tex"
                ]
            },
            {
                "number": "S3",
                "name": "Protodyakonov Strength Coefficients",
                "description": "Protodyakonov strength coefficients for different soil types used in soil strength assessment.",
                "expected_files": [
                    "Table_S3_Protodyakonov_Strength.xlsx",
                    "Table_S3_Protodyakonov_Strength.csv",
                    "Table_S3_Protodyakonov_Strength.tex"
                ]
            },
            {
                "number": "S4",
                "name": "Sensitivity Analysis Results",
                "description": "Comparative sensitivity metrics from OAT, Monte Carlo, and Sobol analyses.",
                "expected_files": [
                    "Table_S4_Sensitivity_Comparison.xlsx",
                    "Table_S4_Sensitivity_Comparison.csv",
                    "Table_S4_Sensitivity_Comparison.tex"
                ]
            },
            {
                "number": "S5",
                "name": "OTU Distribution by Stability Class",
                "description": "Distribution of OTUs across stability classes with area statistics and mean Q_OTU values.",
                "expected_files": [
                    "Table_S5_OTU_Distribution.xlsx",
                    "Table_S5_OTU_Distribution.csv",
                    "Table_S5_OTU_Distribution.tex"
                ]
            },
            {
                "number": "S6",
                "name": "Weighting Coefficients Rationale",
                "description": "Rationale and literature support for weighting coefficients (k_VI, k_SI, k_BI) used in Q_OTU calculation.",
                "expected_files": [
                    "Table_S6_Weighting_Coefficients.xlsx",
                    "Table_S6_Weighting_Coefficients.csv",
                    "Table_S6_Weighting_Coefficients.tex"
                ]
            },
            {
                "number": "S7",
                "name": "Economic Cost Breakdown",
                "description": "Economic cost breakdown for different OTU stability classes with component costs and savings.",
                "expected_files": [
                    "Table_S7_Economic_Cost_Breakdown.xlsx",
                    "Table_S7_Economic_Cost_Breakdown.csv",
                    "Table_S7_Economic_Cost_Breakdown.tex"
                ]
            }
        ]
        
        # Source directories
        source_dirs = [
            self.base_dir / "supplementary_tables",
            self.base_dir / "sensitivity_analysis",
            self.base_dir / "validation_framework",
            self.base_dir / "economic_analysis"
        ]
        
        # Collect and copy tables
        collected_tables = []
        
        for table in tables:
            table_collected = {
                "number": table["number"],
                "name": table["name"],
                "description": table["description"],
                "files": []
            }
            
            for expected_file in table["expected_files"]:
                # Try to find the file in source directories
                found = False
                for source_dir in source_dirs:
                    source_path = source_dir / expected_file
                    if source_path.exists():
                        # Copy to supplementary materials directory
                        dest_path = self.tables_dir / expected_file
                        shutil.copy2(source_path, dest_path)
                        
                        table_collected["files"].append({
                            "filename": expected_file,
                            "size_kb": round(source_path.stat().st_size / 1024, 1),
                            "format": expected_file.split('.')[-1].upper()
                        })
                        
                        self.file_inventory.append({
                            "type": "table",
                            "number": table["number"],
                            "filename": expected_file,
                            "path": str(dest_path.relative_to(self.supplementary_dir)),
                            "size_kb": round(source_path.stat().st_size / 1024, 1)
                        })
                        
                        found = True
                        logger.info(f"[OK] Collected {expected_file}")
                        break
                
                if not found:
                    logger.warning(f"[WARNING] Table file not found: {expected_file}")
            
            collected_tables.append(table_collected)
        
        # Save table metadata
        tables_metadata_path = self.supplementary_dir / "tables_metadata.json"
        with open(tables_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(collected_tables, f, indent=2)
        
        logger.info(f"[OK] Collected {len(collected_tables)} tables with {sum(len(t['files']) for t in collected_tables)} files")
        return collected_tables
    
    def collect_figures_s1_s2(self):
        """Collect all supplementary figures S1-S2."""
        logger.info("[COLLECT] Collecting supplementary figures S1-S2")
        
        figures = [
            {
                "number": "S1",
                "name": "Comprehensive Sensitivity Analysis",
                "description": "Combined visualization of sensitivity analysis results from OAT, Monte Carlo, and Sobol methods.",
                "expected_files": [
                    "Figure_S1_Sensitivity_Analysis.png",
                    "Figure_S1_Sensitivity_Analysis.pdf",
                    "Figure_S1_Sensitivity_Analysis.svg"
                ]
            },
            {
                "number": "S2",
                "name": "Validation Framework Workflow",
                "description": "Detailed workflow diagram of the validation framework showing data collection, analysis, and reporting steps.",
                "expected_files": [
                    "Figure_S2_Validation_Workflow.png",
                    "Figure_S2_Validation_Workflow.pdf"
                ]
            }
        ]
        
        # Source directories
        source_dirs = [
            self.base_dir / "figures",
            self.base_dir / "sensitivity_analysis" / "plots",
            self.base_dir / "validation_framework"
        ]
        
        # Collect and copy figures
        collected_figures = []
        
        for figure in figures:
            figure_collected = {
                "number": figure["number"],
                "name": figure["name"],
                "description": figure["description"],
                "files": []
            }
            
            for expected_file in figure["expected_files"]:
                # Try to find the file in source directories
                found = False
                for source_dir in source_dirs:
                    source_path = source_dir / expected_file
                    if source_path.exists():
                        # Copy to supplementary materials directory
                        dest_path = self.figures_dir / expected_file
                        shutil.copy2(source_path, dest_path)
                        
                        figure_collected["files"].append({
                            "filename": expected_file,
                            "size_kb": round(source_path.stat().st_size / 1024, 1),
                            "format": expected_file.split('.')[-1].upper(),
                            "dimensions": self._get_image_dimensions(source_path) if source_path.suffix.lower() in ['.png', '.jpg', '.jpeg'] else "N/A"
                        })
                        
                        self.file_inventory.append({
                            "type": "figure",
                            "number": figure["number"],
                            "filename": expected_file,
                            "path": str(dest_path.relative_to(self.supplementary_dir)),
                            "size_kb": round(source_path.stat().st_size / 1024, 1)
                        })
                        
                        found = True
                        logger.info(f"[OK] Collected {expected_file}")
                        break
                
                if not found:
                    # Check with alternative naming
                    alt_names = [
                        f"Figure_{figure['number']}_*.png",
                        f"Figure_{figure['number']}_*.pdf",
                        f"figure_{figure['number'].lower()}*.png"
                    ]
                    
                    for alt_pattern in alt_names:
                        for source_dir in source_dirs:
                            for alt_path in source_dir.glob(alt_pattern):
                                dest_path = self.figures_dir / expected_file
                                shutil.copy2(alt_path, dest_path)
                                
                                figure_collected["files"].append({
                                    "filename": expected_file,
                                    "size_kb": round(alt_path.stat().st_size / 1024, 1),
                                    "format": expected_file.split('.')[-1].upper(),
                                    "source_file": alt_path.name
                                })
                                
                                self.file_inventory.append({
                                    "type": "figure",
                                    "number": figure["number"],
                                    "filename": expected_file,
                                    "path": str(dest_path.relative_to(self.supplementary_dir)),
                                    "size_kb": round(alt_path.stat().st_size / 1024, 1),
                                    "source": alt_path.name
                                })
                                
                                found = True
                                logger.info(f"[OK] Collected {alt_path.name} as {expected_file}")
                                break
                            if found:
                                break
                        if found:
                            break
            
            collected_figures.append(figure_collected)
        
        # Save figure metadata
        figures_metadata_path = self.supplementary_dir / "figures_metadata.json"
        with open(figures_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(collected_figures, f, indent=2)
        
        logger.info(f"[OK] Collected {len(collected_figures)} figures with {sum(len(f['files']) for f in collected_figures)} files")
        return collected_figures
    
    def _get_image_dimensions(self, image_path: Path) -> str:
        """Get image dimensions if possible."""
        try:
            from PIL import Image
            with Image.open(image_path) as img:
                width, height = img.size
                return f"{width}x{height} pixels"
        except (ImportError, Exception):
            return "Unknown"
    
    def collect_additional_materials(self):
        """Collect additional supplementary materials."""
        logger.info("[COLLECT] Collecting additional supplementary materials")
        
        additional_materials = []
        
        # Collect validation framework documents
        validation_dir = self.base_dir / "validation_framework"
        if validation_dir.exists():
            for doc_file in validation_dir.glob("*.json"):
                dest_path = self.data_dir / doc_file.name
                shutil.copy2(doc_file, dest_path)
                
                additional_materials.append({
                    "type": "validation_data",
                    "filename": doc_file.name,
                    "description": "Validation framework design and results"
                })
                
                self.file_inventory.append({
                    "type": "data",
                    "category": "validation",
                    "filename": doc_file.name,
                    "path": str(dest_path.relative_to(self.supplementary_dir)),
                    "size_kb": round(doc_file.stat().st_size / 1024, 1)
                })
        
        # Collect sensitivity analysis data
        sensitivity_dir = self.base_dir / "sensitivity_analysis"
        if sensitivity_dir.exists():
            for data_file in sensitivity_dir.glob("*.json"):
                dest_path = self.data_dir / data_file.name
                shutil.copy2(data_file, dest_path)
                
                additional_materials.append({
                    "type": "sensitivity_data",
                    "filename": data_file.name,
                    "description": "Sensitivity analysis parameters and results"
                })
                
                self.file_inventory.append({
                    "type": "data",
                    "category": "sensitivity",
                    "filename": data_file.name,
                    "path": str(dest_path.relative_to(self.supplementary_dir)),
                    "size_kb": round(data_file.stat().st_size / 1024, 1)
                })
        
        # Collect uncertainty analysis data
        uncertainty_dir = self.base_dir / "uncertainty_analysis"
        if uncertainty_dir.exists():
            for data_file in uncertainty_dir.glob("*.json"):
                dest_path = self.data_dir / data_file.name
                shutil.copy2(data_file, dest_path)
                
                additional_materials.append({
                    "type": "uncertainty_data",
                    "filename": data_file.name,
                    "description": "Uncertainty analysis results"
                })
        
        logger.info(f"[OK] Collected {len(additional_materials)} additional material files")
        return additional_materials
    
    def create_readme_file(self):
        """Create README file for supplementary materials."""
        logger.info("[CREATE] Creating README file")
        
        readme_content = f"""# Supplementary Materials for "Optimal Take-off Unit Methodology for Rocket Stage Impact Zone Analysis"

## Overview

This package contains supplementary materials for the manuscript "Optimal Take-off Unit (OTU) Methodology for Rocket Stage Impact Zone Analysis". The materials include supplementary tables, figures, and data files referenced in the manuscript.

## Package Information

- **Package Version**: 1.0
- **Creation Date**: {datetime.now().strftime('%Y-%m-%d')}
- **Total Files**: {len(self.file_inventory)}
- **Total Size**: {sum(item['size_kb'] for item in self.file_inventory) / 1024:.1f} MB

## File Structure

```
supplementary_materials/
├── README.md (this file)
├── tables_metadata.json (metadata for all tables)
├── figures_metadata.json (metadata for all figures)
├── tables/ (Supplementary Tables S1-S7)
│   ├── Table_S1_Sentinel2_Scenes.xlsx/csv/tex
│   ├── Table_S2_Soil_Quality_Coefficients.xlsx/csv/tex
│   ├── Table_S3_Protodyakonov_Strength.xlsx/csv/tex
│   ├── Table_S4_Sensitivity_Comparison.xlsx/csv/tex
│   ├── Table_S5_OTU_Distribution.xlsx/csv/tex
│   ├── Table_S6_Weighting_Coefficients.xlsx/csv/tex
│   └── Table_S7_Economic_Cost_Breakdown.xlsx/csv/tex
├── figures/ (Supplementary Figures S1-S2)
│   ├── Figure_S1_Sensitivity_Analysis.png/pdf/svg
│   └── Figure_S2_Validation_Workflow.png/pdf
└── data/ (Additional data files)
    ├── validation_framework_*.json
    ├── sensitivity_analysis_*.json
    └── uncertainty_analysis_*.json
```

## Supplementary Tables

### Table S1: Sentinel-2 Scene Metadata
Complete list of Sentinel-2 scenes used in the analysis with acquisition dates, cloud cover, and quality flags.

### Table S2: Soil Quality Coefficients (Bonitet)
Bonitet correction coefficients for different soil types used in Q_SI calculation.

### Table S3: Protodyakonov Strength Coefficients
Protodyakonov strength coefficients for different soil types used in soil strength assessment.

### Table S4: Sensitivity Analysis Results
Comparative sensitivity metrics from OAT, Monte Carlo, and Sobol analyses.

### Table S5: OTU Distribution by Stability Class
Distribution of OTUs across stability classes with area statistics and mean Q_OTU values.

### Table S6: Weighting Coefficients Rationale
Rationale and literature support for weighting coefficients (k_VI, k_SI, k_BI) used in Q_OTU calculation.

### Table S7: Economic Cost Breakdown
Economic cost breakdown for different OTU stability classes with component costs and savings.

## Supplementary Figures

### Figure S1: Comprehensive Sensitivity Analysis
Combined visualization of sensitivity analysis results from OAT, Monte Carlo, and Sobol methods. Shows parameter importance rankings, correlation patterns, and interaction effects.

### Figure S2: Validation Framework Workflow
Detailed workflow diagram of the validation framework showing data collection protocols, validation metrics calculation, and success criteria evaluation.

## Data Files

Additional JSON files contain:

- **Validation framework design**: Detailed specifications of validation metrics, success criteria, and evaluation protocols.
- **Sensitivity analysis parameters**: Complete parameter sets for OAT, Monte Carlo, and Sobol sensitivity analyses.
- **Uncertainty quantification**: Statistical distributions and uncertainty propagation results.
- **Economic cost models**: Detailed cost component breakdowns and scenario assumptions.

## Usage Instructions

1. **Extract the ZIP archive**: Use any standard ZIP extraction tool.
2. **Navigate to the supplementary_materials directory**.
3. **Review README.md** for detailed file descriptions.
4. **Open tables/** for Excel/CSV/LaTeX versions of supplementary tables.
5. **Open figures/** for high-resolution images of supplementary figures.
6. **Open data/** for additional JSON data files.

## Citation

When using these supplementary materials, please cite the main manuscript:

> Author et al. (2024). "Optimal Take-off Unit Methodology for Rocket Stage Impact Zone Analysis". *Journal of Aerospace Engineering*.

## Contact

For questions about these supplementary materials, contact:
- Research Team: research@example.com
- Data Repository: https://github.com/example/otu-methodology

## License

These supplementary materials are provided under the Creative Commons Attribution 4.0 International License (CC BY 4.0).

---

*This package was automatically generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.*
"""
        
        readme_path = self.supplementary_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        self.file_inventory.append({
            "type": "documentation",
            "filename": "README.md",
            "path": "README.md",
            "size_kb": round(readme_path.stat().st_size / 1024, 1)
        })
        
        logger.info(f"[OK] Created README file: {readme_path}")
        return readme_path
    
    def create_file_manifest(self):
        """Create Excel file manifest with metadata for all files."""
        logger.info("[CREATE] Creating file manifest")
        
        if not self.file_inventory:
            logger.warning("[WARNING] No files in inventory, skipping manifest creation")
            return None
        
        # Convert inventory to DataFrame
        df = pd.DataFrame(self.file_inventory)
        
        # Add additional metadata columns
        df['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        df['checksum'] = ''  # Placeholder for checksum
        
        # Reorder columns
        columns_order = ['type', 'number', 'category', 'filename', 'path', 'size_kb', 'timestamp', 'checksum']
        existing_columns = [col for col in columns_order if col in df.columns]
        df = df[existing_columns]
        
        # Save to Excel
        manifest_path = self.supplementary_dir / "File_Manifest.xlsx"
        
        with pd.ExcelWriter(manifest_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='File_Manifest', index=False)
            
            # Add summary sheet
            summary_data = {
                'Metric': ['Total Files', 'Total Size (MB)', 'Tables Count', 'Figures Count', 'Data Files Count'],
                'Value': [
                    len(df),
                    round(df['size_kb'].sum() / 1024, 2),
                    len(df[df['type'] == 'table']),
                    len(df[df['type'] == 'figure']),
                    len(df[df['type'] == 'data'])
                ]
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Add file type distribution
            type_dist = df['type'].value_counts().reset_index()
            type_dist.columns = ['File Type', 'Count']
            type_dist.to_excel(writer, sheet_name='Type_Distribution', index=False)
        
        self.file_inventory.append({
            "type": "manifest",
            "filename": "File_Manifest.xlsx",
            "path": "File_Manifest.xlsx",
            "size_kb": round(manifest_path.stat().st_size / 1024, 1)
        })
        
        logger.info(f"[OK] Created file manifest: {manifest_path}")
        return manifest_path
    
    def create_zip_archive(self):
        """Create ZIP archive of all supplementary materials."""
        logger.info("[CREATE] Creating ZIP archive")
        
        zip_path = self.base_dir / "Supplementary_Materials.zip"
        
        # Remove existing ZIP if present
        if zip_path.exists():
            zip_path.unlink()
            logger.info("[INFO] Removed existing ZIP archive")
        
        # Create ZIP archive
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from supplementary directory
            for file_path in self.supplementary_dir.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.supplementary_dir.parent)
                    zipf.write(file_path, arcname)
                    logger.debug(f"[ZIP] Added: {arcname}")
            
            # Also add README and manifest from supplementary directory
            readme_path = self.supplementary_dir / "README.md"
            if readme_path.exists():
                zipf.write(readme_path, readme_path.relative_to(self.supplementary_dir.parent))
            
            manifest_path = self.supplementary_dir / "File_Manifest.xlsx"
            if manifest_path.exists():
                zipf.write(manifest_path, manifest_path.relative_to(self.supplementary_dir.parent))
        
        zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
        
        self.file_inventory.append({
            "type": "archive",
            "filename": "Supplementary_Materials.zip",
            "path": str(zip_path.relative_to(self.base_dir.parent)),
            "size_kb": round(zip_path.stat().st_size / 1024, 1)
        })
        
        logger.info(f"[OK] Created ZIP archive: {zip_path} ({zip_size_mb:.1f} MB)")
        return zip_path
    
    def run(self):
        """Run complete supplementary materials package creation."""
        logger.info("[RUN] Starting supplementary materials package creation")
        
        try:
            # Step 1: Collect all materials
            tables = self.collect_tables_s1_s7()
            figures = self.collect_figures_s1_s2()
            additional = self.collect_additional_materials()
            
            # Step 2: Create documentation
            readme_path = self.create_readme_file()
            manifest_path = self.create_file_manifest()
            
            # Step 3: Create ZIP archive
            zip_path = self.create_zip_archive()
            
            # Step 4: Generate completion report
            elapsed_time = time.time() - self.start_time
            
            report = {
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "elapsed_time_seconds": round(elapsed_time, 2),
                "files_collected": len(self.file_inventory),
                "tables_collected": len(tables),
                "figures_collected": len(figures),
                "additional_materials": len(additional),
                "zip_archive_size_mb": round(zip_path.stat().st_size / (1024 * 1024), 2),
                "output_files": [
                    str(readme_path) if readme_path else None,
                    str(manifest_path) if manifest_path else None,
                    str(zip_path) if zip_path else None
                ]
            }
            
            # Save completion report
            report_path = self.supplementary_dir / "completion_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"[SUCCESS] Supplementary materials package created successfully in {elapsed_time:.1f} seconds")
            logger.info(f"[INFO] Total files: {len(self.file_inventory)}")
            logger.info(f"[INFO] ZIP archive: {zip_path}")
            
            return report
            
        except Exception as e:
            logger.error(f"[ERROR] Failed to create supplementary materials package: {str(e)}")
            logger.exception(e)
            
            error_report = {
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "elapsed_time_seconds": round(time.time() - self.start_time, 2)
            }
            
            error_path = self.supplementary_dir / "error_report.json"
            with open(error_path, 'w', encoding='utf-8') as f:
                json.dump(error_report, f, indent=2)
            
            raise

def main():
    """Main entry point for the script."""
    print("=" * 70)
    print("Supplementary Materials Package Creator")
    print("Task 3.9 from IMPLEMENTATION_ROADMAP.md")
    print("=" * 70)
    
    try:
        # Create package
        package = SupplementaryMaterialsPackage()
        report = package.run()
        
        print("\n" + "=" * 70)
        print("SUCCESS: Supplementary materials package created!")
        print("=" * 70)
        print(f"• Total files collected: {report['files_collected']}")
        print(f"• Tables: {report['tables_collected']}")
        print(f"• Figures: {report['figures_collected']}")
        print(f"• ZIP archive size: {report['zip_archive_size_mb']} MB")
        print(f"• Elapsed time: {report['elapsed_time_seconds']} seconds")
        print(f"• Output directory: {package.supplementary_dir}")
        print(f"• ZIP archive: outputs/Supplementary_Materials.zip")
        print("=" * 70)
        
        return 0
        
    except Exception as e:
        print(f"\n[ERROR] Failed to create supplementary materials package: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
