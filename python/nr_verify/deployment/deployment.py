"""
File contaninig solidity contracts deployment part
"""
import sys
import os
import pickle

from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from web3 import Web3


def read_file_content(file_name):
    """
    Read and return the content of a file.
    """
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()


def deploy_contract():
    # pylint: disable=R0914
    """
    Function to deploy contract
    """
    # Load environment variables
    load_dotenv()
    # Get the list of contract paths and Solidity version from the .env file
    contract_dir = os.getenv('CONTRACT_DIR')
    contract_filenames = os.getenv('CONTRACT_NAMES').split(',')
    contract_names = [os.path.basename(contract_filename).split('.')[0]
                      for contract_filename in contract_filenames]
    solidity_version = os.getenv('SOLIDITY_VERSION')

    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(current_file_dir)
    if os.path.exists(contract_dir):
        os.chdir(os.getenv('CONTRACT_DIR'))
    else:
        print("Error reading dir")
        sys.exit(1)

    # Install and set the Solidity compiler version
    install_solc(solidity_version)
    # Compile the Solidity code
    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {
            contract_name: {
                "content": read_file_content(contract_filename)
            } for contract_name, contract_filename in
            zip(contract_names, contract_filenames)
        },
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["metadata", "evm.bytecode", "evm.bytecode.sourceMap", "abi"]
                }
            }
        }
    }, solc_version=solidity_version)

    compiled_contracts = {
        contract_name: {
            'bytecode': compiled_sol['contracts'][contract_name][contract_name]
            ['evm']['bytecode']['object'],
            'abi': compiled_sol['contracts'][contract_name][contract_name]['abi']
        }
        for contract_name in contract_names
    }
    os.chdir(os.path.dirname(__file__))
    with open('contracts.bin', 'wb') as file:
        file.write(pickle.dumps(compiled_contracts))

    # Connect to an Ethereum node
    web3 = Web3(Web3.HTTPProvider(
        f"HTTP://{os.getenv('IP')}:{os.getenv('PORT')}"))
    # Check connection
    assert web3.is_connected(), "Web3 is not connected to Ethereum node."

    # Remove file deployment.txt if it exists
    if os.path.exists("deployment.txt"):
        os.remove("deployment.txt")

    # Deploy each compiled contract
    schnorr_sig_nr_addr = None

    for contract_name in compiled_contracts.keys():

        contract = web3.eth.contract(
            abi=compiled_contracts[contract_name]['abi'],
            bytecode=compiled_contracts[contract_name]['bytecode']
        )

        # Load account from private key
        private_key = os.getenv('PRIVATE_KEY')
        account = web3.eth.account.from_key(private_key)

        # Set up transaction
        nonce = web3.eth.get_transaction_count(account.address)
        constructor_arg = None
        if contract_name == "SignaturesStorage" and schnorr_sig_nr_addr is not None:
            constructor_arg = schnorr_sig_nr_addr

        transaction = contract.constructor(constructor_arg).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'chainId': int(os.getenv('CHAIN_ID')),
            'gasPrice': web3.eth.gas_price
        })

        # Sign the transaction
        signed_txn = web3.eth.account.sign_transaction(
            transaction, private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        if contract_name == "SchnorrSignatureNodeRing":
            schnorr_sig_nr_addr = tx_receipt.contractAddress

        # Output the address of the deployed contract
        print(
            f"Contract {contract_name} deployed at address: {tx_receipt.contractAddress}")

        with open("deployment.txt", "a", encoding="UTF-8") as file:
            file.write(f"{contract_name}: {tx_receipt.contractAddress}\n")
