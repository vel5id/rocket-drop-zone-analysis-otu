"""Test OTU pipeline with a small 10x10 grid to verify all fixes work correctly.

This script creates a manageable test area and runs the full OTU calculation
to verify NDVI retrieval, soil data, relief data, and final OTU computation.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from otu.calculator import OTUCalculator
from otu.chunk_manager import ChunkManager
from datetime import datetime

def test_small_grid():
    print("="*70)
    print("OTU PIPELINE TEST - SMALL GRID (10x10 = 100 chunks)")
    print("="*70)
    
    # Define test area (Kazakhstan region)
    # Adjust these coordinates to your actual area of interest
    min_lat = 47.0
    max_lat = 47.1  # ~11 km north
    min_lon = 66.0
    max_lon = 66.15  # ~11 km east (at this latitude)
    
    print(f"\nTest Area:")
    print(f"  Latitude:  {min_lat}° to {max_lat}°")
    print(f"  Longitude: {min_lon}° to {max_lon}°")
    print(f"  Cell size: 1 km")
    
    # Create chunk manager
    manager = ChunkManager.from_bounds(
        min_lat=min_lat,
        max_lat=max_lat,
        min_lon=min_lon,
        max_lon=max_lon,
        chunk_size_km=1.0,
    )
    
    print(f"\nCreated {len(manager.chunks)} chunks")
    
    # Create calculator
    calculator = OTUCalculator(
        chunk_manager=manager,
        output_dir=Path("output/otu_test")
    )
    
    # Run calculation
    target_date = "2024-09-09"
    print(f"\nRunning OTU calculation for {target_date}...")
    print("This will take ~2-5 minutes depending on GEE response time.\n")
    
    try:
        results = calculator.calculate_single_day(
            target_date=target_date,
            show_progress=True,
            use_cache=False  # Force fresh data to test everything
        )
        
        # Analyze results
        print("\n" + "="*70)
        print("ANALYSIS")
        print("="*70)
        
        chunks = manager.chunks
        chunks_with_ndvi = [c for c in chunks if c.q_vi > 0.0]
        chunks_missing_ndvi = [c for c in chunks if "ndvi" in c.missing_data]
        chunks_missing_soil = [c for c in chunks if "soil" in c.missing_data]
        chunks_missing_relief = [c for c in chunks if "relief" in c.missing_data]
        
        print(f"\nData Availability:")
        print(f"  NDVI retrieved:     {len(chunks_with_ndvi)}/{len(chunks)} ({100*len(chunks_with_ndvi)/len(chunks):.1f}%)")
        print(f"  NDVI missing:       {len(chunks_missing_ndvi)}/{len(chunks)}")
        print(f"  Soil missing:       {len(chunks_missing_soil)}/{len(chunks)}")
        print(f"  Relief missing:     {len(chunks_missing_relief)}/{len(chunks)}")
        
        # NDVI statistics
        if chunks_with_ndvi:
            ndvi_values = [c.q_vi for c in chunks_with_ndvi]
            print(f"\nNDVI Statistics:")
            print(f"  Min:  {min(ndvi_values):.4f}")
            print(f"  Max:  {max(ndvi_values):.4f}")
            print(f"  Mean: {sum(ndvi_values)/len(ndvi_values):.4f}")
        
        # OTU statistics
        stats = results['statistics']
        print(f"\nOTU Statistics:")
        print(f"  Mean: {stats['mean']:.4f}")
        print(f"  Min:  {stats['min']:.4f}")
        print(f"  Max:  {stats['max']:.4f}")
        print(f"  MAD:  {stats['mad']:.4f}")
        
        # Success criteria
        print(f"\n" + "="*70)
        print("SUCCESS CRITERIA")
        print("="*70)
        
        success = True
        
        if len(chunks_with_ndvi) == 0:
            print("❌ FAIL: No NDVI data retrieved")
            success = False
        else:
            print(f"✅ PASS: NDVI data retrieved for {len(chunks_with_ndvi)} chunks")
        
        if stats['mean'] < 0.01:
            print("❌ FAIL: OTU values suspiciously low")
            success = False
        else:
            print(f"✅ PASS: OTU values in reasonable range ({stats['mean']:.3f})")
        
        if results['summary']['failed'] > 0:
            print(f"⚠️  WARNING: {results['summary']['failed']} chunks failed")
        else:
            print("✅ PASS: All chunks processed successfully")
        
        print(f"\nOutput saved to: {results['output_path']}")
        
        if success:
            print("\n🎉 ALL TESTS PASSED! Pipeline is working correctly.")
        else:
            print("\n⚠️  SOME TESTS FAILED. Check the output above.")
        
        return success
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_small_grid()
    sys.exit(0 if success else 1)
