"""Utility class for elliptic curves operations."""

from random import randint

from py_ecc.bn128 import G1, curve_order


def generate_random_scalar():
    """
    Generate a random scalar within the valid range of the elliptic curve group order.

    Returns:
        int: A random integer between 1 and `curve_order - 1`.
    """
    return randint(1, curve_order - 1)


def convert_bn128_point_to_coordinates(point: G1):
    """
    Convert a BN128 curve point into a list of its x and y coordinates.

    Args:
        point (Tuple[FQ, FQ]): A point on the curve represented as a tuple of FQ elements.

    Returns:
        List[int]: A list containing the x and y coordinates of the point as integers.
    """
    return [int(point[0]), int(point[1])]
