"""
Module: schnorr_signature
This module provides implementation for Schnorr signature algorithm.
"""
from typing import Tuple
from py_ecc.bn128 import multiply, add, curve_order, G1, field_modulus
from .util import keccak256, encode_packed, randsn, addmodn, mulmodn


class SchnorrSignature:
    """
    Schnorr Signature implementation.

    This class provides methods for signing and verifying Schnorr signatures.
    """

    def hash(self, b: bytes) -> int:
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
        return int.from_bytes(keccak256(b), byteorder="big") % curve_order

    def sign(self, privkey: int, message: int):
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
        x = randsn()
        x_ = multiply(G1, x)

        # h = Hash(X, message)
        h = self.hash(encode_packed(x_[0].n, x_[1].n, message))

        # s = x + a * h
        s = addmodn(x, mulmodn(privkey, h))

        return pubkey, (x_, s)

    def verify(self, pubkey: int, message: int, signature: Tuple[int, int]) -> bool:
        """
        This function verifies schnorr signature with given public key over the message

        Args:
            pubkey (int): Public key.
            message (int): Message correspodning to signature.
            signature (tuple): Signature to be verified.

        Returns:
            bool: True if signature is verified, else False
        """
        x_, s = signature

        # h = Hash(X, message)
        h = self.hash(encode_packed(x_[0].n, x_[1].n, message))

        # sG = s * G
        sg_ = multiply(G1, s)

        # hA = h * A
        ha_ = multiply(pubkey, h)

        # X + hA
        xha_ = add(x_, ha_)

        # Verify that s * G = X + h * A
        return sg_ == xha_


if __name__ == "__main__":

    FIELD_ORDER = int(
        "0x30644e72e131a029b85045b68181585d97816a916871ca8d3c208c16d87cfd47", 16)
    GEN_ORDER = int(
        "0x30644e72e131a029b85045b68181585d2833e84879b9709143e1f593f0000001", 16)

    print(f"{FIELD_ORDER=}\n{GEN_ORDER=}")
    print(f"{curve_order=}\n{field_modulus=}")

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
