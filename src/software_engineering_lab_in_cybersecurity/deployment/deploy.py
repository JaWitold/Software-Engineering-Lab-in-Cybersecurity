"""
File containing Solidity contracts deployment part.
"""

import json
import logging
import os
import re
import sys
from typing import List, Tuple

from eth_account.signers.local import LocalAccount
from hexbytes import HexBytes
from solcx import compile_standard, install_solc
from web3.contract import Contract
from web3.types import TxReceipt

from software_engineering_lab_in_cybersecurity.blockchain_base import BlockchainBase

_logger = logging.getLogger(__name__)


class ContractDeployer(BlockchainBase):
    """
    A class responsible for deploying Solidity contracts to an Ethereum blockchain network.

    This class handles the entire process of deploying a contract, including reading the contract source code,
    compiling it using the specified Solidity version, preparing and sending the transaction, and finally,
    saving the compiled contract's information and deployment address.
    """

    solidity_version = "0.8.18"

    def __init__(self, account_address: str, private_key: str, ip: str, port: str, chain_id: str) -> None:
        """
        Deploy a contract to a specified network using the given private key for authentication.

        :param account_address: The blockchain address of the deploying account.
        :type account_address: str
        :param private_key: The private key associated with the deploying account.
        :type private_key: str
        :param ip: The IP address of the blockchain node.
        :type ip: str
        :param port: The port number of the blockchain node.
        :type port: str
        :param chain_id: The unique identifier for the blockchain network.
        :type chain_id: str
        """
        super().__init__(ip, port, chain_id)

        self.account_address = account_address
        self.private_key = private_key

        self.account = self.web3.eth.account.from_key(self.private_key)
        assert self.account is not None, "Failed to create account from provided private key."

    def deploy_contract(self, contract_name: str) -> TxReceipt:
        """
        Deploys the specified Solidity contract to the blockchain.

        :param contract_name: The name of the contract to deploy.
        :type contract_name: str
        """
        solidity_code = self._read_contract(contract_name)
        compiled_contract = self.compile_contract(solidity_code)
        transaction_hash = self.prepare_transaction(compiled_contract)
        receipt = self.wait_for_receipt(transaction_hash)
        self.save_compiled_contract(contract_name, receipt, compiled_contract)

        _logger.info("Deployed contract")
        return receipt

    @staticmethod
    def _read_contract(contract_name: str) -> List[Tuple[str, str, str]]:
        """
        Reads the Solidity contract file containing the specified contract name from the 'contracts' directory.

        :param contract_name: The name of the Solidity contract to read.
        :type contract_name: str
        :param contracts: A list of tuples containing contract name, content, and filename for each contract.
        :type contracts: List[Tuple[str, str, str]]
        :return: The content of the Solidity contract file.
        :rtype: List[Tuple[str, str, str]]
        :raises FileNotFoundError: If no contract matching the specified name is found.
        """
        contract = None

        contracts_dir = os.path.join(os.getcwd(), "contracts")

        prefix = r"contract\s+"
        pattern = r"(\s*{|\s+is\s+\w+)"
        contract_name_esc_regex = re.escape(contract_name)
        compiled_regex = re.compile(prefix + contract_name_esc_regex + pattern)

        for filename in os.listdir(contracts_dir):
            if filename.endswith(".sol"):
                with open(os.path.join(contracts_dir, filename), "r", encoding="utf-8") as file:
                    content = file.read()
                    if compiled_regex.search(content):
                        contract = (contract_name, content, filename)
                        break
        if not contract:
            _logger.error(
                "No contract named %s was found in the 'contracts' directory.",
                contract_name,
            )
            sys.exit(1)
        return contract

    def compile_contract(self, code: Tuple[str, str, str]) -> Contract:
        """
        Compiles the specified Solidity contract along with its dependencies.

        :param code: A list of tuples containing contract name, content, and filename for each contract and dependency.
        :type code: List[Tuple[str, str, str]]
        :return: A Web3 contract object for the compiled main contract.
        :rtype: Contract
        """
        install_solc(self.solidity_version)

        c_name, content, f_name = code

        compiled_sol = compile_standard(
            {
                "language": "Solidity",
                "sources": {f_name: {"content": content}},
                "settings": {
                    "outputSelection": {
                        "*": {
                            "*": [
                                "metadata",
                                "evm.bytecode",
                                "evm.bytecode.sourceMap",
                                "abi",
                            ]
                        }
                    }
                },
            },
            solc_version=self.solidity_version,
            base_path=os.path.join(os.getcwd(), "contracts"),
        )

        metadata = compiled_sol["contracts"][f_name][c_name]

        return self.web3.eth.contract(abi=metadata["abi"], bytecode=metadata["evm"]["bytecode"]["object"])

    def prepare_transaction(
        self, contract: Contract, account: LocalAccount = None, private_key: str = None
    ) -> HexBytes:
        """
        Prepares a transaction for sending to the specified contract.

        This method extends the functionality of the parent class's `prepare_transaction` method, allowing for optional
        specification of an account and a private key. If not provided, the method uses instance attributes as defaults.

        :param contract: The contract instance to which the transaction will be sent.
        :type contract: Contract
        :param account: The account from which the transaction is made. Defaults to `self.account` if not provided.
        :type account: LocalAccount, optional
        :param private_key: The private key for signing the transaction. Defaults to `self.private_key` if not provided.
        :type private_key: str, optional
        :return: A `HexBytes` object representing the prepared transaction's hash.
        :rtype: HexBytes
        """
        return super().prepare_transaction(
            contract.constructor(), account or self.account, private_key or self.private_key
        )

    @staticmethod
    def save_compiled_contract(contract_name: str, receipt: TxReceipt, compiled_contract: Contract) -> None:
        """
        Saves the compiled contract's information and deployment address to a JSON file.

        :param contract_name: The name of compiled contract.
        :type contract_name: str
        :param receipt: The transaction receipt containing the deployment address.
        :type receipt: TxReceipt
        :param compiled_contract: The compiled contract instance.
        :type compiled_contract: Contract
        """
        base_directory = os.path.join(os.getcwd(), "deployment")
        deployed_contracts_file_path = os.path.join(base_directory, "deployed_contracts.json")
        os.makedirs(base_directory, exist_ok=True)

        contract_data = {
            "name": contract_name,
            "abi": compiled_contract.abi,
            "bytecode": compiled_contract.bytecode.hex(),
        }

        if os.path.exists(deployed_contracts_file_path):
            with open(deployed_contracts_file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    data = {}
        else:
            data = {}

        data[receipt.contractAddress] = contract_data

        with open(deployed_contracts_file_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, sort_keys=True)

        _logger.info(
            "Contract %s deployed and saved at %s",
            contract_name,
            receipt.contractAddress,
        )
