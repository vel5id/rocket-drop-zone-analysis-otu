#!/usr/bin/env python3
"""
Create Submission Package Template for MDPI Language Service.
Task 4.5: Professional Editing Service
"""

import zipfile
import json
from datetime import datetime
from pathlib import Path
import shutil

def create_submission_package_template():
    """Create a template submission package for MDPI."""
    
    print("Creating Submission Package Template for MDPI Language Service...")
    
    # Create template directory structure
    template_dir = Path("templates/submission_package")
    template_dir.mkdir(parents=True, exist_ok=True)
    
    # Create package structure
    package_structure = {
        "manuscript": [
            "main_manuscript.docx",
            "abstract.md",
            "introduction.md",
            "methods.md",
            "results.md",
            "discussion.md",
            "conclusion.md"
        ],
        "figures": [
            "Figure_1_Methodology.png",
            "Figure_2_Study_Area.png",
            "Figure_3_Results.png"
        ],
        "tables": [
            "Table_1_Data_Sources.xlsx",
            "Table_2_Results_Summary.xlsx"
        ],
        "bibliography": [
            "references.bib",
            "doi_validation_report.txt"
        ],
        "supplementary": [
            "Supplementary_Materials_README.md"
        ]
    }
    
    # Create README file
    readme_content = """# MDPI Language Editing Service - Submission Template
## Rocket Drop Zone Analysis - OTU Pipeline

### INSTRUCTIONS FOR USE:

1. **Replace Placeholder Files**
   - Replace `main_manuscript.docx` with your actual manuscript
   - Update figure files in `figures/` directory
   - Add your tables to `tables/` directory
   - Include formatted references in `bibliography/`

2. **File Requirements**
   - Manuscript: .docx or .tex format
   - Figures: PNG or JPG, 300 DPI minimum
   - Tables: Excel (.xlsx) or CSV format
   - References: BibTeX format, MDPI style

3. **Metadata**
   - Update `metadata.json` with your manuscript details
   - Ensure all author information is correct
   - Specify target journal (Aerospace)

4. **Submission**
   - Zip this entire directory
   - Submit via MDPI language service portal
   - Keep submission ID for tracking

### DIRECTORY STRUCTURE:
- `manuscript/` - Main manuscript files
- `figures/` - All figures (300 DPI)
- `tables/` - Supplementary tables
- `bibliography/` - Reference files
- `supplementary/` - Additional materials

### CONTACT INFORMATION:
- Corresponding Author: [Your Name]
- Email: [your.email@institution.edu]
- Institution: [Your Institution]
- Manuscript ID: [To be assigned by MDPI]

### SPECIAL NOTES FOR EDITOR:
- This is a technical manuscript about rocket drop zone analysis
- Please preserve technical terms: OTU, NDVI, SRTM, DEM
- Maintain consistency with previous language edits
- References follow MDPI Aerospace style

---
**Package Created:** {date}
**Template Version:** 1.0
**Task Reference:** 4.5 Professional Editing Service
""".format(date=datetime.now().strftime("%Y-%m-%d"))
    
    readme_path = template_dir / "README_Submission.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # Create metadata file
    metadata = {
        "package_type": "MDPI Language Editing Submission",
        "created_date": datetime.now().isoformat(),
        "template_version": "1.0",
        "manuscript_details": {
            "title": "Rocket Drop Zone Analysis Using Operational Terrain Units (OTUs)",
            "authors": [
                {
                    "first_name": "[Author1_First]",
                    "last_name": "[Author1_Last]",
                    "email": "[author1@email.com]",
                    "affiliation": "[Affiliation 1]",
                    "orcid": "[0000-0000-0000-0000]"
                },
                {
                    "first_name": "[Author2_First]",
                    "last_name": "[Author2_Last]",
                    "email": "[author2@email.com]",
                    "affiliation": "[Affiliation 2]",
                    "orcid": "[0000-0000-0000-0001]"
                }
            ],
            "corresponding_author": "[author1@email.com]",
            "target_journal": "Aerospace",
            "word_count": 0,
            "abstract_word_count": 0,
            "figure_count": 0,
            "table_count": 0,
            "reference_count": 0
        },
        "editing_instructions": {
            "focus_areas": [
                "Academic English clarity",
                "Sentence structure improvement",
                "Technical terminology consistency",
                "MDPI style compliance"
            ],
            "preserve": [
                "Technical terms (OTU, NDVI, SRTM)",
                "Mathematical equations",
                "Methodology descriptions",
                "Data references"
            ],
            "special_requests": [
                "Check article usage (a/an/the)",
                "Reduce passive voice where possible",
                "Ensure acronyms are defined at first use",
                "Verify reference formatting"
            ]
        },
        "integration_with_tasks": {
            "task_4_1": "Language check completed",
            "task_4_2_4_3": "Manual language editing applied",
            "task_4_4": "Bibliography formatted to MDPI style",
            "task_4_5": "Professional editing service preparation"
        }
    }
    
    metadata_path = template_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Create directory structure and placeholder files
    for directory, files in package_structure.items():
        dir_path = template_dir / directory
        dir_path.mkdir(exist_ok=True)
        
        for file in files:
            file_path = dir_path / file
            
            # Create placeholder content based on file type
            if file.endswith('.md'):
                content = f"# Placeholder: {file}\n\nThis is a placeholder file for the submission package.\nReplace with actual content before submission.\n\nCreated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            elif file.endswith('.txt'):
                content = f"Placeholder file: {file}\n\nThis file should contain:\n- Relevant data or information\n- Properly formatted content\n- Actual manuscript text\n\nTemplate version: 1.0"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            else:
                # Create empty file for other types
                file_path.touch()
    
    # Create a sample manuscript file
    sample_manuscript = template_dir / "manuscript" / "sample_manuscript_section.md"
    with open(sample_manuscript, 'w', encoding='utf-8') as f:
        f.write("""# Sample Manuscript Section

## 1. Introduction

The recovery of rocket stages after launch represents a critical component of space mission planning and cost management. Traditional approaches to drop zone selection often rely on qualitative assessments and historical precedent, which may not adequately account for contemporary environmental factors or economic considerations.

Recent advances in remote sensing technology and geospatial analysis provide opportunities for more systematic, data-driven methodologies. The Operational Terrain Unit (OTU) concept, originally developed for military terrain analysis, offers a quantitative framework that can be adapted for rocket drop zone assessment.

## 2. Methodology

### 2.1 Data Sources

Our analysis integrates multiple data sources:

1. **Sentinel-2 Imagery**: Used for vegetation assessment via the Normalized Difference Vegetation Index (NDVI)
2. **SRTM DEM**: Digital Elevation Model for topographic analysis
3. **SoilGrids Data**: Global soil information for quality assessment
4. **Economic Data**: Cost parameters for damage assessment

### 2.2 OTU Calculation

The OTU value is calculated using the following formula:

```
OTU = w₁ × Q_NDVI + w₂ × Q_Soil + w₃ × Q_Topography + w₄ × Q_Accessibility
```

Where:
- Q_NDVI: Vegetation quality index (0-1)
- Q_Soil: Soil quality index (0-1)  
- Q_Topography: Terrain suitability index (0-1)
- Q_Accessibility: Access and infrastructure index (0-1)
- w₁-w₄: Weighting coefficients summing to 1.0

## 3. Results

Preliminary results indicate that approximately 15% of the study area qualifies as highly suitable (OTU > 0.7), while 40% is moderately suitable (OTU 0.4-0.7). The remaining 45% is classified as unsuitable or requiring significant mitigation measures.

## 4. Discussion

The OTU-based approach offers several advantages over traditional methods:

1. **Quantitative Assessment**: Provides numerical suitability scores
2. **Multi-criteria Integration**: Combines environmental, topographic, and economic factors
3. **Scalability**: Can be applied to different regions and scales
4. **Reproducibility**: Based on standardized data sources and algorithms

## 5. Conclusion

The Operational Terrain Unit methodology provides a systematic, data-driven approach for rocket drop zone analysis. By integrating remote sensing data, terrain analysis, and economic considerations, it offers improved decision support for space mission planning.

### Future Work

1. Extension to other geographic regions
2. Incorporation of real-time weather data
3. Development of automated decision support tools
4. Integration with rocket trajectory simulation

---
*This is a sample manuscript section for demonstration purposes.*
*Replace with actual manuscript content before submission.*
""")
    
    # Create ZIP package
    output_dir = Path("outputs/professional_editing")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = output_dir / "Submission_Package_Template.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from template directory
        for file_path in template_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(template_dir)
                zipf.write(file_path, arcname)
    
    print(f"\nTemplate created successfully!")
    print(f"Template directory: {template_dir}")
    print(f"ZIP package: {zip_path}")
    
    # Create usage instructions
    print("\n" + "="*60)
    print("USAGE INSTRUCTIONS")
    print("="*60)
    print("\n1. Extract the template:")
    print("   unzip outputs/professional_editing/Submission_Package_Template.zip")
    
    print("\n2. Replace placeholder files with your actual content:")
    print("   - Replace files in manuscript/ directory")
    print("   - Add your figures to figures/ directory")
    print("   - Add your tables to tables/ directory")
    print("   - Update bibliography/ files")
    
    print("\n3. Update metadata.json with your manuscript details")
    
    print("\n4. Create your submission package:")
    print("   python scripts/professional_editing_service.py --create-package")
    
    print("\n5. Submit to MDPI language service")
    
    print("\n" + "="*60)
    print("TEMPLATE CONTENTS")
    print("="*60)
    
    # List template contents
    for directory, files in package_structure.items():
        print(f"\n{directory}/")
        for file in files:
            print(f"  - {file}")
    
    print(f"\nAdditional files:")
    print(f"  - README_Submission.txt")
    print(f"  - metadata.json")
    print(f"  - manuscript/sample_manuscript_section.md")
    
    return zip_path

