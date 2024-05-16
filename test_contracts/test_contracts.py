import copy
import unittest

import requests
from deploy_util_for_tests import (
    CONTRACT_NAME,
    TEST_CHAIN_ID,
    TEST_IP,
    TEST_PORT,
    deploy_contract_for_tests,
    get_account_address_and_priv_key,
)

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.node_ring_schnorr_signature import (
    G1,
    NodeRingSchnorrSignature,
    SchnorrSignature,
    convert_point_2d_to_list,
    generate_random_scalar,
    multiply,
)


def generate_random_nr_signature(ring_size: int):
    """
    Simulate node ring signature with given number of ring size
    """
    priv_keys_list = [generate_random_scalar() for _ in range(ring_size - 1)]
    pub_keys_list = [multiply(G1, priv_key) for priv_key in priv_keys_list]
    pub_keys_list_copy = copy.deepcopy(pub_keys_list)

    msg = generate_random_scalar()
    priv_key = generate_random_scalar()
    while priv_key in priv_keys_list:
        priv_key = generate_random_scalar()
    signature = NodeRingSchnorrSignature.sign(msg, priv_key, pub_keys_list)

    idx = 0
    while len(pub_keys_list_copy) > idx and pub_keys_list_copy[idx] == signature.ring_public_keys[idx]:
        idx += 1

    priv_keys_list.insert(idx, priv_key)

    return priv_keys_list, msg, signature


class TestContracts(unittest.TestCase):
    """Unit tests for SchnorrSignature contract"""

    @classmethod
    def setUpClass(cls):
        """
        Method to deploy contract before testsuite
        """
        # Perform initialization or setup common to all test cases
        contract_address = deploy_contract_for_tests().contractAddress
        cls.client = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)
        _, cls.blockchain_priv_key = get_account_address_and_priv_key(2)

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

        self.assertTrue(result, f"{CONTRACT_NAME} verification failed")

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

        self.assertFalse(result, f"{CONTRACT_NAME} verification succedded for invalid signature")

    def test_contract_node_ring_schnorr_signature_verification(self):
        """
        Perform NodeRingSchnorr signature verification using the contract.
        """
        ring_size = 10
        _, msg, signature = generate_random_nr_signature(ring_size)
        arguments = self.client.convert_nr_sign_sigma_to_sol_arguments(signature)
        result = self.client.contract.functions.testVerifyNodeRingSignature(msg, *arguments).call()

        self.assertTrue(result, f"{CONTRACT_NAME} verification failed")

    def test_contract_signature_storage(self):
        """
        Store signature on blockchain using the contract.
        """
        # pylint: disable=R0914
        ring_size = 4
        priv_keys_list, msg, signature = generate_random_nr_signature(ring_size)
        prev_block_num = self.client.web3.eth.block_number

        # register keys
        exception = None
        for priv_key, pub_key in zip(priv_keys_list, signature.ring_public_keys):
            try:
                sigma = SchnorrSignature.sign(convert_point_2d_to_list(pub_key)[0], priv_key)
                receipt = self.client.register(self.blockchain_priv_key, pub_key, sigma.r, sigma.s)
            except requests.exceptions.ReadTimeout as e:
                exception = e

        try:
            receipt = self.client.store_signature(self.blockchain_priv_key, msg, signature)
            curr_block_num = receipt.blockNumber
            self.assertGreater(curr_block_num, prev_block_num, "Block wasn't added")
        # get signature
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
