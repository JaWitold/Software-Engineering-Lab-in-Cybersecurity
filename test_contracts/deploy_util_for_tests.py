import os
import socket
import subprocess

from software_engineering_lab_in_cybersecurity.deployment.deploy import ContractDeployer
from software_engineering_lab_in_cybersecurity.utility import load_accounts

TEST_IP = os.getenv("CONTRACT_IP", "127.0.0.1")
TEST_PORT = os.getenv("CONTRACT_PORT", "8545")
TEST_CHAIN_ID = os.getenv("CHAIN_ID", "1337")
TEST_CONTAINER_NAME = os.getenv("CONTAINER_NAME", "ganache-container")


def _check_docker_container_exists(container_name):
    try:
        # Run the "docker inspect" command to get information about the container
        subprocess.run(
            ["docker", "inspect", container_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return True
    except subprocess.CalledProcessError:
        # If the container does not exist, Docker inspect will return a non-zero exit code
        return False


def _chek_connection(host, port):
    try:
        # Create a socket object
        with socket.create_connection((host, port), timeout=1):
            return True
    except (socket.timeout, ConnectionRefusedError):
        return False


def deploy_contract_for_tests(contract_name: str):
    """
    Util function to deploy contract that should be tested

    :param contract_name: contract name that would be deployed
    "type contract_name: str
    """
    deployed_contracts_file_path = os.path.join(os.getcwd(), "deployment", "deployed_contracts.json")
    with open(deployed_contracts_file_path, "w", encoding="utf-8"):
        pass

    account_idx = 0
    assert _check_docker_container_exists(TEST_CONTAINER_NAME), f"Docker Ganache not launched {TEST_CONTAINER_NAME=}"
    assert _chek_connection(TEST_IP, TEST_PORT), f"Docker connection error {TEST_IP=}"
    accounts = load_accounts(None)
    addresses = list(accounts["private_keys"].keys())
    assert len(addresses) > 0, "Account addresses not loaded"
    account_address = addresses[account_idx]
    private_key = accounts["private_keys"][account_address]
    deployer = ContractDeployer(account_address, private_key, TEST_IP, TEST_PORT, TEST_CHAIN_ID)
    return deployer.deploy_contract(contract_name)
