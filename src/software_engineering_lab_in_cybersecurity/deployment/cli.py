"""
CLI interface for deploying smart contracts.
"""

import json
import logging
import os
import sys
from typing import List

from dotenv import load_dotenv

from software_engineering_lab_in_cybersecurity import __version__
from software_engineering_lab_in_cybersecurity.common_utils import (
    parse_args,
    setup_logging,
)
from software_engineering_lab_in_cybersecurity.deployment.deploy import ContractDeployer

load_dotenv()

_logger = logging.getLogger(__name__)


def load_accounts() -> dict:
    """Load accounts and their private keys from the accounts.json file."""
    try:
        with open("accounts/accounts.json", "r", encoding="UTF-8") as file:
            return json.load(file)
    except FileNotFoundError:
        _logger.error("accounts.json file not found.")
        sys.exit(1)


def main(args: List[str]) -> None:
    """
    Main function to handle CLI for deployment.

    :param args: A list of command line arguments.
    :type args: List[str]
    """
    config = {
        "version": f"Software-Engineering-Lab-in-Cybersecurity {__version__}",
        "custom_args": {
            "--contract": {
                "dest": "contract_name",
                "type": str,
                "help": "Name of the contract to deploy. Can also be set in .env as CONTRACT_NAME.",
                "default": os.getenv("CONTRACT_NAME"),
            },
            "--ip": {
                "dest": "ip",
                "type": str,
                "help": "IP address for deployment. Can also be set in .env as CONTRACT_IP.",
                "default": os.getenv("CONTRACT_IP"),
            },
            "--port": {
                "dest": "port",
                "type": str,
                "help": "Port number for deployment. Can also be set in .env as CONTRACT_PORT.",
                "default": os.getenv("CONTRACT_PORT", "8545"),
            },
            "--chain-id": {
                "dest": "chain_id",
                "type": str,
                "help": "Chain ID for the deployment network. Can also be set in .env as CHAIN_ID.",
                "default": os.getenv("CHAIN_ID"),
            },
            "--private-key": {
                "dest": "private_key",
                "type": str,
                "help": "Private key for deployment. If not provided, you'll be prompted to select an account.",
                "default": None,
            },
            "--account-address": {
                "dest": "account_address",
                "type": str,
                "help": "The address of a blockchain account. If not provided, you'll be prompted to select one.",
                "default": None,
            },
        },
    }
    args = parse_args("Deploy smart contracts to blockchain networks.", args, config)
    setup_logging(args.loglevel)

    account_address = args.account_address
    private_key = args.private_key
    if not account_address or not private_key:
        accounts = load_accounts()
        print("Please select an account by its index to deploy the contract:")
        addresses = list(accounts["private_keys"].keys())
        for i, address in enumerate(addresses, 1):
            print(f"{[i]} {address}")

        index = int(input("Account Index: ")) - 1
        if index < 0 or index >= len(addresses):
            _logger.error("Invalid account index.")
            sys.exit(1)

        account_address = addresses[index]
        private_key = accounts["private_keys"][account_address]
        print(f"Selected address: {account_address}")

    _logger.debug("Initiating deployment process...")
    deployer = ContractDeployer(account_address, private_key, args.ip, args.port, args.chain_id)
    deployer.deploy_contract(args.contract_name)
    _logger.info("Deployment process completed.")


def run() -> None:
    """
    Entry point for the deployment CLI script.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
