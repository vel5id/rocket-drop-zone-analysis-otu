"""
Task 1.1: Create Sentinel-2 Scene Metadata Table (Table S1) - Enhanced Version

This script extracts metadata from all Sentinel-2 scenes used in the analysis
and creates Table S1 for supplementary materials. Includes comprehensive logging
and progress tracking.

Implements БЛОК 1, Task 1.1 from revision plan.
"""
from __future__ import annotations

import pandas as pd
from datetime import datetime
from pathlib import Path
import ee
import time
import logging
import sys
from typing import Optional
import traceback

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'sentinel_table_enhanced.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def setup_earth_engine() -> bool:
    """
    Initialize Earth Engine with fallback to mock data.
    
    Returns:
        bool: True if GEE initialized successfully, False otherwise
    """
    try:
        ee.Initialize()
        logger.info("Earth Engine initialized successfully")
        return True
    except Exception as e:
        logger.warning(f"Earth Engine initialization failed: {e}")
        print("\n" + "="*70)
        print("EARTH ENGINE AUTHENTICATION REQUIRED")
        print("="*70)
        print("To use real Sentinel-2 data, you need to authenticate with Google Earth Engine.")
        print("Run the following command in your terminal:")
        print("\n    earthengine authenticate\n")
        print("Then run this script again.")
        print("\nFor now, the script will use mock data for demonstration.")
        print("="*70 + "\n")
        return False

def create_mock_metadata(num_scenes: int = 50) -> pd.DataFrame:
    """
    Create mock metadata for demonstration when GEE is not available.
    
    Args:
        num_scenes: Number of mock scenes to generate
    
    Returns:
        DataFrame with mock scene metadata
    """
    logger.info(f"Creating mock metadata with {num_scenes} scenes")
    
    # Generate sample dates
    dates = pd.date_range(start='2017-01-01', end='2023-12-31', freq='30D')
    
    records = []
    for i, date in enumerate(dates[:num_scenes]):
        record = {
            'Scene_ID': f'S2A_MSIL2A_{date.strftime("%Y%m%dT%H%M%S")}_N9999_R999_T43UDP_{i:04d}',
            'Granule_ID': f'L2A_T43UDP_A{date.strftime("%Y%m%d")}_{i:04d}',
            'Acquisition_Date': date.strftime('%Y-%m-%d'),
            'Acquisition_Time': '10:30:00 UTC',
            'Cloud_Cover_Percent': round(10 + i % 20, 2),
            'Processing_Baseline': '04.00',
            'Sensor': 'Sentinel-2A MSI' if i % 2 == 0 else 'Sentinel-2B MSI',
            'Processing_Level': 'Level-2A (Surface Reflectance)',
            'Tile_ID': f'43U{"DP"[i%2]}',
            'Orbit_Number': 12345 + i,
            'Quality_Flag': 'PASSED' if (10 + i % 20) < 30 else 'FILTERED',
            'Data_Source': 'MOCK (GEE not available)',
        }
        records.append(record)
    
    df = pd.DataFrame(records)
    logger.info(f"Created mock metadata with {len(df)} scenes")
    return df

