import unittest

from conftest import get_random_int
from py_ecc.bn128 import G1, multiply

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.schnorr_signature import (
    SchnorrSignature,
)


class TestSchnorrSignature(unittest.TestCase):
    """
    Unit tests for the Schnorr signature scheme implementation.

    Tests cover signature verification, failure cases for forged messages, and
    signature validation with non-matching public keys, ensuring the Schnorr
    signature behaves as expected under various scenarios.
    """

    def test_schnorr_signature_verifies(self):
        """
        Test that a Schnorr signature correctly verifies with matching message and keys.
        """
        for _ in range(10):
            message = get_random_int()
            sk = get_random_int()
            pk = multiply(G1, sk)
            signature = SchnorrSignature.sign(message, sk)
            self.assertTrue(
                signature.verify(message, pk),
                "Signature should verify with matching message and keys.",
            )

    def test_schnorr_signature_fails_for_forged_message(self):
        """
        Test that a Schnorr signature fails to verify for a forged message.
        """
        for _ in range(10):
            message = get_random_int()
            forged_message = get_random_int()
            sk = get_random_int()
            pk = multiply(G1, sk)
            signature = SchnorrSignature.sign(message, sk)
            self.assertFalse(
                signature.verify(forged_message, pk),
                "Signature verification should fail for forged message.",
            )

    def test_schnorr_signature_fails_for_not_matching_key(self):
        """
        Test that a Schnorr signature fails to verify with a public key that does not match the signer's key.
        """
        for _ in range(10):
            message = get_random_int()
            sk = get_random_int()
            sk_2 = get_random_int()
            pk = multiply(G1, sk_2)
            signature = SchnorrSignature.sign(message, sk)
            self.assertFalse(
                signature.verify(message, pk),
                "Signature verification should fail with non-matching public key.",
            )


if __name__ == "__main__":
    unittest.main()
