# 📘 Scripts README
## Revision Scripts for MDPI Aerospace Manuscript

This directory contains scripts for generating supplementary materials and tables for the manuscript revision.

---

## 🚀 Quick Start

### Prerequisites

1. **Install Python dependencies:**
```bash
pip install pandas numpy openpyxl earthengine-api
```

2. **Authenticate with Google Earth Engine** (for Task 1.1 only):
```bash
earthengine authenticate
```

3. **Verify project structure:**
```bash
# Ensure you're in the project root
cd rocket-drop-zone-analysis-otu

# Verify outputs directory exists
ls outputs/supplementary_tables/
```

---

## 📜 Available Scripts

### 1. [`create_sentinel_table.py`](create_sentinel_table.py)
**Task 1.1: Sentinel-2 Scene Metadata Table**

**Purpose:** Extract metadata from all Sentinel-2 scenes used in the analysis.

**Requirements:**
- Google Earth Engine authentication
- Internet connection

**Usage:**
```bash
python scripts/create_sentinel_table.py
```

**Outputs:**
- `outputs/supplementary_tables/Table_S1_Sentinel2_Scenes.xlsx`
- `outputs/supplementary_tables/Table_S1_Sentinel2_Scenes.csv`
- `outputs/supplementary_tables/Table_S1_Sentinel2_Scenes.tex`
- `outputs/supplementary_tables/Table_S1_Manuscript_Text.txt`

**Customization:**
Edit the `create_study_area_roi()` function to adjust study area coordinates.

---

### 2. [`create_soil_tables.py`](create_soil_tables.py)
**Task 1.2: Soil Coefficients Tables (QBi, QSi)**

**Purpose:** Generate bonitet and Protodyakonov strength coefficient tables.

**Requirements:**
- pandas, openpyxl (no GEE needed)

**Usage:**
```bash
python scripts/create_soil_tables.py
```

**Outputs:**
- `outputs/supplementary_tables/Table_S2_Soil_Quality_Coefficients.xlsx/csv/tex`
- `outputs/supplementary_tables/Table_S3_Protodyakonov_Strength.xlsx/csv/tex`
- `outputs/supplementary_tables/Soil_Calculation_Worked_Example.txt`

**Features:**
- 8 soil types with slope corrections
- 8 material types on Protodyakonov scale
- Worked example included

---

### 3. [`create_fire_hazard_classification.py`](create_fire_hazard_classification.py)
**Task 1.3: Fire Hazard Classification**

**Purpose:** Create vegetation classification and fire hazard assessment tables.

**Requirements:**
- pandas, numpy, openpyxl (no GEE needed)

**Usage:**
```bash
python scripts/create_fire_hazard_classification.py
```

**Outputs:**
- `outputs/supplementary_tables/Fire_Hazard_Classification.xlsx/csv/tex`
- `outputs/supplementary_tables/Fire_Hazard_Seasonal_Comparison.csv`
- `outputs/supplementary_tables/Fire_Hazard_Methodology_Text.txt`
- `outputs/supplementary_tables/Fire_Hazard_Worked_Example.txt`

**Features:**
- 8 vegetation classes with NDVI ranges
- Seasonal correction factors
- Fire risk levels and flammability weights

---

## 🔄 Execution Order

**Recommended order:**

1. **First:** Run Tasks 1.2 and 1.3 (no GEE required)
   ```bash
   python scripts/create_soil_tables.py
   python scripts/create_fire_hazard_classification.py
   ```

2. **Second:** Authenticate with GEE and run Task 1.1
   ```bash
   earthengine authenticate
   python scripts/create_sentinel_table.py
   ```

3. **Third:** Review Task 1.4 documentation
   ```bash
   cat outputs/supplementary_tables/Task_1.4_Atmospheric_Correction_Details.md
   ```

---

## 📊 Output Verification

After running scripts, verify outputs:

```bash
# Check Excel files
ls -lh outputs/supplementary_tables/*.xlsx

# Check CSV files
ls -lh outputs/supplementary_tables/*.csv

# Check LaTeX files
ls -lh outputs/supplementary_tables/*.tex

# Check text files
ls -lh outputs/supplementary_tables/*.txt
```

