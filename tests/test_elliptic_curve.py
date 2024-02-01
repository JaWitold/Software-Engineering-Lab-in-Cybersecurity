from py_ecc.bn128 import G1, curve_order

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.elliptic_curve import (
    convert_bn128_point_to_coordinates,
    generate_random_scalar,
)

__author__ = "Witold Karaś"
__copyright__ = "Witold Karaś"
__license__ = "MIT"


def test_convert_bn128_point_to_coordinates():
    """Convert BN128 Point to Coordinates Tests"""
    assert convert_bn128_point_to_coordinates(G1) == [1, 2]


def test_generate_random_scalar():
    """Generate Random Scalar Tests"""
    for _ in range(1000):
        scalar = generate_random_scalar()
        assert 1 <= scalar < curve_order
