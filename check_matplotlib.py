"""
Quick check if matplotlib.path is available in the environment.
"""
try:
    from matplotlib.path import Path
    import numpy as np
    
    print("✅ matplotlib.path is AVAILABLE")
    
    # Test basic functionality
    polygon = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
    path = Path(polygon)
    
    test_points = np.array([[0.5, 0.5], [2.0, 2.0]])
    result = path.contains_points(test_points)
    
    print(f"✅ Test: Point (0.5, 0.5) inside: {result[0]}")
    print(f"✅ Test: Point (2.0, 2.0) inside: {result[1]}")
    
    if result[0] and not result[1]:
        print("\n✅ matplotlib.path is WORKING CORRECTLY")
    else:
        print("\n❌ matplotlib.path logic is BROKEN")
        
except ImportError as e:
    print(f"❌ matplotlib.path is NOT AVAILABLE: {e}")
    print("\n⚠️  Grid generation will use FALLBACK ray-casting")
    print("   This may be the cause of the rectangular grid bug!")
