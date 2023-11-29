from web3 import Web3
from deployment.consts import *
import json
from schemas import SchnorrSignature


MY_ADDRESS = "0x25C00757DDD113CbC428c0CDd5Af9755ae7E2811"
PRIVATE_KEY = "0x4c683b0cd99b085dd6fab2d1dfeedbadab99be509bdee52f744a4cdb69993da8"


# For connecting to ganache
w3 = Web3(Web3.HTTPProvider(GANACHE_URL))

# input("provide contract address: ")
contractAddress = "0xd08E39251Dfaf0D1b3Ac8E02632d5919A0877C87"

with open(ABI_FILENAME) as f:
    contract_abi = json.load(f)

# Working with deployed Contracts
nonce = w3.eth.get_transaction_count(MY_ADDRESS)

simple_storage = w3.eth.contract(address=contractAddress, abi=contract_abi)

ss = SchnorrSignature()
PRIVKEY = 19977808579986318922850133509558564821349392755821541651519240729619349670944
MESSAGE = 123
PUBKEY, signature = ss.sign(PRIVKEY, MESSAGE)

x_, s = signature

result = simple_storage.functions.verify(
    bn128Point_to_list(PUBKEY),
    MESSAGE,
    bn128Point_to_list(x_),
    s
).call()

print(f"{'ACCEPTED' if result == 1 else 'REJECTED'}")
# ).build_transaction(
#     {
#         "chainId": CHAIN_ID,
#         "gasPrice": w3.eth.gas_price,
#         "from": MY_ADDRESS,
#         "nonce": nonce,
#     }
# )


# signed_txn = w3.eth.account.sign_transaction(
#     greeting_transaction, private_key=PRIVATE_KEY
# )
# tx_greeting_hash = w3.eth.send_raw_transaction(
#     signed_txn.rawTransaction)
# print("Updating stored Value...")
# tx_receipt = w3.eth.wait_for_transaction_receipt(tx_greeting_hash)