def extract_sentinel2_metadata(
    roi: ee.Geometry,
    start_date: str = "2017-01-01",
    end_date: str = "2023-12-31",
    cloud_threshold: int = 30,
    max_scenes: Optional[int] = 50,
    use_mock: bool = False,
) -> pd.DataFrame:
    """
    Extract metadata from Sentinel-2 scenes used in the analysis.
    
    Args:
        roi: Region of interest (study area geometry)
        start_date: Start date for scene collection
        end_date: End date for scene collection
        cloud_threshold: Maximum cloud cover percentage
        max_scenes: Maximum number of scenes to process (None for all)
        use_mock: Use mock data instead of real GEE data
    
    Returns:
        DataFrame with scene metadata
    """
    if use_mock:
        logger.info("Using mock data as requested")
        return create_mock_metadata(max_scenes or 50)
    
    logger.info(f"Fetching Sentinel-2 scenes from {start_date} to {end_date}...")
    logger.info(f"Cloud threshold: {cloud_threshold}%, Max scenes: {max_scenes}")
    
    try:
        # Query Sentinel-2 Surface Reflectance collection
        logger.info("Querying COPERNICUS/S2_SR_HARMONIZED collection...")
        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(roi)
            .filterDate(start_date, end_date)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", cloud_threshold))
        )
        
        # Get collection info
        logger.info("Getting collection size...")
        collection_size = collection.size().getInfo()
        logger.info(f"Found {collection_size} scenes matching criteria")
        
        # Limit number of scenes if specified
        if max_scenes and collection_size > max_scenes:
            logger.info(f"Limiting to {max_scenes} scenes (first {max_scenes} of {collection_size})")
            collection = collection.limit(max_scenes)
            collection_size = max_scenes
        
        # Get collection as list
        logger.info("Converting collection to list...")
        collection_list = collection.toList(collection_size)
        
        # Extract metadata for each scene
        metadata_records = []
        start_time = time.time()
        success_count = 0
        error_count = 0
        
        logger.info(f"Starting metadata extraction for {collection_size} scenes...")
        
        for i in range(collection_size):
            try:
                # Progress indicator
                if i % 10 == 0 or i == collection_size - 1:
                    elapsed = time.time() - start_time
                    scenes_per_second = (i + 1) / elapsed if elapsed > 0 else 0
                    progress_pct = (i + 1) / collection_size * 100
                    logger.info(f"Progress: {i + 1}/{collection_size} ({progress_pct:.1f}%) - "
                               f"{scenes_per_second:.2f} scenes/sec - "
                               f"{success_count} successful, {error_count} errors")
                
                # Get image and properties
                image = ee.Image(collection_list.get(i))
                props = image.getInfo()['properties']
                
                # Extract relevant metadata
                system_time = props.get('system:time_start', 0)
                acquisition_date = datetime.fromtimestamp(system_time / 1000).strftime('%Y-%m-%d')
                acquisition_time = datetime.fromtimestamp(system_time / 1000).strftime('%H:%M:%S UTC')
                cloud_cover = round(props.get('CLOUDY_PIXEL_PERCENTAGE', 0), 2)
                
                record = {
                    'Scene_ID': props.get('PRODUCT_ID', 'N/A'),
                    'Granule_ID': props.get('GRANULE_ID', 'N/A'),
                    'Acquisition_Date': acquisition_date,
                    'Acquisition_Time': acquisition_time,
                    'Cloud_Cover_Percent': cloud_cover,
                    'Processing_Baseline': props.get('PROCESSING_BASELINE', 'N/A'),
                    'Sensor': 'Sentinel-2 MSI',
                    'Processing_Level': 'Level-2A (Surface Reflectance)',
                    'Tile_ID': props.get('MGRS_TILE', 'N/A'),
                    'Orbit_Number': props.get('SENSING_ORBIT_NUMBER', 'N/A'),
                    'Quality_Flag': 'PASSED' if cloud_cover < cloud_threshold else 'FILTERED',
                    'Data_Source': 'Google Earth Engine',
                }
                
                metadata_records.append(record)
                success_count += 1
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing scene {i}: {str(e)[:100]}...")
                if error_count <= 3:  # Log full trace for first few errors
                    logger.debug(f"Full error trace for scene {i}: {traceback.format_exc()}")
                continue
        
        # Create DataFrame
        df = pd.DataFrame(metadata_records)
        
        if len(df) == 0:
            logger.warning("No scenes processed successfully. Creating mock data.")
            return create_mock_metadata(max_scenes or 50)
        
        # Sort by acquisition date
        df = df.sort_values('Acquisition_Date').reset_index(drop=True)
        
        total_time = time.time() - start_time
        logger.info(f"Metadata extraction completed: {len(df)} scenes in {total_time:.2f} seconds")
        logger.info(f"Success rate: {success_count}/{collection_size} ({success_count/collection_size*100:.1f}%)")
        if error_count > 0:
            logger.warning(f"Errors encountered: {error_count} scenes failed")
        
        return df
        
    except Exception as e:
        logger.error(f"Error in metadata extraction: {e}")
        logger.error(f"Full trace: {traceback.format_exc()}")
        logger.info("Falling back to mock data")
        return create_mock_metadata(max_scenes or 50)

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
    
    logger.info(f"Created study area ROI with coordinates: {coords[:2]}...")
    return ee.Geometry.Polygon(coords)

