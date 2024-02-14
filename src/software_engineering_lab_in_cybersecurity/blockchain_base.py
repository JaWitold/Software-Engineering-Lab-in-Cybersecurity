from abc import ABC
from typing import Union

from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from web3 import HTTPProvider, Web3
from web3.contract import ContractConstructor
from web3.contract.contract import ContractFunction
from web3.types import TxReceipt


class BlockchainBase(ABC):
    """
    An abstract base class for interacting with an Ethereum blockchain node.
    """

    def __init__(self, ip: str, port: str, chain_id: str):
        """
        Initialize the connection to the Ethereum node.

        :param ip: The IP address of the blockchain node.
        :type ip: str
        :param port: The port on which the blockchain node is accessible.
        :type port: str
        """
        self.ip = ip
        self.port = port
        self.chain_id = chain_id

        self.web3 = Web3(HTTPProvider(f"HTTP://{self.ip}:{self.port}"))
        assert self.web3.is_connected(), "Failed to connect to Ethereum node."

    def prepare_transaction(
        self, contract: Union[ContractFunction, ContractConstructor], account: LocalAccount, private_key: str
    ) -> HexBytes:
        """
        Prepares the transaction for deploying the contract.

        :param contract: The Web3 contract object to deploy.
        :type contract: ContractFunction | ContractConstructor
        :param account: The Web3 account.
        :type account: LocalAccount
        :param private_key: The private key for account
        :type private_key: str
        :return: The hash of the sent transaction.
        """
        transaction = contract.build_transaction(
            {
                "from": account.address,
                "nonce": self.web3.eth.get_transaction_count(account.address),
                "chainId": int(self.chain_id),
                "gasPrice": self.web3.eth.gas_price,
            }
        )
        signature = self.web3.eth.account.sign_transaction(transaction, private_key)
        return self.web3.eth.send_raw_transaction(signature.rawTransaction)

    def wait_for_receipt(self, transaction_hash: HexBytes) -> TxReceipt:
        """
        Waits for the transaction to be mined and returns the transaction receipt.

        :param transaction_hash: The hash of the transaction to wait for.
        :type transaction_hash: HexBytes
        :return: The transaction receipt.
        """
        return self.web3.eth.wait_for_transaction_receipt(transaction_hash)
