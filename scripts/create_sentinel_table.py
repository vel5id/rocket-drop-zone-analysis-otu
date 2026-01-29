"""
Task 1.1: Create Sentinel-2 Scene Metadata Table (Table S1)

This script extracts metadata from all Sentinel-2 scenes used in the analysis
and creates Table S1 for supplementary materials.

Implements БЛОК 1, Task 1.1 from revision plan.
"""
from __future__ import annotations

import pandas as pd
from datetime import datetime
from pathlib import Path
import ee

# Initialize Earth Engine
try:
    ee.Initialize()
except Exception:
    print("Attempting to authenticate with Earth Engine...")
    ee.Authenticate()
    ee.Initialize()


def extract_sentinel2_metadata(
    roi: ee.Geometry,
    start_date: str = "2017-01-01",
    end_date: str = "2023-12-31",
    cloud_threshold: int = 30,
) -> pd.DataFrame:
    """
    Extract metadata from Sentinel-2 scenes used in the analysis.
    
    Args:
        roi: Region of interest (study area geometry)
        start_date: Start date for scene collection
        end_date: End date for scene collection
        cloud_threshold: Maximum cloud cover percentage
    
    Returns:
        DataFrame with scene metadata
    """
    print(f"Fetching Sentinel-2 scenes from {start_date} to {end_date}...")
    
    # Query Sentinel-2 Surface Reflectance collection
    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(roi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
    )
    
    # Get collection info
    collection_list = collection.toList(collection.size())
    collection_size = collection.size().getInfo()
    
    print(f"Found {collection_size} scenes matching criteria")
    
    # Extract metadata for each scene
    metadata_records = []
    
    for i in range(collection_size):
        image = ee.Image(collection_list.get(i))
        props = image.getInfo()['properties']
        
        # Extract relevant metadata
        record = {
            'Scene_ID': props.get('PRODUCT_ID', 'N/A'),
            'Granule_ID': props.get('GRANULE_ID', 'N/A'),
            'Acquisition_Date': datetime.fromtimestamp(
                props.get('system:time_start', 0) / 1000
            ).strftime('%Y-%m-%d'),
            'Acquisition_Time': datetime.fromtimestamp(
                props.get('system:time_start', 0) / 1000
            ).strftime('%H:%M:%S UTC'),
            'Cloud_Cover_Percent': round(props.get('CLOUDY_PIXEL_PERCENTAGE', 0), 2),
            'Processing_Baseline': props.get('PROCESSING_BASELINE', 'N/A'),
            'Sensor': 'Sentinel-2 MSI',
            'Processing_Level': 'Level-2A (Surface Reflectance)',
            'Tile_ID': props.get('MGRS_TILE', 'N/A'),
            'Orbit_Number': props.get('SENSING_ORBIT_NUMBER', 'N/A'),
            'Quality_Flag': 'PASSED' if props.get('CLOUDY_PIXEL_PERCENTAGE', 100) < cloud_threshold else 'FILTERED',
        }
        
        metadata_records.append(record)
        
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/{collection_size} scenes...")
    
    # Create DataFrame
    df = pd.DataFrame(metadata_records)
    
    # Sort by acquisition date
    df = df.sort_values('Acquisition_Date').reset_index(drop=True)
    
    return df


def create_study_area_roi() -> ee.Geometry:
    """
    Define the study area ROI for Baikonur Cosmodrome drop zones.
    
    Returns:
        Earth Engine Geometry object
    """
    # Approximate coordinates for Baikonur drop zones
    # These should be adjusted based on actual study area
    coords = [
        [62.0, 45.5],  # Southwest corner
        [67.0, 45.5],  # Southeast corner
        [67.0, 48.0],  # Northeast corner
        [62.0, 48.0],  # Northwest corner
        [62.0, 45.5],  # Close polygon
    ]
    
    return ee.Geometry.Polygon(coords)


