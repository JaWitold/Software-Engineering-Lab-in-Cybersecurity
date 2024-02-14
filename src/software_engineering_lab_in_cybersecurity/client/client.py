"""
Provides functionality for interacting with an Ethereum blockchain, focusing on deploying contracts and
storing NodeRingSchnorrSignature signatures.
"""

import json
import logging
import os

from web3.contract import Contract

from software_engineering_lab_in_cybersecurity.blockchain_base import BlockchainBase
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.elliptic_curve import (
    convert_point_2d_to_list,
)
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.node_ring_schnorr_signature import (
    NodeRingSchnorrSignature,
)

_logger = logging.getLogger(__name__)


class BlockchainClient(BlockchainBase):
    """
    A client for interacting with an Ethereum blockchain node.

    This client is designed to connect to a blockchain node via Web3.py, enabling operations such as
    loading compiled contracts and storing signatures on the blockchain.
    """

    def load_compiled_contract(self, contract_address: str) -> Contract:
        """
        Retrieves a compiled contract by its address for interaction.

        :param contract_address: Ethereum address of the compiled contract.
        :type contract_address: str
        :return: A Web3 Contract instance for the specified contract.
        :rtype: Contract
        """
        deployed_contracts_file_path = os.path.join(os.getcwd(), "deployment", "deployed_contracts.json")
        with open(deployed_contracts_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return self.web3.eth.contract(address=contract_address, abi=data[contract_address]["abi"])

    def store_signature(
        self, contract_address: str, account_private_key: str, message: int, signature: NodeRingSchnorrSignature
    ):
        """
        Stores a NodeRingSchnorrSignature signature in the blockchain.

        :param contract_address: Address of the contract to store the signature.
        :type contract_address: str
        :param account_private_key: Private key of the account for transaction signing.
        :type account_private_key: str
        :param message: Message that was signed, represented as an integer.
        :type message: int
        :param signature: Signature instance to store on the blockchain.
        :type signature: NodeRingSchnorrSignature
        """

        account = self.web3.eth.account.from_key(account_private_key)
        assert account is not None, "Failed to create account from provided private key."

        contract = self.load_compiled_contract(contract_address)

        cc = contract.functions.addSignature(
            message,
            convert_point_2d_to_list(signature.signature_public_key),
            [convert_point_2d_to_list(rp) for rp in signature.random_points],
            [convert_point_2d_to_list(sub_signature.r) for sub_signature in signature.sub_signatures],
            [sub_signature.s for sub_signature in signature.sub_signatures],
            signature.signature_sum,
            [convert_point_2d_to_list(pk) for pk in signature.ring_public_keys],
        )

        transaction_hash = self.prepare_transaction(cc, account, account_private_key)
        receipt = self.wait_for_receipt(transaction_hash)

        _logger.info("Block number: %s", receipt.blockNumber)
        _logger.info("Gas used: %s", receipt.gasUsed)
        _logger.debug("Block: %s", self.web3.eth.get_block(receipt.blockNumber))
