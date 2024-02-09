"""
CLI interface for deploying smart contracts.
"""

import logging
import sys
from typing import List

from software_engineering_lab_in_cybersecurity import __version__
from software_engineering_lab_in_cybersecurity.common_utils import (
    parse_args,
    setup_logging,
)
from software_engineering_lab_in_cybersecurity.deployment.deploy import deploy_contract

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
            "--contract": {
                "dest": "contract_name",
                "type": str,
                "required": True,
                "help": "Name of the contract to deploy.",
            },
            "--network": {
                "dest": "network",
                "type": str,
                "default": "development",
                "help": "Blockchain network to deploy the contract on.",
            },
        },
    }
    args = parse_args("Deploy smart contracts to blockchain networks.", args, config)
    setup_logging(args.loglevel)
    _logger.debug("Initiating deployment process...")
    deploy_contract(args.contract_name, args.network)
    _logger.info("Deployment process completed.")


def run() -> None:
    """
    Entry point for the deployment CLI script.
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
