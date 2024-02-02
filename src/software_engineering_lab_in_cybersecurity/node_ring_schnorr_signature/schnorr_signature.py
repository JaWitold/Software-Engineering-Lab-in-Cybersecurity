"""
This module implements the Schnorr signature scheme using elliptic curve cryptography as defined over the BN128 curve.
It provides functionality to sign messages and verify signatures according to the Schnorr signature protocol.
This implementation is intended for educational and research purposes in software engineering and cybersecurity fields,
especially focusing on blockchain technology and cryptographic protocols.

.. note::
    This module is designed for educational and research purposes and may not be suitable for production
    environments without further security assessments and optimizations.
"""

from py_ecc.bn128 import G1, add, multiply
from py_ecc.typing import Field, Point2D

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.elliptic_curve import (
    convert_bn128_point_to_coordinates,
    generate_random_scalar,
)
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.utility import (
    sol_hash,
)

SchnorrSignatureType = Point2D[Field], int


class SchnorrSignature:
    """
    Implements Schnorr signature scheme operations, including signing and verification
    of messages using elliptic curve cryptography.
    """

    @staticmethod
    def sign(message: int, private_key: int) -> SchnorrSignatureType:
        """
        Generates a Schnorr signature for a given message using the sender's private key.

        This method uses an ephemeral key pair for the signing process, computes a hash
        value using the public part of the ephemeral key and the message, and calculates
        the signature by combining the ephemeral private key, the signer's private key, and the hash.

        :param message: The message to be signed.
        :type message: int
        :param private_key: The private key of the signer.
        :type private_key: int
        :return: A tuple containing the elliptic curve point (public part of the ephemeral key)
                 and the signature value.
        :rtype: SchnorrSignatureType
        """
        ephemeral_value = generate_random_scalar()
        public_ephemeral_value = multiply(G1, ephemeral_value)
        h = sol_hash(
            *convert_bn128_point_to_coordinates(public_ephemeral_value), message
        )
        return public_ephemeral_value, ephemeral_value + (private_key * h)

    @staticmethod
    def verify(
        message: int, signature: SchnorrSignatureType, public_key: Point2D[Field]
    ) -> bool:
        """
        Verifies a Schnorr signature for a given message and public key.

        This method determines if the provided signature corresponds to the message and the public key
        by recalculating the hash with the message and the public part of the ephemeral key, and then
        verifying the elliptic curve equation associated with the Schnorr signature.

        :param message: The message corresponding to the signature.
        :type message: int
        :param signature: The signature to be verified, represented as an elliptic curve point and an integer.
        :type signature: SchnorrSignatureType
        :param public_key: The public key associated with the signature.
        :type public_key: Point2D[Field]
        :return: True if the signature is valid for the given message and public key, False otherwise.
        :rtype: bool
        """
        r, s = signature
        h = sol_hash(*convert_bn128_point_to_coordinates(r), message)
        return multiply(G1, s) == add(r, multiply(public_key, h))
