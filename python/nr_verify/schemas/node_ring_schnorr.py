"""
Module: node_ring_schnorr
This module provides implementation for NodeRingSchnorr signature algorithm.
"""

import random

from py_ecc.bn128 import multiply, add, G1, neg, eq

from .schnorr_signature import SchnorrSignature
from .util import keccak256, encode_packed, randsn, addmodn, curve_order


class NodeRingSchnorr:
    """
    Implements a variant of the Schnorr signature scheme for a ring of nodes.
    """
    GEN_ORDER = 0x30644E72E131A029B85045B68181585D2833E84879B9709143E1F593F0000001

    @staticmethod
    def _generate_random_values(count):
        random_values = []
        while len(random_values) < count:
            value = randsn()
            if value not in random_values:
                random_values.append(value)
        return random_values

    @staticmethod
    def _calculate_partial_signatures(new_private_key, message, ext_public_keys, random_values):
        ephemeral_randomness = []
        sigmas = []
        product = None
        for i, ext_public_key in enumerate(ext_public_keys):
            ephemeral_randomness.append(multiply(G1, random_values[i]))
            _, sigma = SchnorrSignature.sign(
                new_private_key,
                int(ephemeral_randomness[i][0]) + int(ephemeral_randomness[i][1])
            )
            sigmas.append(sigma)
            hash_input = encode_packed(
                message,
                ephemeral_randomness[i][0],
                ephemeral_randomness[i][1],
                sigma[0][0],
                sigma[0][1],
                sigma[1]
            )
            hash_ = int.from_bytes(keccak256(hash_input), byteorder="big") % curve_order
            product = add(product, multiply(neg(ext_public_key), hash_))
        return ephemeral_randomness, sigmas, product

    def nr_sign(self, private_key: int, message: int, ext_public_keys):
        # pylint: disable=R0914
        """
        Generates a signature using a variant of the Schnorr signature scheme.

        :param private_key: The private key of the signer.
        :param message: The message to be signed.
        :param ext_public_keys: A list of external public keys, each represented as a pair of integers
            (elliptic curve points).
        :return: A tuple consisting of:
                 - new_public_key: The newly generated public key.
                 - ephemeral_randomness: A list of ephemeral randomness values, one for each external public key, plus
                    one additional value.
                 - sigmas: A list of sigmas (partial signatures), one for each value in ephemeral_randomness.
                 - master_sum: The sum of the master random value and the product of the signer's private key and the
                    master hash, incremented by the sum of all random values.
                 - ext_public_keys: An updated list of external public keys with the signer's public key inserted
                    at a random position.
        """
        # Step 1: Generate an ephemeral key pair
        new_private_key = int.from_bytes(
            keccak256(
                encode_packed(
                    message,
                    private_key,
                    *[y[0] for y in ext_public_keys],
                    *[y[1] for y in ext_public_keys]
                )
            ), byteorder="big"
        ) % self.GEN_ORDER
        new_public_key = multiply(G1, new_private_key)

        # Step 2: Generate a list of unique random values
        random_values = self._generate_random_values(len(ext_public_keys))

        # Step 3: Calculate partial signatures and hashes for each external public key
        ephemeral_randomness, sigmas, product = self._calculate_partial_signatures(
            new_private_key,
            message,
            ext_public_keys,
            random_values
        )

        # Step 4: Loop until a valid master random value is found
        while True:
            master_random_value = randsn()
            master_randomness = add(multiply(G1, master_random_value), product)

            if master_randomness is not None and all(master_randomness != r for r in ephemeral_randomness):
                break

        # Step 5: Generate the master signature
        _, master_sigma = SchnorrSignature.sign(
            new_private_key,
            int(master_randomness[0]) + int(master_randomness[1])
        )
        master_hash = int.from_bytes(
            keccak256(
                encode_packed(
                    message,
                    master_randomness[0],
                    master_randomness[1],
                    master_sigma[0][0],
                    master_sigma[0][1],
                    master_sigma[1]
                )
            ), byteorder="big"
        ) % self.GEN_ORDER
        master_sum = (master_random_value + private_key * master_hash) % curve_order

        # Step 6: Add all random values to the master sum
        for random_value in random_values:
            master_sum = addmodn(master_sum, random_value)

        # Step 7: Insert the master randomness, signature, and public key at a random position
        index = random.randint(0, len(ext_public_keys))
        ephemeral_randomness.insert(index, master_randomness)
        sigmas.insert(index, master_sigma)
        ext_public_keys.insert(index, multiply(G1, private_key))

        return (
            new_public_key,
            ephemeral_randomness,
            sigmas,
            master_sum,
            ext_public_keys
        )

    def nr_verify(self, message: int, signature):
        """
        Verifies NodeRingSchnorr signature of the message.
        :param message: The message to be verified.
        :param signature:  A tuple consisting of:
                 - new_public_key: The newly generated public key.
                 - ephemeral_randomness: A list of ephemeral randomness values, one for each external public key,
                    plus one additional value.
                 - sigmas: A list of sigmas (partial signatures), one for each value in ephemeral_randomness.
                 - master_sum: The sum of the master random value and the product of the signer's private key and the
                    master hash, incremented by the sum of all random values.
                 - ext_public_keys: An updated list of external public keys with the signer's public key inserted
                    at a random position.
        :return: bool
        """
        new_public_key, ephemeral_randomness, sigmas, master_sum, ext_public_keys = signature

        sum_ = None
        prod = True
        for i, ext_public_key in enumerate(ext_public_keys):
            prod = prod and SchnorrSignature.verify(new_public_key,
                                                    int(ephemeral_randomness[i][0]) + int(ephemeral_randomness[i][1]),
                                                    sigmas[i]
                                                    )
            hash_ = int.from_bytes(keccak256(encode_packed(
                message,
                ephemeral_randomness[i][0],
                ephemeral_randomness[i][1],
                sigmas[i][0][0],
                sigmas[i][0][1],
                sigmas[i][1]
            )), byteorder="big") % self.GEN_ORDER
            sum_ = add(sum_, add(ephemeral_randomness[i], multiply(ext_public_key, hash_)))
        return prod and eq(multiply(G1, master_sum), sum_)
