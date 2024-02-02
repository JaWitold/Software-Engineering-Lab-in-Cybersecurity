import random

from py_ecc.bn128 import G1, multiply

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.schnorr_signature import (
    SchnorrSignature,
)

__author__ = "Witold Karaś"
__copyright__ = "Witold Karaś"
__license__ = "MIT"


def test_schnorr_signature_verifies():
    """Convert BN128 Point to Coordinates Tests"""
    for _ in range(10):
        m = random.randint(1, 0xFFFFFF)
        sk = random.randint(1, 0xFFFFFF)
        pk = multiply(G1, sk)
        assert SchnorrSignature.verify(m, SchnorrSignature.sign(m, sk), pk)