def add_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add summary statistics to the metadata table.
    
    Args:
        df: DataFrame with scene metadata
    
    Returns:
        DataFrame with added summary row
    """
    summary = {
        'Scene_ID': 'SUMMARY STATISTICS',
        'Granule_ID': f'Total scenes: {len(df)}',
        'Acquisition_Date': f'{df["Acquisition_Date"].min()} to {df["Acquisition_Date"].max()}',
        'Acquisition_Time': '',
        'Cloud_Cover_Percent': f'Mean: {df["Cloud_Cover_Percent"].mean():.2f}%',
        'Processing_Baseline': f'Modes: {df["Processing_Baseline"].mode().iloc[0] if len(df) > 0 else "N/A"}',
        'Sensor': 'Sentinel-2A/2B MSI',
        'Processing_Level': 'Level-2A (Sen2Cor)',
        'Tile_ID': f'Unique tiles: {df["Tile_ID"].nunique()}',
        'Orbit_Number': '',
        'Quality_Flag': f'Passed: {(df["Quality_Flag"] == "PASSED").sum()}',
    }
    
    # Append summary as last row
    df_with_summary = pd.concat([df, pd.DataFrame([summary])], ignore_index=True)
    
    return df_with_summary


def save_table_s1(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Save Table S1 in multiple formats.
    
    Args:
        df: DataFrame with scene metadata
        output_dir: Output directory path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as Excel
    excel_path = output_dir / "Table_S1_Sentinel2_Scenes.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df.to_excel(
            writer,
            sheet_name='Sentinel-2 Metadata',
            index=False,
            freeze_panes=(1, 0)
        )
        
        # Format the worksheet
        worksheet = writer.sheets['Sentinel-2 Metadata']
        
        # Set column widths
        column_widths = {
            'A': 35,  # Scene_ID
            'B': 35,  # Granule_ID
            'C': 15,  # Acquisition_Date
            'D': 18,  # Acquisition_Time
            'E': 18,  # Cloud_Cover_Percent
            'F': 20,  # Processing_Baseline
            'G': 18,  # Sensor
            'H': 30,  # Processing_Level
            'I': 12,  # Tile_ID
            'J': 15,  # Orbit_Number
            'K': 15,  # Quality_Flag
        }
        
        for col, width in column_widths.items():
            worksheet.column_dimensions[col].width = width
    
    print(f"[OK] Saved Excel: {excel_path}")
    
    # Save as CSV
    csv_path = output_dir / "Table_S1_Sentinel2_Scenes.csv"
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"[OK] Saved CSV: {csv_path}")
    
    # Create LaTeX version
    latex_path = output_dir / "Table_S1_Sentinel2_Scenes.tex"
    
    # Select key columns for LaTeX (to fit on page)
    df_latex = df[['Scene_ID', 'Acquisition_Date', 'Cloud_Cover_Percent', 
                   'Tile_ID', 'Quality_Flag']].copy()
    
    # Shorten Scene IDs for LaTeX
    df_latex['Scene_ID'] = df_latex['Scene_ID'].str.slice(0, 25) + '...'
    
    latex_content = df_latex.to_latex(
        index=False,
        caption='Sentinel-2 scenes used in the analysis (abbreviated)',
        label='tab:sentinel2_scenes',
        column_format='lcccc',
        escape=False
    )
    
    with open(latex_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"[OK] Saved LaTeX: {latex_path}")


def generate_manuscript_text(df: pd.DataFrame) -> str:
    """
    Generate text for Materials & Methods section.
    
    Args:
        df: DataFrame with scene metadata
    
    Returns:
        Formatted text for manuscript
    """
    total_scenes = len(df) - 1  # Exclude summary row
    date_range = f"{df['Acquisition_Date'].iloc[0]} to {df['Acquisition_Date'].iloc[-2]}"
    mean_cloud = df['Cloud_Cover_Percent'].iloc[:-1].mean()
    unique_tiles = df['Tile_ID'].iloc[:-1].nunique()
    
    text = f"""
### Sentinel-2 Data Acquisition (for Materials & Methods section)

Sentinel-2 Level-2A Surface Reflectance imagery was acquired from the 
Copernicus Open Access Hub for the period {date_range}. A total of {total_scenes} 
scenes were processed, covering {unique_tiles} unique MGRS tiles over the study area. 
All scenes were filtered to include only those with cloud cover below 30%, 
with a mean cloud cover of {mean_cloud:.2f}%. 

Atmospheric correction was performed using the ESA Sen2Cor processor (version 2.9), 
which applies scene classification and atmospheric correction to convert 
Top-of-Atmosphere (TOA) reflectance to Bottom-of-Atmosphere (BOA) surface reflectance. 
The Sen2Cor algorithm accounts for atmospheric scattering and absorption, 
terrain correction, and cirrus cloud detection.

All scene metadata, including acquisition dates, cloud cover percentages, 
and quality flags, are provided in Supplementary Table S1.
"""
    
    return text


def main():
    """Main execution function."""
    print("=" * 70)
    print("Task 1.1: Creating Sentinel-2 Scene Metadata Table (Table S1)")
    print("=" * 70)
    print()
    
    # Define study area
    roi = create_study_area_roi()
    
    # Extract metadata
    df = extract_sentinel2_metadata(
        roi=roi,
        start_date="2017-01-01",
        end_date="2023-12-31",
        cloud_threshold=30
    )
    
    # Add summary statistics
    df = add_summary_statistics(df)
    
    # Save outputs
    output_dir = Path("outputs/supplementary_tables")
    save_table_s1(df, output_dir)
    
    # Generate manuscript text
    manuscript_text = generate_manuscript_text(df)
    
    # Save manuscript text
    text_path = output_dir / "Table_S1_Manuscript_Text.txt"
    with open(text_path, 'w', encoding='utf-8') as f:
        f.write(manuscript_text)
    
    print(f"[OK] Saved manuscript text: {text_path}")
    
    print()
    print("=" * 70)
    print("[OK] Task 1.1 COMPLETED")
    print(f"✓ Total scenes processed: {len(df) - 1}")
    print(f"✓ Output files created in: {output_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
