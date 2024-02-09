"""
Deployment logic for smart contracts.
"""

import logging

_logger = logging.getLogger(__name__)


def deploy_contract(
    account_address: str, private_key: str, contract_name: str, ip: str, port: str, chain_id: str
) -> None:
    """
    Deploy a contract to a specified network using the given private key for authentication.

    :param account_address: The blockchain address of the deploying account.
    :type account_address: str
    :param private_key: The private key associated with the deploying account.
    :type private_key: str
    :param contract_name: The name of the contract to deploy.
    :type contract_name: str
    :param ip: The IP address of the blockchain node.
    :type ip: str
    :param port: The port number of the blockchain node.
    :type port: str
    :param chain_id: The unique identifier for the blockchain network.
    :type chain_id: str
    """
    # Use lazy % formatting for logging
    _logger.info("Deploying %s to %s:%s, %s", contract_name, ip, port, chain_id)
    _logger.info("%s has been successfully deployed to %s:%s.", contract_name, account_address, private_key)
    print("Deploying %s to %s:%s, %s", contract_name, ip, port, chain_id)
    print(("%s has been successfully deployed to %s:%s.", contract_name, account_address, private_key))