def create_minimal_submission_package():
    """Create a minimal submission package for quick testing."""
    
    print("\nCreating minimal submission package for testing...")
    
    output_dir = Path("outputs/professional_editing")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = output_dir / "Submission_Package_Minimal.zip"
    
    # Create minimal files
    minimal_files = {
        "manuscript/main_manuscript.docx": "Placeholder for main manuscript",
        "README.txt": "Minimal submission package for testing\nCreated: " + datetime.now().strftime("%Y-%m-%d"),
        "metadata.json": json.dumps({
            "test_package": True,
            "created": datetime.now().isoformat(),
            "purpose": "Testing professional editing service"
        }, indent=2)
    }
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for filename, content in minimal_files.items():
            zipf.writestr(filename, content)
    
    print(f"Minimal package created: {zip_path}")
    print("Use for testing the professional editing service workflow.")
    
    return zip_path

if __name__ == '__main__':
    # Create full template
    template_zip = create_submission_package_template()
    
    # Create minimal package for testing
    minimal_zip = create_minimal_submission_package()
    
    print("\n" + "="*60)
    print("CREATION COMPLETE")
    print("="*60)
    print(f"\nFiles created:")
    print(f"1. Full template: {template_zip}")
    print(f"2. Minimal package: {minimal_zip}")
    print(f"3. Template directory: templates/submission_package/")
    
    print("\nNext steps:")
    print("1. Use the template to prepare your submission")
    print("2. Or use the minimal package for testing")
    print("3. Run: python scripts/professional_editing_service.py --create-package")
    print("4. Submit to MDPI language service")