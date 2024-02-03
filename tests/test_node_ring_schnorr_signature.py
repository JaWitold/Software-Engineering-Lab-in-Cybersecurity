import unittest

from conftest import get_random_int
from py_ecc.bn128 import G1, multiply

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.node_ring_schnorr_signature import (
    NodeRingSchnorrSignature,
)

__author__ = "Witold Karaś"
__copyright__ = "Witold Karaś"
__license__ = "MIT"
__email__ = "<witekkaras00@gmail.com>"


class TestNodeRingSchnorrSignature(unittest.TestCase):
    """
    Unit tests for the Node Ring Schnorr signature scheme implementation.

    Tests cover signature verification, failure cases for forged messages, and
    signature validation with non-matching public keys, ensuring the Node Ring Schnorr
    signature behaves as expected under various scenarios.
    """

    def test_node_ring_schnorr_signature_verifies(self):
        """
        Test that a Node Ring Schnorr signature correctly verifies with matching message and keys.
        """
        message = get_random_int()
        sk = get_random_int()
        pks = [multiply(G1, 1), multiply(G1, 2), multiply(G1, 3), multiply(G1, 4)]
        # print(node_ring_signature)
        self.assertTrue(
            NodeRingSchnorrSignature.sign(message, sk, pks).verify(message),
            "Signature should verify with matching message and keys.",
        )

    def test_node_ring_schnorr_signature_fails_for_forged_message(self):
        """
        Test that a Node Ring Schnorr signature fails for forged message.
        """
        message = get_random_int()
        forged_message = get_random_int()
        sk = get_random_int()
        pks = [multiply(G1, get_random_int()), multiply(G1, get_random_int()), multiply(G1, get_random_int())]
        # print(node_ring_signature)
        self.assertFalse(
            NodeRingSchnorrSignature.sign(message, sk, pks).verify(forged_message),
            "Signature should fail for forged message and keys.",
        )

    def test_node_ring_schnorr_signature_fails_for_invalid_sub_signature(self):
        """
        Test that a Node Ring Schnorr signature fails for forged message.
        """
        message = get_random_int()
        forged_message = get_random_int()
        sk = get_random_int()
        pks = [multiply(G1, get_random_int()), multiply(G1, get_random_int()), multiply(G1, get_random_int())]
        signature = NodeRingSchnorrSignature.sign(message, sk, pks)
        signature.sub_signatures[0].s += 1
        self.assertFalse(
            signature.verify(forged_message),
            "Signature should fail for forged message and keys.",
        )

    def test_node_ring_schnorr_signature_verifies_for_empty_ring(self):
        """
        Test that a Node Ring Schnorr signature fails for forged message.
        """
        message = get_random_int()
        sk = get_random_int()
        # print(node_ring_signature)
        self.assertTrue(
            NodeRingSchnorrSignature.sign(message, sk, []).verify(message),
            "Signature should verify with matching message and keys.",
        )


if __name__ == "__main__":
    unittest.main()
