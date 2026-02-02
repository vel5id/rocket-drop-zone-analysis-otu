"""Test NDVI with QA60 cloud mask instead of SCL.

This is a fallback test if the SCL mask is still too aggressive.
QA60 is a simpler bitmask-based cloud filter.
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from otu.calculator import OTUCalculator
from otu.chunk_manager import ChunkManager

def test_qa60_mask():
    print("="*60)
    print("TESTING NDVI WITH QA60 MASK (Simpler Cloud Filter)")
    print("="*60)
    
    # Create a small test area
    manager = ChunkManager.from_bounds(
        min_lat=47.0, max_lat=47.02,
        min_lon=66.0, max_lon=66.02,
        chunk_size_km=1.0,
    )
    
    print(f"Created {len(manager.chunks)} test chunks")
    print("\nNOTE: This test uses the MODIFIED calculator with relaxed SCL mask.")
    print("If this still fails, we need to implement QA60 mask in calculator.py\n")
    
    calculator = OTUCalculator(chunk_manager=manager)
    
    try:
        results = calculator.calculate_single_day(
            target_date="2024-09-09",
            show_progress=True,
            use_cache=False
        )
        
        print("\n" + "="*60)
        print("TEST RESULTS")
        print("="*60)
        
        # Check NDVI values
        chunks_with_ndvi = [c for c in manager.chunks if c.q_vi > 0.0]
        chunks_with_missing = [c for c in manager.chunks if "ndvi" in c.missing_data]
        
        print(f"Chunks with NDVI > 0.0: {len(chunks_with_ndvi)}/{len(manager.chunks)}")
        print(f"Chunks flagged as missing NDVI: {len(chunks_with_missing)}/{len(manager.chunks)}")
        
        if len(chunks_with_ndvi) > 0:
            print("\n✅ SUCCESS: NDVI data retrieved!")
            print(f"   Sample NDVI values: {[round(c.q_vi, 3) for c in chunks_with_ndvi[:3]]}")
        else:
            print("\n⚠️  STILL FAILING: All NDVI values are 0.0")
            print("   Next step: Implement QA60 mask directly in calculator.py")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qa60_mask()
