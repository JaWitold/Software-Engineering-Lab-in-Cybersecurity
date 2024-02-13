"""
File containing Solidity contracts deployment part.
"""

import logging

from software_engineering_lab_in_cybersecurity.blockchain_base import BlockchainBase
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

    def load_compiled_contracts(self) -> dict:
        """
        Load compiled Solidity contracts.

        This method should be implemented to load compiled contracts, typically from a file or
        a predefined location where compiled contract artifacts are stored.

        :return: A mapping of contract names to their compiled artifacts.
        :rtype: dict
        """

    def store_signature(self, account_address: str, account_private_key: str, signature: NodeRingSchnorrSignature):
        """
        Store a signature on the blockchain.

        Given an account's address and private key, and a signature object, this method sends a transaction
        to store the signature on the blockchain.

        :param account_address: The blockchain address of the account.
        :type account_address: str
        :param account_private_key: The private key associated with the account for signing the transaction.
        :type account_private_key: str
        :param signature: The signature object to be stored on the blockchain.
        :type signature: dict
        """
