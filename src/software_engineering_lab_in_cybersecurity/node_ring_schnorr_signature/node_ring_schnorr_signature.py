"""
This module implements the Node Ring Schnorr signature scheme using ...
"""

import random
from typing import List, Tuple

from py_ecc.bn128 import G1, add, curve_order, eq, multiply, neg
from py_ecc.typing import Field, Point2D

from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.elliptic_curve import (
    convert_point_2d_to_list,
    generate_random_scalar,
    sum_coordinates,
)
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.schnorr_signature import (
    SchnorrSignature,
)
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.utility import (
    sol_hash,
)


class NodeRingSchnorrSignature:
    """
    Implements the Node Ring Schnorr signature scheme operations, including signing
    messages and verifying ring signatures.

    The Node Ring Schnorr signature scheme is an advanced cryptographic mechanism
    designed for ensuring the integrity and authenticity of messages in a
    decentralized network environment. It leverages the properties of elliptic curve
    cryptography and Schnorr signatures to provide security and privacy.

    :param signature_public_key: The public key corresponding to the signature.
    :type signature_public_key: Point2D[Field]
    :param ring_public_keys: A list of public keys forming the ring in which the
        signature is generated.
    :type ring_public_keys: List[Point2D[Field]]
    :param random_points: A list of random points used in the signature generation
        process.
    :type random_points: List[Point2D[Field]]
    :param sub_signatures: A list of Schnorr signatures that constitute the node ring
        signature.
    :type sub_signatures: List[SchnorrSignature]
    :param signature_sum: An integer representing the summation of the signature
        components.
    :type signature_sum: int
    """

    def __init__(
        self,
        signature_public_key: Point2D[Field],
        ring_public_keys: List[Point2D[Field]],
        random_points: List[Point2D[Field]],
        sub_signatures: List[SchnorrSignature],
        signature_sum: int,
    ) -> None:
        self.signature_public_key = signature_public_key
        self.ring_public_keys = ring_public_keys
        self.random_points = random_points
        self.sub_signatures = sub_signatures
        self.signature_sum = signature_sum

    @staticmethod
    def sign(message: int, private_key: int, ring_public_keys: List[Point2D[Field]]):
        """
        Generates a Node Ring Schnorr signature for a given message using the signer's
        private key and a list of ring public keys.

        :param message: The message to be signed, represented as an integer.
        :type message: int
        :param private_key: The private key of the signer, used to generate the
            signature.
        :type private_key: int
        :param ring_public_keys: A list of public keys that form the ring for the
            signature generation.
        :type ring_public_keys: List[Point2D[Field]]
        :return: An instance of `NodeRingSchnorrSignature` representing the generated
            signature.
        :rtype: NodeRingSchnorrSignature
        """

        # Step 1: Generate an ephemeral key pair
        signature_private_key, signature_public_key = NodeRingSchnorrSignature.__generate_signature_keys(
            message, private_key, ring_public_keys
        )

        # Step 2: Generate a list of unique random values
        random_values = NodeRingSchnorrSignature.__generate_unique_random_values(len(ring_public_keys))

        # Step 3: Calculate partial signatures and hashes for each external public key
        signature_random_points, sub_signatures, product = NodeRingSchnorrSignature.__calculate_partial_signatures(
            message, signature_private_key, ring_public_keys, random_values
        )

        # Step 4: Loop until a valid master random value is found
        signer_r, signer_r_point = NodeRingSchnorrSignature.__generate_signer_randomness(
            product, signature_random_points
        )

        # Step 5: Generate the master signature
        signer_sub_signature = SchnorrSignature.sign(sum_coordinates(signer_r_point), signature_private_key)
        signer_hash = NodeRingSchnorrSignature.__get_hash_for_message_randomness_and_signature(
            message, signer_r_point, signer_sub_signature
        )

        # Step 6: Add all random values to the signature sum
        signature_sum = NodeRingSchnorrSignature.__compute_signature_sum(
            signer_hash, private_key, random_values, signer_r
        )
        # Step 7: Insert the master randomness, signature, and public key at a random position
        NodeRingSchnorrSignature.__append_signer_to_ring(
            private_key, signer_r_point, signer_sub_signature, ring_public_keys, signature_random_points, sub_signatures
        )

        return NodeRingSchnorrSignature(
            signature_public_key, ring_public_keys, signature_random_points, sub_signatures, signature_sum
        )

    def verify(self, message: int) -> bool:
        """
        Verifies a Node Ring Schnorr signature against a given message.

        :param message: The message for which the signature is to be verified.
        :type message: int
        :return: True if the signature is valid for the given message, False otherwise.
        :rtype: bool
        """
        signature_sum = None
        for ring_public_key, sub_signature, r in zip(self.ring_public_keys, self.sub_signatures, self.random_points):
            if not sub_signature.verify(sum_coordinates(r), self.signature_public_key):
                return False

            hash_ = NodeRingSchnorrSignature.__get_hash_for_message_randomness_and_signature(message, r, sub_signature)
            signature_sum = add(signature_sum, add(r, multiply(ring_public_key, hash_)))

        return eq(multiply(G1, self.signature_sum), signature_sum)

    @staticmethod
    def __compute_signature_sum(master_hash: int, private_key: int, random_values: List[int], signer_r: int) -> int:
        """
        Compute the signature sum based on the master hash, private key, random values, and signer's R value.

        :param master_hash: The hash of all relevant data contributing to the signature.
        :param private_key: The private key of the signer.
        :param random_values: A list of random values used in the signature computation.
        :param signer_r: The R value from the signer's ephemeral key pair.
        :return: The computed signature sum as an integer.

        The signature sum is calculated as the sum of the signer's R value, the product of the private key and master
        hash, and all the random values, modulo the curve order.
        """
        initial_sum = signer_r + private_key * master_hash
        return (initial_sum + sum(random_values)) % curve_order

    @staticmethod
    def __generate_signer_randomness(product: Point2D[Field], signature_r: List[Point2D[Field]]):
        while True:
            master_random_value = generate_random_scalar()
            signer_r = add(multiply(G1, master_random_value), product)

            if signer_r is not None and all(signer_r != r for r in signature_r):  # pragma: no cover
                break
        return master_random_value, signer_r

    @staticmethod
    def __append_signer_to_ring(
        master_private_key: int,
        master_randomness: Point2D[Field],
        master_sigma: SchnorrSignature,
        ring_public_keys: List[Point2D[Field]],
        signature_random_points: List[Point2D[Field]],
        sub_signatures: List[SchnorrSignature],
    ):
        index = random.randint(0, len(ring_public_keys))
        signature_random_points.insert(index, master_randomness)
        sub_signatures.insert(index, master_sigma)
        ring_public_keys.insert(index, multiply(G1, master_private_key))

    @staticmethod
    def __generate_signature_keys(message, private_key, ring_public_keys):
        signature_private_key = sol_hash(
            message,
            private_key,
            *[
                coordinate
                for ring_public_key in ring_public_keys
                for coordinate in convert_point_2d_to_list(ring_public_key)
            ]
        )
        signature_public_key = multiply(G1, signature_private_key)
        return signature_private_key, signature_public_key

    @staticmethod
    def __get_hash_for_message_randomness_and_signature(
        message: int, r: Point2D[Field], signature: SchnorrSignature
    ) -> int:
        return (
            sol_hash(message, *convert_point_2d_to_list(r), *convert_point_2d_to_list(signature.r), signature.s)
            % curve_order
        )

    @staticmethod
    def __generate_unique_random_values(number: int) -> List[int]:
        random_values = set()
        while len(random_values) < number:
            random_values.add(generate_random_scalar())
        return list(random_values)

    @staticmethod
    def __calculate_partial_signatures(
        message: int, new_private_key: int, ext_public_keys: List[Point2D[Field]], random_values: List[int]
    ) -> Tuple[List[Point2D[Field]], List[SchnorrSignature], Point2D[Field]]:
        random_points = []
        sub_signatures = []
        ring_sum = None
        for i, ext_public_key in enumerate(ext_public_keys):
            random_points.append(multiply(G1, random_values[i]))
            sub_signature = SchnorrSignature.sign(sum_coordinates(random_points[i]), new_private_key)
            sub_signatures.append(sub_signature)
            hash_ = NodeRingSchnorrSignature.__get_hash_for_message_randomness_and_signature(
                message, random_points[i], sub_signature
            )
            ring_sum = add(ring_sum, multiply(neg(ext_public_key), hash_))
        return random_points, sub_signatures, ring_sum
