"""
Test OTU Logic.
"""
import unittest
import numpy as np
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.otu_config import OTUConfig
from otu.otu_logic import compute_q_relief, compute_q_si, compute_q_bi, compute_aspect_modifier, compute_fire_risk

class TestOTULogic(unittest.TestCase):
    
    def test_relief_penalty_scalar(self):
        """Test relief penalty logic for scalars."""
        # Flat terrain (0 deg) -> Penalty 0 -> Q_Relief 1.0
        self.assertAlmostEqual(compute_q_relief(0, 0), 1.0)
        
        # Critical slope (20 deg) -> Penalty 0.5 -> Q_Relief 0.5
        # Formula: slope / (critical * 2) = 20 / 40 = 0.5
        self.assertAlmostEqual(compute_q_relief(20, 0), 0.5)
        
        # Steep slope (30 deg) -> Penalty > 0.5
        # Excess = 10. Penalty = 0.5 + (10/20)^2 = 0.5 + 0.25 = 0.75 -> Q_Relief 0.25
        self.assertAlmostEqual(compute_q_relief(30, 0), 0.25)
        
        # Very steep (40 deg) -> Penalty = 0.5 + (20/20)^2 = 1.5 -> Clamped to 1.0 -> Q_Relief 0.0
        self.assertAlmostEqual(compute_q_relief(40, 0), 0.0)
        
        # Water body -> Penalty 0.5 -> Q_Relief 0.5
        self.assertAlmostEqual(compute_q_relief(0, 1), 0.5)

    def test_aspect_modifier(self):
        """Test aspect (exposure) modifier."""
        # North (0) -> 1.0
        self.assertAlmostEqual(compute_aspect_modifier(0), 1.0)
        # North (360) -> 1.0
        self.assertAlmostEqual(compute_aspect_modifier(360), 1.0)
        # South (180) -> 0.6
        self.assertAlmostEqual(compute_aspect_modifier(180), 0.6)
        # East (90) -> ~0.8 (avg of 1.0 and 0.6)
        self.assertAlmostEqual(compute_aspect_modifier(90), 0.8)
        
    def test_fire_risk(self):
        """Test fire risk calculation."""
        # Low NDVI -> Low Risk
        self.assertEqual(compute_fire_risk(0.1), 0.0)
        # High NDVI -> High Risk
        self.assertEqual(compute_fire_risk(0.9), 1.0)
        # Mid NDVI (0.5) -> Mid Risk (0.5)
        self.assertAlmostEqual(compute_fire_risk(0.5), 0.5)
        
    def test_relief_with_aspect(self):
        """Test relief combined with aspect."""
        # Flat, North -> 1.0 * 1.0 = 1.0
        self.assertAlmostEqual(compute_q_relief(0, 0, 0), 1.0)
        # Flat, South -> 1.0 * 0.6 = 0.6
        self.assertAlmostEqual(compute_q_relief(0, 0, 180), 0.6)
        # Critical Slope (0.5), South (0.6) -> 0.3
        self.assertAlmostEqual(compute_q_relief(20, 0, 180), 0.3)
        
    def test_relief_penalty_vector(self):
        """Test relief penalty logic for arrays."""
        slopes = np.array([0, 20, 30, 40])
        water = np.array([0, 0, 0, 0])
        
        q_relief = compute_q_relief(slopes, water)
        
        expected = np.array([1.0, 0.5, 0.25, 0.0])
        np.testing.assert_allclose(q_relief, expected, atol=1e-5)

if __name__ == '__main__':
    unittest.main()
