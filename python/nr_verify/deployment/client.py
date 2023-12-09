"""
Client to connect to blockchain
"""
import json
from web3 import Web3
from nr_verify.deployment.consts import GANACHE_URL, ABI_FILENAME
from nr_verify.schemas.schnorr_signature import SchnorrSignature
from nr_verify.schemas.util import bn128_point_to_list

MY_ADDRESS = "0x25C00757DDD113CbC428c0CDd5Af9755ae7E2811"
PRIVATE_KEY = "0x4c683b0cd99b085dd6fab2d1dfeedbadab99be509bdee52f744a4cdb69993da8"


def run_client():
    """
    Connect to Ganache blockchain and call transaction function
    """
    # For connecting to ganache
    w3_instance = Web3(Web3.HTTPProvider(GANACHE_URL))

    # input("provide contract address: ")
    contract_address = "0xd08E39251Dfaf0D1b3Ac8E02632d5919A0877C87"

    with open(ABI_FILENAME, encoding='utf-8') as file:
        contract_abi = json.load(file)

    # Working with deployed Contracts

    simple_storage = w3_instance.eth.contract(address=contract_address, abi=contract_abi)

    privkey = 19977808579986318922850133509558564821349392755821541651519240729619349670944
    message = 123
    pubkey, signature = SchnorrSignature.sign(privkey, message)

    public_ephemeral_val, small_s = signature

    result = simple_storage.functions.verify(
        bn128_point_to_list(pubkey),
        message,
        bn128_point_to_list(public_ephemeral_val),
        small_s
    ).call()

    print(f"{'ACCEPTED' if result == 1 else 'REJECTED'}")
    # ).build_transaction(
    #     {
    #         "chainId": CHAIN_ID,
    #         "gasPrice": w3_instance.eth.gas_price,
    #         "from": MY_ADDRESS,
    #         "nonce": nonce,
    #     }
    # )


    # signed_txn = w3_instance.eth.account.sign_transaction(
    #     greeting_transaction, private_key=PRIVATE_KEY
    # )
    # tx_greeting_hash = w3_instance.eth.send_raw_transaction(
    #     signed_txn.rawTransaction)
    # print("Updating stored Value...")
    # tx_receipt = w3_instance.eth.wait_for_transaction_receipt(tx_greeting_hash)
