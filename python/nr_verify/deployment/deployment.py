import os
import pickle

from dotenv import load_dotenv
from solcx import compile_standard, install_solc
from web3 import Web3


def read_file_content(file_name):
    """ Read and return the content of a file. """
    with open(file_name, 'r', encoding='utf-8') as file:
        return file.read()


if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    # Get the list of contract paths and Solidity version from the .env file
    contract_dir = os.getenv('CONTRACT_DIR')
    contract_names = os.getenv('CONTRACT_NAMES').split(',')
    solidity_version = os.getenv('SOLIDITY_VERSION')

    if os.path.exists(contract_dir):
        os.chdir(os.getenv('CONTRACT_DIR'))

    # Install and set the Solidity compiler version
    install_solc(solidity_version)
    # Compile the Solidity code
    compiled_sol = compile_standard({
        "language": "Solidity",
        "sources": {
            os.path.basename(contract_name).split('.')[0]: {
                "content": read_file_content(contract_name)
            } for contract_name in contract_names
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
            'bytecode': compiled_sol['contracts'][contract_name][contract_name]['evm']['bytecode']['object'],
            'abi': compiled_sol['contracts'][contract_name][contract_name]['abi']
        }
        for contract_filename in contract_names
        for contract_name in [os.path.basename(contract_filename).split('.')[0]]
    }
    os.chdir(os.path.dirname(__file__))
    with open('contracts.bin', 'wb') as f:
        f.write(pickle.dumps(compiled_contracts))

    # Connect to an Ethereum node
    web3 = Web3(Web3.HTTPProvider(f"HTTP://{os.getenv('IP')}:{os.getenv('PORT')}"))
    # Check connection
    assert web3.is_connected(), "Web3 is not connected to Ethereum node."

    # Remove file deployment.txt if it exists
    if os.path.exists("deployment.txt"):
        os.remove("deployment.txt")

    # Deploy each compiled contract
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
        transaction = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': nonce,
            'chainId': int(os.getenv('CHAIN_ID')),
            'gasPrice': web3.eth.gas_price
        })

        # Sign the transaction
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key)

        # Send the transaction
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Output the address of the deployed contract
        print(f"Contract {contract_name} deployed at address: {tx_receipt.contractAddress}")

        with open("deployment.txt", "a", encoding="UTF-8") as f:
            f.write(f"{contract_name}: {tx_receipt.contractAddress}\n")