**Expected files:**
- 3 Excel files (Tables S1, S2, S3)
- 3+ CSV files
- 3+ LaTeX files
- 4+ text files (manuscript text, worked examples)

---

## 🐛 Troubleshooting

### Issue: "earthengine-api not found"
**Solution:**
```bash
pip install earthengine-api
```

### Issue: "Authentication required"
**Solution:**
```bash
earthengine authenticate
# Follow the browser authentication flow
```

### Issue: "Permission denied" on outputs directory
**Solution:**
```bash
mkdir -p outputs/supplementary_tables
chmod 755 outputs/supplementary_tables
```

### Issue: "ModuleNotFoundError: No module named 'openpyxl'"
**Solution:**
```bash
pip install openpyxl
```

### Issue: Script runs but no output files
**Solution:**
Check that you're running from project root:
```bash
pwd  # Should show: .../rocket-drop-zone-analysis-otu
python scripts/create_soil_tables.py
```

---

## 🔧 Customization

### Modify Study Area (Task 1.1)
Edit `create_sentinel_table.py`:
```python
def create_study_area_roi() -> ee.Geometry:
    coords = [
        [your_lon_min, your_lat_min],
        [your_lon_max, your_lat_min],
        [your_lon_max, your_lat_max],
        [your_lon_min, your_lat_max],
        [your_lon_min, your_lat_min],
    ]
    return ee.Geometry.Polygon(coords)
```

### Modify Date Range (Task 1.1)
Edit `main()` function:
```python
df = extract_sentinel2_metadata(
    roi=roi,
    start_date="2017-01-01",  # Change this
    end_date="2023-12-31",    # Change this
    cloud_threshold=30
)
```

### Add New Soil Types (Task 1.2)
Edit `SoilQualityCalculator.BONITET_COEFFICIENTS` dictionary.

### Add New Vegetation Classes (Task 1.3)
Edit `FireHazardClassifier.VEGETATION_CLASSES` dictionary.

---

## 📝 Integration with Manuscript

### For Materials & Methods Section
Use generated text files:
- `Table_S1_Manuscript_Text.txt` → Section 3.1 (Data Acquisition)
- `Fire_Hazard_Methodology_Text.txt` → Section 3.2 (Fire Hazard)
- `Task_1.4_Atmospheric_Correction_Details.md` → Section 3.1 (Processing)

### For Supplementary Materials
Include all generated Excel/CSV files:
- Table S1: Sentinel-2 Scenes
- Table S2: Bonitet Coefficients
- Table S3: Protodyakonov Strength
- Fire Hazard Classification

### For Worked Examples
Use generated example files in manuscript text or supplementary methods.

---

## 🧪 Testing

### Quick Test (without GEE)
```bash
# Test soil tables
python scripts/create_soil_tables.py
# Should complete in < 5 seconds

# Test fire classification
python scripts/create_fire_hazard_classification.py
# Should complete in < 5 seconds
```

### Full Test (with GEE)
```bash
# Authenticate first
earthengine authenticate

# Test Sentinel-2 extraction
python scripts/create_sentinel_table.py
# May take 1-5 minutes depending on scene count
```

---

## 📚 References

**Scripts implement methodologies from:**
- Task 1.1: ESA Sentinel-2 User Guide
- Task 1.2: National soil classification standards (bonitet methodology)
- Task 1.3: Fire hazard assessment literature
- Task 1.4: Sen2Cor documentation (Louis et al., 2016)

---

## 🆘 Support

**For issues:**
1. Check this README
2. Review script docstrings
3. Check [`outputs/Day_1_Implementation_Report.md`](../outputs/Day_1_Implementation_Report.md)
4. Review main plan: [`Documents/00_MAIN_PLAN.md`](../Documents/00_MAIN_PLAN.md)

**For questions about methodology:**
- See worked examples in output text files
- Review class docstrings in scripts
- Check IMPLEMENTATION_CHECKLIST.md for task details

---

**Last Updated:** 2026-01-27  
**Version:** 1.0  
**Status:** Ready for execution
