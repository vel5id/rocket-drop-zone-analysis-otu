"""Test NDVI retrieval with minimal chunks to verify the fix."""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from otu.calculator import OTUCalculator
from otu.chunk_manager import ChunkManager

def test_ndvi_fix():
    print("="*60)
    print("TESTING NDVI FIX")
    print("="*60)
    
    # Create a small test area (just 4 chunks)
    manager = ChunkManager.from_bounds(
        min_lat=47.0, max_lat=47.02,
        min_lon=66.0, max_lon=66.02,
        chunk_size_km=1.0,
    )
    
    print(f"Created {len(manager.chunks)} test chunks")
    
    calculator = OTUCalculator(chunk_manager=manager)
    
    try:
        results = calculator.calculate_single_day(
            target_date="2024-09-09",
            show_progress=True,
            use_cache=False  # Force fresh GEE query
        )
        
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        print(f"Statistics: {results['statistics']}")
        
        # Check if we got any non-zero NDVI values
        chunks_with_ndvi = [c for c in manager.chunks if c.q_vi > 0.0]
        print(f"\nChunks with NDVI > 0.0: {len(chunks_with_ndvi)}/{len(manager.chunks)}")
        
        if len(chunks_with_ndvi) > 0:
            print("✅ SUCCESS: NDVI data retrieved!")
        else:
            print("⚠️  WARNING: All NDVI values are still 0.0")
            print("   This might be expected if there's truly no Sentinel-2 data for this region/date.")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ndvi_fix()
