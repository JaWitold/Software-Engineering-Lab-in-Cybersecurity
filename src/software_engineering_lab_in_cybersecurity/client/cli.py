"""
CLI interface for operating blockchain.
"""

import logging
import os
import sys
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from py_ecc.bn128 import G1, multiply
from py_ecc.fields import bn128_FQ
from py_ecc.typing import Field, Point2D

from software_engineering_lab_in_cybersecurity import __version__
from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.node_ring_schnorr_signature import (
    NodeRingSchnorrSignature,
)
from software_engineering_lab_in_cybersecurity.utility import (
    account_config,
    connection_config,
    load_accounts,
    parse_args,
    select_account_for_transaction,
    setup_logging,
)

load_dotenv()

_logger = logging.getLogger(__name__)


def get_input_with_prompt(prompt_message: str, default: str = None) -> str:
    """
    Get user input with a prompt message, returning a default value if the input is empty.

    :param prompt_message: The message to display to the user.
    :type prompt_message: str
    :param default: The default value to return if no input is given.
    :type default: str, optional
    :return: The user input or the default value.
    :rtype: str
    """
    user_input = input(f"{prompt_message}: ").strip()
    return user_input if user_input else default


def select_private_key(accounts: Dict[str, str], logger: logging.Logger) -> str:
    """
    Interactively select or provide a private key for signing the message. Supports direct input of custom private keys.

    :param accounts: A dictionary of account addresses to their respective private keys.
    :type accounts: Dict[str, str]
    :param logger: The logger instance for logging error messages.
    :type logger: logging.Logger
    :return: The selected or provided private key.
    :rtype: str
    """
    print("Select an account for the private key:")
    for i, (address, _) in enumerate(accounts.items(), start=1):
        print(f"[{i}] {address}")

    custom_prefix = "custom:"
    selection = get_input_with_prompt(
        "Enter account number or provide a private key directly (prefix with 'custom:' for custom keys (hex))"
    )

    if selection.startswith(custom_prefix):
        # If the selection starts with 'custom:', strip the prefix and return the rest as the private key
        return selection[len(custom_prefix) :].strip()
    if selection.isdigit() and 1 <= int(selection) <= len(accounts):
        # If the selection is a digit within the range of account numbers, select the corresponding private key
        selected_index = int(selection) - 1
        return list(accounts.keys())[selected_index]
    # If the selection does not match any of the above conditions, log an error and request input again
    logger.error(
        "Invalid selection. Please enter a valid account number or a custom private key prefixed with 'custom:'."
    )
    return select_private_key(accounts, logger)


def select_public_keys_ring(accounts: Dict[str, str], exclude_address: str) -> List[Point2D[Field]]:
    """
    Interactively select public keys for the ring, excluding the signer's own key, or input custom public keys.

    :param accounts: A dictionary of account addresses to their respective public keys.
    :type accounts: Dict[str, str]
    :param exclude_address: The address of the signer to exclude from the selection.
    :type exclude_address: str
    :return: A list of selected public keys for the ring.
    :rtype: List[Point2D[Field]]
    """
    available_addresses = [addr for addr in accounts.keys() if addr != exclude_address]
    selected_public_keys = []

    print(
        "Select public keys for the ring (excluding the signer). Enter 'done' to finish, or input custom keys as 'x,y':"
    )
    while True:
        for i, addr in enumerate(available_addresses, start=1):
            print(f"[{i}] {addr} (Public Key: {multiply(G1, int(accounts[addr], 16))}")
        choice = get_input_with_prompt("Select a public key by number, enter 'done', or input custom key as 'x,y'")

        if choice.lower() == "done":
            break
        if choice.isdigit() and 1 <= int(choice) <= len(available_addresses):
            selected_index = int(choice) - 1
            selected_address = available_addresses.pop(selected_index)
            selected_public_keys.append(multiply(G1, int(accounts[selected_address], 16)))
            print(selected_public_keys)
        if "," in choice:
            try:
                x, y = map(int, choice.split(","))
                pk = (bn128_FQ(x), bn128_FQ(y))
                if pk not in selected_public_keys and pk != multiply(G1, int(accounts[exclude_address], 16)):
                    selected_public_keys.append(pk)
                else:
                    _logger.warning("Public key has been already added to the ring")
            except ValueError:
                print("Invalid custom key format. Please input as 'x,y' where x and y are integers.")
        else:
            print("Invalid selection. Please try again.")

    return selected_public_keys


