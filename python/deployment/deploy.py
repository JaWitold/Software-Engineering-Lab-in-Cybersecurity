import json

from web3 import Web3


from solcx import compile_standard, install_solc
from dotenv import load_dotenv
from consts import *
import os

MY_ADDRESS = "0x2BC1db4F7c62477831Ab2463E08EAEd9A1752210"
PRIVATE_KEY = "0xf1e71b826f508bdbd7d58ea081f8c9edbdfb1ad5b34480f8175a2b1ac2bbcf64"


load_dotenv()


with open(SOL_CONTRACT_FILE_PATH, "r") as file:
    sol_contract_file = file.read()

with open(SOL_ELIPTIC_CURVE_FILE_PATH, "r") as file:
    sol_elliptic_curves_file = file.read()

print("Installing...")
install_solc(SOL_VER)


# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {SOL_CONTRACT_FILENAME: {"content": sol_contract_file},
                    SOL_ELIPTIC_CURVE_FILENAME: {"content": sol_elliptic_curves_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version=SOL_VER,
)


# get bytecode
bytecode = compiled_sol["contracts"][SOL_CONTRACT_FILENAME][SOL_CONTRACT_NAME]["evm"][
    "bytecode"
]["object"]

# get abi
abi = json.loads(
    compiled_sol["contracts"][SOL_CONTRACT_FILENAME][SOL_CONTRACT_NAME]["metadata"]
)["output"]["abi"]


with open(ABI_FILENAME, "w") as file:
    json.dump(abi, file)


# For connecting to ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))


# Create the contract in Python
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest transaction
nonce = w3.eth.get_transaction_count(MY_ADDRESS)
# Submit the transaction that deploys the contract
transaction = Contract.constructor().build_transaction(
    {
        "chainId": CHAIN_ID,
        "gasPrice": w3.eth.gas_price,
        "from": MY_ADDRESS,
        "nonce": nonce,
    }
)
print(w3.eth.gas_price)
# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(
    transaction, private_key=PRIVATE_KEY)
print("Deploying Contract!")
# Send it!
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Wait for the transaction to be mined, and get the transaction receipt
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")
print("Paste this address to client")
