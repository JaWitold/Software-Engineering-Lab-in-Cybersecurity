import unittest

from py_ecc.bn128 import G1, curve_order

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.elliptic_curve import (
    convert_bn128_point_to_coordinates,
    generate_random_scalar,
)

__author__ = "Witold Karaś"
__copyright__ = "Witold Karaś"
__license__ = "MIT"
__email__ = "<witekkaras00@gmail.com>"


class TestEllipticCurveOperations(unittest.TestCase):
    """Unit tests for elliptic curve operations."""

    def test_convert_bn128_point_to_coordinates(self):
        """Test that G1 point is correctly converted to its x and y coordinates."""
        self.assertEqual(
            convert_bn128_point_to_coordinates(G1),
            [1, 2],
            "G1 point coordinates do not match expected values.",
        )

    def test_generate_random_scalar(self):
        """Test that generated scalars are within the valid range of the elliptic curve group order."""
        for _ in range(1000):
            scalar = generate_random_scalar()
            self.assertTrue(
                1 <= scalar < curve_order, "Generated scalar is out of valid range."
            )


if __name__ == "__main__":
    unittest.main()