def select_signature(signatures):
    """
    Allows the user to select a signature from a list for verification purposes.

    :param signatures: A list of available signatures for selection.
    :type signatures: List[str]
    :return: The selected signature.
    :rtype: str
    """
    print("Select signature to verify:")
    while True:
        for i, signature in enumerate(signatures, start=1):
            print(f"[{i}] {signature}")
        choice = get_input_with_prompt("Select a signature by index number:")

        if choice.isdigit() and 1 <= int(choice) <= len(signatures):
            return signatures[int(choice) - 1]
        print("Invalid selection. Please try again.")


def select_public_key() -> Tuple[bn128_FQ, bn128_FQ]:
    """
    Prompts the user to input a public key in a specific format for signature verification.

    :return: A tuple representing the public key.
    :rtype: Tuple[Field, Field]
    """
    print("Select public key, input key as 'x,y':")
    while True:
        input_key = get_input_with_prompt("Select public key, input key as 'x,y':")
        if "," in input_key:
            try:
                x_str, y_str = input_key.split(",")
                return bn128_FQ(int(x_str)), bn128_FQ(int(y_str))
            except ValueError:
                print("Invalid custom key format. Please input as 'x,y' where x and y are integers.")
        else:
            print("Invalid selection. Please try again.")


def main(args: List[str]) -> None:
    """
    Handle CLI for NodeRingSchnorrSignature operations.

    :param args: Command line arguments.
    :type args: List[str]
    """
    config = {
        "version": f"Software-Engineering-Lab-in-Cybersecurity {__version__}",
        "custom_args": {
            **connection_config,
            "--verify": {
                "dest": "verify",
                "action": "store_true",
                "help": "Flag to initiate hierarchical signature verification.",
            },
            "--signature-public-key": {
                "dest": "signature_public_key",
                "type": str,
                "help": "Public key of the signature. If not provided, you'll be prompted to provide one.",
                "default": None,
            },
            "--sign": {
                "dest": "sign",
                "action": "store_true",
                "help": "Flag to initiate creating signature.",
            },
            "--message": {
                "dest": "message",
                "type": str,
                "help": "Message to be signed. If not provided, you'll be prompted provide one.",
                "default": None,
            },
            "--message-private-key": {
                "dest": "message_private_key",
                "type": str,
                "help": "Private key for signature. If not provided, you'll be prompted to select one.",
                "default": None,
            },
            "--contract-address": {
                "dest": "contract_address",
                "type": str,
                "help": "Address of contract. ",
                "default": os.getenv("CONTRACT_ADDRESS"),
            },
            **account_config,
        },
    }
    args = parse_args("NodeRingSchnorrSignature operations.", args, config)
    setup_logging(args.loglevel)

    if args.sign:
        accounts = load_accounts(_logger)["private_keys"]
        message = int(args.message or get_input_with_prompt("Enter the message to sign"))
        message_private_key = int(args.message_private_key or select_private_key(accounts, _logger), 16)
        account_address, account_private_key = args.account_address, args.private_key
        if not account_address or not account_private_key:
            account_address, account_private_key = select_account_for_transaction(_logger)

        public_keys_ring = select_public_keys_ring(accounts, account_address)
        signature = NodeRingSchnorrSignature.sign(message, message_private_key, public_keys_ring)

        client = BlockchainClient(args.ip, args.port, args.chain_id, args.contract_address)
        client.store_signature(account_private_key, message, signature)

        _logger.info("Signature public key: %s", signature.signature_public_key)
    elif args.verify:
        # ask for signature public key (x, y)
        signature_public_key = (
            tuple(map(bn128_FQ, map(int, args.signature_public_key.split(","))))[0:2]
            if args.signature_public_key and "," in args.signature_public_key
            else select_public_key()
        )

        if len(signature_public_key) != 2:
            _logger.error("Invalid public key provided: %s, expected (x, y)", args.signature_public_key)
            sys.exit(1)

        client = BlockchainClient(args.ip, args.port, args.chain_id, args.contract_address)
        signatures = client.get_signatures_by_new_public_key(signature_public_key)
        print(type(signatures[0][0]), signatures)
        if len(signatures) == 0:
            _logger.error("No signatures found for %s", args.signature_public_key)
            sys.exit(1)

        signature = signatures[0] if len(signatures) == 1 else select_signature(signatures)

        print("Verification result: %s", client.verify_signature(signature))
    else:
        _logger.error("No operation specified. Use --sign <message> to sign or --verify to verify.")
        sys.exit(1)


def run() -> None:
    """
    Entry point for the NodeRingSchnorrSignature CLI script.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
