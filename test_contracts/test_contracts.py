import unittest

import requests
from deploy_util_for_tests import deploy_contract_and_get_account

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.node_ring_schnorr_signature import (
    G1,
    NodeRingSchnorrSignature,
    SchnorrSignature,
    convert_point_2d_to_list,
    generate_random_scalar,
    multiply,
)


def _gen_rand_keys(num_of_keys: int):
    priv_keys_list = [generate_random_scalar() for _ in range(num_of_keys)]
    pub_keys_list = [multiply(G1, priv_key) for priv_key in priv_keys_list]
    return priv_keys_list, pub_keys_list


def generate_and_register_keys(blockchain_priv_key: str, client: BlockchainClient, num_of_keys: int):
    """
    Generate random private keys and their corresponding public keys, and register them on the blockchain.

    This function generates a specified number of random private keys. For each private key, it computes
    the corresponding public key and registers both keys on the blockchain using the provided client.

    :param blockchain_priv_key: The private key of the blockchain account used for registration.
    :type blockchain_priv_key: str

    :param client: An instance of BlockchainClient that provides methods to interact with the blockchain.
    :type client: BlockchainClient

    :param num_of_keys: The number of private/public key pairs to generate and register.
    :type num_of_keys: int

    :returns: None
    """
    priv_keys_list, pub_keys_list = _gen_rand_keys(num_of_keys)
    for priv_key, pub_key in zip(priv_keys_list, pub_keys_list):
        sigma = SchnorrSignature.sign(convert_point_2d_to_list(pub_key)[0], priv_key)
        client.register(blockchain_priv_key, pub_key, sigma.r, sigma.s)
    return priv_keys_list, pub_keys_list


class TestContracts(unittest.TestCase):
    """Unit tests for SchnorrSignature contract"""

    @classmethod
    def setUpClass(cls):
        """
        Method to deploy contract before testsuite
        """
        # Perform initialization or setup common to all test cases
        cls.client, cls.blockchain_priv_key = deploy_contract_and_get_account()

    def test_contract_schnorr_signature_verification(self):
        """
        Perform Schnorr signature verification using the contract.
        """
        privkey = 19977808579986318922850133509558564821349392755821541651519240729619349670944
        pubkey = multiply(G1, privkey)
        message = 123
        signature = SchnorrSignature.sign(message, privkey)
        result = self.client.contract.functions.testVerifySchnorrSignature(
            message, convert_point_2d_to_list(pubkey), convert_point_2d_to_list(signature.r), signature.s
        ).call()
        self.assertTrue(result, "verification failed")

    def test_contract_schnorr_signature_verification_failed(self):
        """
        Perform failed Schnorr signature verification using the contract.
        """
        privkey = 19977808579986318922850133509558564821349392755821541651519240729619349670944
        pubkey = multiply(G1, privkey)
        message = 123
        signature = SchnorrSignature.sign(message, privkey)
        signature.s += signature.s // 2
        result = self.client.contract.functions.testVerifySchnorrSignature(
            message, convert_point_2d_to_list(pubkey), convert_point_2d_to_list(signature.r), signature.s
        ).call()
        self.assertFalse(result, "verification succedded for invalid signature")

    def test_contract_node_ring_schnorr_signature_verification(self):
        """
        Perform NodeRingSchnorr signature verification using the contract.
        """
        ring_size = 10
        priv_keys_list, pub_keys_keys_list = _gen_rand_keys(ring_size)
        signing_priv_key, _ = priv_keys_list.pop(), pub_keys_keys_list.pop()
        message = generate_random_scalar()
        signature = NodeRingSchnorrSignature.sign(message, signing_priv_key, pub_keys_keys_list)
        arguments = self.client.convert_nr_sign_sigma_to_sol_arguments(signature)
        result = self.client.contract.functions.testVerifyNodeRingSignature(message, *arguments).call()
        self.assertTrue(result, "verification failed")

    def test_contract_signature_storage(self):
        """
        Store signature on blockchain using the contract.
        """
        ring_size = 10
        priv_keys_list, pub_keys_keys_list = generate_and_register_keys(
            self.blockchain_priv_key, self.client, ring_size
        )
        signing_priv_key, _ = priv_keys_list.pop(), pub_keys_keys_list.pop()
        message = generate_random_scalar()
        signature = NodeRingSchnorrSignature.sign(message, signing_priv_key, pub_keys_keys_list)
        prev_block_num = self.client.web3.eth.block_number

        exception = None
        try:
            receipt = self.client.store_signature(self.blockchain_priv_key, message, signature)
            curr_block_num = receipt.blockNumber
            self.assertGreater(curr_block_num, prev_block_num, "Block wasn't added")
        except requests.exceptions.ReadTimeout as e:
            exception = e

        self.assertIsNone(exception, f"Timeout error: {exception}")
        signatures_list = self.client.get_signatures_by_new_public_key(signature.signature_public_key)
        print(signatures_list)
        self.assertTrue(signatures_list is not None and len(signatures_list) > 0, "Signatures list empty")

        signature_by_idx = self.client.get_signatures_by_idx(0)
        print(signature_by_idx)
        self.assertTrue(signature_by_idx is not None)

        hier_verify_result = self.client.verify_signature(signatures_list[0])
        self.assertTrue(hier_verify_result, "Hier verify failed")
