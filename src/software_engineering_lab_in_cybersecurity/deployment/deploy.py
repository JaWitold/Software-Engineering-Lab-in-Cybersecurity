"""
Deployment logic for smart contracts.
"""

import logging

_logger = logging.getLogger(__name__)


def deploy_contract(contract_name: str, network: str) -> None:
    """
    Deploy a contract to a specified network.

    :param contract_name: The name of the contract to deploy.
    :type contract_name: str
    :param network: The network to deploy the contract on.
    :type network: str
    """
    # Use lazy % formatting for logging
    _logger.info("Deploying %s to %s...", contract_name, network)
    # Insert deployment logic here
    _logger.info("%s has been successfully deployed to %s.", contract_name, network)
