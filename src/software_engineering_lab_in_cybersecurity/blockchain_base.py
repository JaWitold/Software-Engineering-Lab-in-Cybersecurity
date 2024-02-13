from abc import ABC

from web3 import HTTPProvider, Web3


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
