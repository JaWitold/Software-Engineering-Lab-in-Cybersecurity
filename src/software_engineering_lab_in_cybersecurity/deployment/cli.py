"""
CLI interface for deploying smart contracts.
"""

import logging
import os
import sys
from typing import List

from dotenv import load_dotenv

from software_engineering_lab_in_cybersecurity import __version__
from software_engineering_lab_in_cybersecurity.deployment.deploy import ContractDeployer
from software_engineering_lab_in_cybersecurity.utility import (
    account_config,
    connection_config,
    parse_args,
    select_account_for_transaction,
    setup_logging,
)

load_dotenv()

_logger = logging.getLogger(__name__)


def main(args: List[str]) -> None:
    """
    Main function to handle CLI for deployment.

    :param args: A list of command line arguments.
    :type args: List[str]
    """
    config = {
        "version": f"Software-Engineering-Lab-in-Cybersecurity {__version__}",
        "custom_args": {
            **connection_config,
            "--contract": {
                "dest": "contract_name",
                "type": str,
                "help": "Name of the contract to deploy. Can also be set in .env as CONTRACT_NAME.",
                "default": os.getenv("CONTRACT_NAME"),
            },
            **account_config,
        },
    }
    args = parse_args("Deploy smart contracts to blockchain networks.", args, config)
    setup_logging(args.loglevel)

    account_address = args.account_address
    private_key = args.private_key
    if not account_address or not private_key:
        account_address, private_key = select_account_for_transaction(_logger)

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