def add_summary_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add summary statistics to the metadata table.
    
    Args:
        df: DataFrame with scene metadata
    
    Returns:
        DataFrame with added summary row
    """
    if len(df) == 0:
        logger.warning("Empty DataFrame, cannot add summary statistics")
        return df
    
    try:
        # Filter out summary row if it already exists
        df_data = df[~df['Scene_ID'].str.contains('SUMMARY', na=False)].copy()
        
        if len(df_data) == 0:
            logger.warning("No data rows found for summary statistics")
            return df
        
        # Calculate statistics
        total_scenes = len(df_data)
        date_range = f'{df_data["Acquisition_Date"].min()} to {df_data["Acquisition_Date"].max()}'
        mean_cloud = df_data["Cloud_Cover_Percent"].mean()
        unique_tiles = df_data["Tile_ID"].nunique()
        passed_scenes = (df_data["Quality_Flag"] == "PASSED").sum()
        data_source = df_data["Data_Source"].iloc[0] if "Data_Source" in df_data.columns else "Unknown"
        
        summary = {
            'Scene_ID': 'SUMMARY STATISTICS',
            'Granule_ID': f'Total scenes: {total_scenes}',
            'Acquisition_Date': date_range,
            'Acquisition_Time': '',
            'Cloud_Cover_Percent': f'Mean: {mean_cloud:.2f}%',
            'Processing_Baseline': f'Mode: {df_data["Processing_Baseline"].mode().iloc[0] if len(df_data) > 0 else "N/A"}',
            'Sensor': 'Sentinel-2A/2B MSI',
            'Processing_Level': 'Level-2A (Sen2Cor)',
            'Tile_ID': f'Unique tiles: {unique_tiles}',
            'Orbit_Number': '',
            'Quality_Flag': f'Passed: {passed_scenes}',
            'Data_Source': data_source,
        }
        
        # Append summary as last row
        df_with_summary = pd.concat([df_data, pd.DataFrame([summary])], ignore_index=True)
        
        logger.info(f"Added summary statistics: {total_scenes} scenes, "
                   f"{unique_tiles} unique tiles, mean cloud {mean_cloud:.2f}%, "
                   f"data source: {data_source}")
        
        return df_with_summary
        
    except Exception as e:
        logger.error(f"Error adding summary statistics: {e}")
        logger.error(f"Full trace: {traceback.format_exc()}")
        return df

def save_table_s1(df: pd.DataFrame, output_dir: Path) -> None:
    """
    Save Table S1 in multiple formats.
    
    Args:
        df: DataFrame with scene metadata
        output_dir: Output directory path
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Saving Table S1 to {output_dir}")
    
    # Save as Excel
    excel_path = output_dir / "Table_S1_Sentinel2_Scenes.xlsx"
    try:
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
                'L': 20,  # Data_Source
            }
            
            for col, width in column_widths.items():
                worksheet.column_dimensions[col].width = width
        
        logger.info(f"[OK] Saved Excel: {excel_path}")
        print(f"[OK] Saved Excel: {excel_path}")
        
    except Exception as e:
        logger.error(f"Error saving Excel file: {e}")
        print(f"[ERROR] Failed to save Excel: {e}")
    
    # Save as CSV
    csv_path = output_dir / "Table_S1_Sentinel2_Scenes.csv"
    try:
        df.to_csv(csv_path, index=False, encoding='utf-8')
        logger.info(f"[OK] Saved CSV: {csv_path}")
        print(f"[OK] Saved CSV: {csv_path}")
    except Exception as e:
        logger.error(f"Error saving CSV file: {e}")
        print(f"[ERROR] Failed to save CSV: {e}")
    
    # Create LaTeX version
    latex_path = output_dir / "Table_S1_Sentinel2_Scenes.tex"
    try:
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
        
        logger.info(f"[OK] Saved LaTeX: {latex_path}")
        print(f"[OK] Saved LaTeX: {latex_path}")
        
    except Exception as e:
        logger.error(f"Error saving LaTeX file: {e}")
        print(f"[ERROR] Failed to save LaTeX: {e}")

def generate_manuscript_text(df: pd.DataFrame) -> str:
    """
    Generate text for Materials & Methods section.
    
    Args:
        df: DataFrame with scene metadata
    
    Returns:
        Formatted text for manuscript
    """
    try:
        # Filter out summary row
        df_data = df[~df['Scene_ID'].str.contains('SUMMARY', na=False)].copy()
        
        if len(df_data) == 0:
            logger.warning("No data for manuscript text generation")
            return "No Sentinel-2 scene data available."
        
        total_scenes = len(df_data)
        date_range = f"{df_data['Acquisition_Date'].iloc[0]} to {df_data['Acquisition_Date'].iloc[-1]}"
        mean_cloud = df_data['Cloud_Cover_Percent'].mean()
        unique_tiles = df_data['Tile_ID'].nunique()
        data_source = df_data['Data_Source'].