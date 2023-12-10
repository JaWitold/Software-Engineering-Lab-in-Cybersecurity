"""
Module: schnorr_signature
This module provides implementation for Schnorr signature algorithm.
"""
from typing import Tuple

from py_ecc.bn128 import multiply, add, curve_order, G1

from .util import keccak256, encode_packed, randsn, addmodn, mulmodn


class SchnorrSignature:
    """
    Schnorr Signature implementation.

    This class provides methods for signing and verifying Schnorr signatures.
    """

    @staticmethod
    def hash(in_bytes: bytes) -> int:
        """
        This function takes a byte sequence, computes its Keccak256 hash,
        interprets the hash as an integer in big-endian byte order
        and then returns the result after taking the modulo with a given curve order.

        Args:
            b (bytes): The byte sequence to be hashed and converted to an integer.

        Returns:
            int: The resulting integer after converting the Keccak256 hash
                 and applying the modulo operation.
        """
        return int.from_bytes(keccak256(in_bytes), byteorder="big") % curve_order

    @staticmethod
    def sign(privkey: int, message: int):
        """
        This function computes schnorr signature with given private key over the message

        Args:
            privkey (int): Private key.
            message (int): Message to be signed.

        Returns:
            tuple: Public key to verify signature, signature over the message
        """
        pubkey = multiply(G1, privkey)

        # X = G * x
        priv_ephemeral_val = randsn()
        public_ephemeral_val = multiply(G1, priv_ephemeral_val)

        # h = Hash(X, message)
        hash_val = int.from_bytes(
            keccak256(encode_packed(public_ephemeral_val[0].n, public_ephemeral_val[1].n, message)),
            'big') % curve_order

        # s = x + a * h
        small_s = addmodn(priv_ephemeral_val, mulmodn(privkey, hash_val))

        return pubkey, (public_ephemeral_val, small_s)

    @staticmethod
    def verify(pubkey: Tuple, message: int, signature: Tuple[int, int]) -> bool:
        """
        This function verifies schnorr signature with given public key over the message

        Args:
            pubkey (int): Public key.
            message (int): Message corresponding to signature.
            signature (tuple): Signature to be verified.

        Returns:
            bool: True if signature is verified, else False
        """
        public_ephemeral_val, small_s = signature

        # h = Hash(X, message)
        hash_val = int.from_bytes(
            keccak256(
                encode_packed(
                    public_ephemeral_val[0].n,
                    public_ephemeral_val[1].n,
                    message)
            ), 'big'
        ) % curve_order
        # sG = s * G
        geneator_to_small_s = multiply(G1, small_s)

        # hA = h * A
        hash_times_pubkey = multiply(pubkey, hash_val)

        # X + hA
        result = add(public_ephemeral_val, hash_times_pubkey)

        # Verify that s * G = X + h * A
        return geneator_to_small_s == result


if __name__ == "__main__":
    ss = SchnorrSignature()

    PRIVKEY_1 = 19977808579986318922850133509558564821349392755821541651519240729619349670944
    PRIVKEY_2 = 34783947491279721981739821

    MESSAGE = 123

    pubkey_1, signature_1 = ss.sign(PRIVKEY_1, 123)
    pubkey_2, signature_2 = ss.sign(PRIVKEY_2, 123)
    assert ss.verify(pubkey_1, MESSAGE, signature_1)
    assert ss.verify(pubkey_2, MESSAGE, signature_2)
    assert not ss.verify(pubkey_1, 124, signature_1)
    assert not ss.verify(pubkey_2, 124, signature_2)
    assert not ss.verify(pubkey_1, MESSAGE, signature_2)
    assert not ss.verify(pubkey_2, MESSAGE, signature_1)
