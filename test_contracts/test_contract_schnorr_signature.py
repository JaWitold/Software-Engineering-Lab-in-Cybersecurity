import unittest

from deploy_util_for_tests import (
    TEST_CHAIN_ID,
    TEST_IP,
    TEST_PORT,
    deploy_contract_for_tests,
)

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.schnorr_signature import (
    G1,
    SchnorrSignature,
    convert_point_2d_to_list,
    multiply,
)

CONTRACT_NAME = "SchnorrSignature"


class TestContractSchnorrSignature(unittest.TestCase):
    """Unit tests for SchnorrSignature contract"""

    @classmethod
    def setUpClass(cls):
        """
        Method to deploy contract before testsuite
        """
        # Perform initialization or setup common to all test cases
        contract_address = deploy_contract_for_tests(CONTRACT_NAME).contractAddress
        cls.client = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)

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
