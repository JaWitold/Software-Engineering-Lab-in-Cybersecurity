"""
File containing Solidity contracts deployment part.
"""

import json
import logging
import os
from typing import Any, List, Tuple

from py_ecc.typing import Field, Point2D
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

    def __init__(self, ip: str, port: str, chain_id: str, contract_address: str) -> None:
        """
        Initialize the connection to the Ethereum node.

        :param ip: The IP address of the blockchain node.
        :type ip: str
        :param port: The port on which the blockchain node is accessible.
        :type port: str
        :param contract_address: The address of the contract where the signature will be stored.
        :type contract_address: str
        """
        super().__init__(ip, port, chain_id)

        self.contract = self.load_compiled_contract(contract_address)

    def load_compiled_contract(self, contract_address: str) -> Contract:
        """
        Load compiled Solidity contracts.

        This method should be implemented to load compiled contracts, typically from a file or
        a predefined location where compiled contract artifacts are stored.

        :param contract_address: The address of the contract to be loaded.
        :type contract_address: str
        :return: The compiled contract instance.
        :rtype: Contract
        """
        deployed_contracts_file_path = os.path.join(os.getcwd(), "deployment", "deployed_contracts.json")
        with open(deployed_contracts_file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        return self.web3.eth.contract(address=contract_address, abi=data[contract_address]["abi"])

    def store_signature(self, account_private_key: str, message: int, signature: NodeRingSchnorrSignature) -> None:
        """
        Store a signature on the blockchain.

        Given an account's address and private key, and a signature object, this method sends a transaction
        to store the signature on the blockchain.

        :param account_private_key: The private key associated with the account for signing the transaction.
        :type account_private_key: str
        :param message: The message to be signed.
        :type message: int
        :param signature: The signature object to be stored on the blockchain.
        :type signature: NodeRingSchnorrSignature
        """
        account = self.web3.eth.account.from_key(account_private_key)
        assert account is not None, "Failed to create account from provided private key."

        contract_function = self.contract.functions.addSignature(
            message,
            convert_point_2d_to_list(signature.signature_public_key),
            [convert_point_2d_to_list(rp) for rp in signature.random_points],
            [convert_point_2d_to_list(sub_signature.r) for sub_signature in signature.sub_signatures],
            [sub_signature.s for sub_signature in signature.sub_signatures],
            signature.signature_sum,
            [convert_point_2d_to_list(pk) for pk in signature.ring_public_keys],
        )

        transaction_hash = self.prepare_transaction(contract_function, account, account_private_key)
        receipt = self.wait_for_receipt(transaction_hash)

        _logger.info("Block number: %s", receipt.blockNumber)
        _logger.info("Gas used: %s", receipt.gasUsed)
        _logger.debug("Block: %s", self.web3.eth.get_block(receipt.blockNumber))

    def get_signatures_by_new_public_key(self, signature_public_key: Point2D[Field]) -> List[Tuple[Any]]:
        """
        Retrieves signatures associated with a given public key from the blockchain.

        :param signature_public_key: Public key to search for signatures.
        :type signature_public_key: Point2D[Field]
        :return: A list of signatures associated with the public key.
        :rtype: List[Tuple[Any]]
        """
        return self.contract.functions.getSignaturesByNewPublicKey(
            convert_point_2d_to_list(signature_public_key)
        ).call()

    def verify_signature(self, signature: List[Tuple[Any]]) -> bool:
        """
        Verifies a signature stored on the blockchain.

        :param signature: The signature data to verify.
        :type signature: List[Tuple[Any]]
        :return: Boolean indicating whether the signature is valid.
        :rtype: bool
        """
        return self.contract.functions.verifyHierarchicalSignature(*signature).call()
