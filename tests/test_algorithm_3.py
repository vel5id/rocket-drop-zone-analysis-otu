import unittest
import numpy as np
from core.algorithms import algorithm_3_dispersion_ellipse_calculation
from core.dto import ImpactPoint, GeoPoint
from core.geo_utils import EARTH_RADIUS_M

class TestAlgorithm3(unittest.TestCase):
    def test_ellipse_calculation_basic(self):
        # Create points in a cross shape
        # Center at (45, 60)
        # We'll use points that should result in an axis-aligned ellipse
        lat_center = 45.0
        lon_center = 60.0

        # 1000 meters North/South
        dlat = np.degrees(1000.0 / EARTH_RADIUS_M)
        # 500 meters East/West
        dlon = np.degrees(500.0 / (EARTH_RADIUS_M * np.cos(np.radians(lat_center))))

        points = [
            ImpactPoint(lat_center + dlat, lon_center, 0.0, 0.0, 0.0, 0),
            ImpactPoint(lat_center - dlat, lon_center, 0.0, 0.0, 0.0, 1),
            ImpactPoint(lat_center, lon_center + dlon, 0.0, 0.0, 0.0, 2),
            ImpactPoint(lat_center, lon_center - dlon, 0.0, 0.0, 0.0, 3)
        ]

        # With points at +/- 1000m and +/- 500m from mean:
        # dy = [1000, -1000, 0, 0], var = 2/3 * 10^6
        # dx = [0, 0, 500, -500], var = 1/6 * 10^6
        # sqrt(eigenvalues) = 1000 * sqrt(2/3) approx 816.5 and 500 * sqrt(2/3) approx 408.2

        ellipse = algorithm_3_dispersion_ellipse_calculation(points, sigma_level=1)

        self.assertAlmostEqual(ellipse.center.latitude, lat_center)
        self.assertAlmostEqual(ellipse.center.longitude, lon_center)

        expected_major = 1000.0 * np.sqrt(2.0/3.0)
        expected_minor = 500.0 * np.sqrt(2.0/3.0)

        self.assertAlmostEqual(ellipse.semi_major_axis, expected_major, delta=0.1)
        self.assertAlmostEqual(ellipse.semi_minor_axis, expected_minor, delta=0.1)
        self.assertAlmostEqual(ellipse.orientation, 0.0, delta=0.1)

        # Check 2D confidence
        expected_conf = 1.0 - np.exp(-1.0**2 / 2.0)
        self.assertAlmostEqual(ellipse.confidence, expected_conf, delta=0.001)

    def test_ellipse_calculation_rotated(self):
        lat_center = 45.0
        lon_center = 60.0

        # Points along 45 degree line (NE-SW)
        dist = 1000.0
        dy = dist * np.cos(np.radians(45))
        dx = dist * np.sin(np.radians(45))

        dlat = np.degrees(dy / EARTH_RADIUS_M)
        dlon = np.degrees(dx / (EARTH_RADIUS_M * np.cos(np.radians(lat_center))))

        points = [
            ImpactPoint(lat_center + dlat, lon_center + dlon, 0.0, 0.0, 0.0, 0),
            ImpactPoint(lat_center - dlat, lon_center - dlon, 0.0, 0.0, 0.0, 1),
        ]

        ellipse = algorithm_3_dispersion_ellipse_calculation(points, sigma_level=1)

        self.assertAlmostEqual(ellipse.orientation, 45.0, delta=0.1)
        self.assertGreater(ellipse.semi_major_axis, 0)
        self.assertAlmostEqual(ellipse.semi_minor_axis, 0, delta=0.001)

    def test_empty_points(self):
        ellipse = algorithm_3_dispersion_ellipse_calculation([], sigma_level=3)
        self.assertEqual(ellipse.sigma_level, 3)
        self.assertGreater(ellipse.semi_major_axis, 0)
        expected_conf = 1.0 - np.exp(-3.0**2 / 2.0)
        self.assertAlmostEqual(ellipse.confidence, expected_conf, delta=0.001)

    def test_single_point(self):
        points = [ImpactPoint(45.0, 60.0, 0.0, 0.0, 0.0, 0)]
        ellipse = algorithm_3_dispersion_ellipse_calculation(points, sigma_level=3)
        self.assertEqual(ellipse.center.latitude, 45.0)
        self.assertEqual(ellipse.center.longitude, 60.0)
        self.assertEqual(ellipse.semi_major_axis, 0.0)
        self.assertEqual(ellipse.confidence, 0.0)

if __name__ == "__main__":
    unittest.main()
