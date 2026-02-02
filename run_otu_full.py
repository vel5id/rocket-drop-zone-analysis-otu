"""Run OTU calculation on full grid using the fixed calculator.

This script uses the refactored OTUCalculator with all bug fixes applied.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from otu.calculator import OTUCalculator
from otu.chunk_manager import ChunkManager

def main():
    print("="*70)
    print("OTU PIPELINE - FULL GRID")
    print("="*70)
    
    # Define your full area of interest
    # TODO: Replace these with your actual coordinates
    min_lat = 46.5
    max_lat = 48.0  # ~166 km north
    min_lon = 65.5
    max_lon = 67.5  # ~150 km east (at this latitude)
    
    cell_size_km = 1.0
    target_date = "2024-09-09"
    
    print(f"\nConfiguration:")
    print(f"  Area: {min_lat}°-{max_lat}° N, {min_lon}°-{max_lon}° E")
    print(f"  Cell size: {cell_size_km} km")
    print(f"  Date: {target_date}")
    
    # Estimate grid size
    lat_range = max_lat - min_lat
    lon_range = max_lon - min_lon
    estimated_cells = int((lat_range * 111) * (lon_range * 111 * 0.7) / (cell_size_km ** 2))
    print(f"  Estimated cells: ~{estimated_cells}")
    
    # Confirm
    response = input(f"\nProceed with calculation? This may take 30-60 minutes. (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Create chunk manager
    print("\nCreating grid...")
    manager = ChunkManager.from_bounds(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        chunk_size_km=cell_size_km,
    )
    
    print(f"Created {len(manager.chunks)} chunks")
    
    # Create calculator
    calculator = OTUCalculator(
        chunk_manager=manager,
        output_dir=Path("output/otu")
    )
    
    # Run calculation
    print(f"\nStarting OTU calculation...")
    print("Progress will be shown below.\n")
    
    try:
        results = calculator.calculate_single_day(
            target_date=target_date,
            show_progress=True,
            use_cache=True  # Enable cache for faster re-runs
        )
        
        # Summary
        print("\n" + "="*70)
        print("CALCULATION COMPLETE")
        print("="*70)
        
        stats = results['statistics']
        
        # Calculate summary from chunks
        chunks = manager.chunks
        total_chunks = len(chunks)
        processed_chunks = len([c for c in chunks if c.is_processed])
        failed_chunks = len([c for c in chunks if c.error])
        
        print(f"\nProcessing Summary:")
        print(f"  Total chunks:    {total_chunks}")
        print(f"  Processed:       {processed_chunks}")
        print(f"  Failed:          {failed_chunks}")
        
        print(f"\nOTU Statistics:")
        print(f"  Mean:   {stats['mean']:.4f}")
        print(f"  Median: {stats['median']:.4f}")
        print(f"  Min:    {stats['min']:.4f}")
        print(f"  Max:    {stats['max']:.4f}")
        print(f"  Std:    {stats['std']:.4f}")
        
        print(f"\nOutput saved to: {results['output_path']}")
        
        # Data quality report
        chunks = manager.chunks
        chunks_missing_ndvi = [c for c in chunks if "ndvi" in c.missing_data]
        chunks_missing_soil = [c for c in chunks if "soil" in c.missing_data]
        chunks_missing_relief = [c for c in chunks if "relief" in c.missing_data]
        
        print(f"\nData Quality:")
        print(f"  NDVI missing:   {len(chunks_missing_ndvi)}/{len(chunks)} ({100*len(chunks_missing_ndvi)/len(chunks):.1f}%)")
        print(f"  Soil missing:   {len(chunks_missing_soil)}/{len(chunks)} ({100*len(chunks_missing_soil)/len(chunks):.1f}%)")
        print(f"  Relief missing: {len(chunks_missing_relief)}/{len(chunks)} ({100*len(chunks_missing_relief)/len(chunks):.1f}%)")
        
        if failed_chunks == 0 and len(chunks_missing_ndvi) < len(chunks) * 0.1:
            print("\n🎉 SUCCESS! Pipeline completed with high data quality.")
        elif failed_chunks == 0:
            print("\n✅ Pipeline completed, but some data is missing (see above).")
        else:
            print(f"\n⚠️  Pipeline completed with {failed_chunks} failures.")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
