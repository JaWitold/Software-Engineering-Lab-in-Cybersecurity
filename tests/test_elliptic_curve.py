import unittest

from py_ecc.bn128 import G1, curve_order

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.elliptic_curve import (
    convert_point_2d_to_list,
    generate_random_scalar,
    sum_coordinates,
)


class TestEllipticCurveOperations(unittest.TestCase):
    """Unit tests for elliptic curve operations."""

    def test_convert_point_2d_to_list(self):
        """Test that G1 point is correctly converted to its x and y coordinates."""
        self.assertEqual(
            convert_point_2d_to_list(G1),
            [1, 2],
            "G1 point coordinates do not match expected values.",
        )

    def test_generate_random_scalar(self):
        """Test that generated scalars are within the valid range of the elliptic curve group order."""
        for _ in range(1000):
            scalar = generate_random_scalar()
            self.assertTrue(1 <= scalar < curve_order, "Generated scalar is out of valid range.")

    def test_coordinate_sum(self):
        """Test that generated scalars are within the valid range of the elliptic curve group order."""
        self.assertEqual(
            sum_coordinates(G1),
            3,
            "sum coordinates do not match expected values.",
        )


if __name__ == "__main__":
    unittest.main()
