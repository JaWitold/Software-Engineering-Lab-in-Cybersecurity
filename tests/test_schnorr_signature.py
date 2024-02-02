import random
import unittest

from py_ecc.bn128 import G1, multiply

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.schnorr_signature import (
    SchnorrSignature,
)

__author__ = "Witold Karaś"
__copyright__ = "Witold Karaś"
__license__ = "MIT"
__email__ = "<witekkaras00@gmail.com>"


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
            message = random.randint(1, 0xFFFFFF)
            sk = random.randint(1, 0xFFFFFF)
            pk = multiply(G1, sk)
            self.assertTrue(
                SchnorrSignature.verify(
                    message, SchnorrSignature.sign(message, sk), pk
                ),
                "Signature should verify with matching message and keys.",
            )

    def test_schnorr_signature_fails_for_forged_message(self):
        """
        Test that a Schnorr signature fails to verify for a forged message.
        """
        for _ in range(10):
            message = random.randint(1, 0xFFFFFF)
            forged_message = random.randint(1, 0xFFFFFF)
            sk = random.randint(1, 0xFFFFFF)
            pk = multiply(G1, sk)
            self.assertFalse(
                SchnorrSignature.verify(
                    forged_message, SchnorrSignature.sign(message, sk), pk
                ),
                "Signature verification should fail for forged message.",
            )

    def test_schnorr_signature_fails_for_not_matching_key(self):
        """
        Test that a Schnorr signature fails to verify with a public key that does not match the signer's key.
        """
        for _ in range(10):
            message = random.randint(1, 0xFFFFFF)
            sk = random.randint(1, 0xFFFFFF)
            sk_2 = random.randint(1, 0xFFFFFF)
            pk = multiply(G1, sk_2)
            self.assertFalse(
                SchnorrSignature.verify(
                    message, SchnorrSignature.sign(message, sk), pk
                ),
                "Signature verification should fail with non-matching public key.",
            )


if __name__ == "__main__":
    unittest.main()
