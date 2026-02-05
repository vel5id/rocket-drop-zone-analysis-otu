import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
from core.algorithms import algorithm_6_impact_probability_calculation
from core.dto import DispersionEllipse, GeoPoint, ImpactPoint

class TestAlgorithm6(unittest.TestCase):
    def test_probability_distribution(self):
        # Setup similar to verification script
        center = GeoPoint(45.0, 60.0, 0.0)
        ellipse = DispersionEllipse(
            center=center,
            semi_major_axis=3000.0,
            semi_minor_axis=1000.0,
            orientation=45.0,
            sigma_level=3
        )

        # Grid around center
        min_lat, max_lat = 44.98, 45.02
        min_lon, max_lon = 59.97, 60.03

        grid_cells = []
        step = 0.002

        lat = min_lat
        while lat < max_lat - 1e-9:
            lon = min_lon
            while lon < max_lon - 1e-9:
                grid_cells.append((lat, lat + step, lon, lon + step))
                lon += step
            lat += step

        # Impact points are ignored by the algo but required by signature
        impact_points = []

        probs = algorithm_6_impact_probability_calculation(impact_points, grid_cells, ellipse)

        # Checks
        total_prob = np.sum(probs)
        print(f"Total probability: {total_prob}")

        # Expectation: Total probability close to 1
        self.assertTrue(0.9 < total_prob < 1.1, f"Total probability {total_prob} should be close to 1")

        # Peak probability should be at the cell closest to center
        # Center cell index
        # We constructed the grid linearly.
        # Let's find index of cell containing (45.0, 60.0)
        max_p_idx = np.argmax(probs)
        max_cell = grid_cells[max_p_idx]

        # Check if the peak cell contains the center
        self.assertLessEqual(max_cell[0], 45.0 + 1e-9)
        self.assertGreaterEqual(max_cell[1], 45.0 - 1e-9)
        self.assertLessEqual(max_cell[2], 60.0 + 1e-9)
        self.assertGreaterEqual(max_cell[3], 60.0 - 1e-9)

    def test_empty_grid(self):
        center = GeoPoint(45.0, 60.0, 0.0)
        ellipse = DispersionEllipse(center, 3000, 1000, 45, 3)
        probs = algorithm_6_impact_probability_calculation([], [], ellipse)
        self.assertEqual(len(probs), 0)

if __name__ == '__main__':
    unittest.main()
