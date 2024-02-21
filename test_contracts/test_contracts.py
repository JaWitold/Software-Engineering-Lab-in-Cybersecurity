import unittest

import requests
from deploy_util_for_tests import (
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

CONTRACT_NAME = "HierarchicalVerification"


def convert_nr_sign_sigma_to_sol_arguments(signature: NodeRingSchnorrSignature):
    """
    Converts python data struct to such that solidity contract will handle

    :param signature: node ring signature as python structure
    "type signature: NodeRingSchnorrSignature
    """
    # pylint: disable=R0801
    return (
        convert_point_2d_to_list(signature.signature_public_key),
        [convert_point_2d_to_list(rp) for rp in signature.random_points],
        [convert_point_2d_to_list(sub_signature.r) for sub_signature in signature.sub_signatures],
        [sub_signature.s for sub_signature in signature.sub_signatures],
        signature.signature_sum,
        [convert_point_2d_to_list(pk) for pk in signature.ring_public_keys],
    )


def generate_random_nr_signature(num_of_pub_keys: int):
    """
    Simulate node ring signature with given number of public keys

    :param num_of_pub_keys:
    "type num_of_pub_keys: int
    """
    priv_keys_list = [generate_random_scalar() for _ in range(num_of_pub_keys)]
    pub_keys = [multiply(G1, priv_key) for priv_key in priv_keys_list]
    priv_key = generate_random_scalar()
    while priv_key in priv_keys_list:
        priv_key = generate_random_scalar()
    msg = 3123231342432
    return msg, NodeRingSchnorrSignature.sign(msg, priv_key, pub_keys)


class TestContracts(unittest.TestCase):
    """Unit tests for SchnorrSignature contract"""

    @classmethod
    def setUpClass(cls):
        """
        Method to deploy contract before testsuite
        """
        # Perform initialization or setup common to all test cases
        contract_address = deploy_contract_for_tests(CONTRACT_NAME).contractAddress
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

        result = self.client.contract.functions.verifySignature(
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

        result = self.client.contract.functions.verifySignature(
            message, convert_point_2d_to_list(pubkey), convert_point_2d_to_list(signature.r), signature.s
        ).call()

        self.assertFalse(result, f"{CONTRACT_NAME} verification succedded for invalid signature")

    def test_contract_node_ring_schnorr_signature_verification(self):
        """
        Perform NodeRingSchnorr signature verification using the contract.
        """
        num_of_pub_keys = 10
        msg, signature = generate_random_nr_signature(num_of_pub_keys)
        arguments = convert_nr_sign_sigma_to_sol_arguments(signature)
        result = self.client.contract.functions.verifyNodeRingSignature(msg, *arguments).call()

        self.assertTrue(result, f"{CONTRACT_NAME} verification failed")

    def test_contract_signature_storage(self):
        """
        Store signature on blockchain using the contract.
        """
        msg, signature = generate_random_nr_signature(3)
        prev_block_num = self.client.web3.eth.block_number
        # store signature
        exception = None
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

        hier_verify_result = self.client.verify_signature(signatures_list[0])
        self.assertTrue(hier_verify_result, "Hier verify failed")
