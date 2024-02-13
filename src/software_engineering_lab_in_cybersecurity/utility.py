import argparse
import json
import os
import sys
from logging import DEBUG, INFO, Logger, basicConfig
from typing import Any, Dict, List


def load_accounts(_logger: Logger = None) -> Dict[str, Dict[str, str]]:
    """Load accounts and their private keys from the accounts.json file."""
    try:
        with open("accounts/accounts.json", "r", encoding="UTF-8") as file:
            return json.load(file)
    except FileNotFoundError:
        _logger.error("accounts.json file not found.")
        sys.exit(1)


def select_account_for_transaction(_logger: Logger = None):
    """
    Interactively prompts the user to select a blockchain account for transactions.

    This function displays a list of blockchain accounts loaded from a predefined source (e.g., 'accounts.json') and
    allows the user to select one by entering its index. It validates the user input to ensure a valid account is
    selected. If the index is invalid, it logs an error and terminates the program.

    :return: A tuple containing the selected account's address and its corresponding private key.
    :rtype: Tuple[str, str]
    """
    accounts = load_accounts(_logger)
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
    return account_address, private_key


def parse_args(description: str, args: List[str], config: Dict[str, Any]) -> argparse.Namespace:
    """
    Generic command line parameter parser.

    :param description: Description of the command line tool.
    :type description: str
    :param args: Command line parameters as list of strings.
    :type args: List[str]
    :param config: Configuration for additional arguments, including version and custom arguments.
    :type config: Dict[str, Any]
    :returns: Command line parameters namespace.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--version", action="version", version=config.get("version"))
    parser.add_argument(
        "-v", "--verbose", dest="loglevel", help="Set loglevel to INFO.", action="store_const", const=INFO
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="Set loglevel to DEBUG.",
        action="store_const",
        const=DEBUG,
    )

    # Dynamically add custom arguments based on config
    for arg_name, arg_config in config.get("custom_args", {}).items():
        parser.add_argument(arg_name, **arg_config)

    return parser.parse_args(args)


def setup_logging(loglevel: int | str | None) -> None:
    """
    Setup basic logging.

    :param loglevel: Minimum loglevel for emitting messages.
    :type loglevel: int | str | None
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    basicConfig(level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


connection_config = {
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
}

account_config = {
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
}
