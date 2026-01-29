
import sys
sys.path.insert(0, '.')
try:
    import numpy as np
    print(f"  numpy: OK ({np.__version__})")
    
    import config.otu_config
    print(f"  config.otu_config: OK")
    
    from otu.otu_logic import compute_q_si, compute_q_bi, compute_otu_index
    print(f"  otu.otu_logic: OK")
    
    print("  [SUCCESS] All imports work")
except Exception as e:
    print(f"  [ERROR] Import failed: {e}")
    sys.exit(1)
