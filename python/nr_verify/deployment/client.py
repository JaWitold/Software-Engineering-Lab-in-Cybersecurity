"""
Client to connect to blockchain
"""

import os
import pickle

from dotenv import load_dotenv
from web3 import Web3

from python.nr_verify.schemas.schnorr_signature import SchnorrSignature
from python.nr_verify.schemas.util import bn128_point_to_list


def initialize_web3_instance(uri: str):
    """
    Initialize Web3 instance with HTTPProvider.
    """
    return Web3(Web3.HTTPProvider(uri))


def load_compiled_contracts(filename='contracts.bin'):
    """
    Load compiled contracts from a binary file.
    """
    with open(filename, 'rb') as file:
        return pickle.load(file)


def get_contract_instance(w3, contract_address, contract_abi):
    """
    Get the contract instance.
    """
    return w3.eth.contract(address=contract_address, abi=contract_abi)


def perform_signature_verification(contract):
    """
    Perform Schnorr signature verification using the contract.
    """
    privkey = 19977808579986318922850133509558564821349392755821541651519240729619349670944
    message = 123
    pubkey, signature = SchnorrSignature.sign(privkey, message)

    public_ephemeral_val, small_s = signature

    return contract.functions.verify(
        bn128_point_to_list(pubkey),
        message,
        bn128_point_to_list(public_ephemeral_val),
        small_s
    ).call()


def run_client():
    """
    Connect to Ganache blockchain and call transaction function.
    """
    load_dotenv()
    w3_instance = Web3(Web3.HTTPProvider(f"http://{os.getenv('IP')}:{os.getenv('PORT')}"))
    compiled_contracts = load_compiled_contracts()

    contract_address = input("Provide contract address: ")
    schnorr_contract = w3_instance.eth.contract(
        address=contract_address,
        abi=compiled_contracts['SchnorrSignature']['abi']
    )
    result = perform_signature_verification(schnorr_contract)

    print(f"{'ACCEPTED' if result == 1 else 'REJECTED'}")


if __name__ == '__main__':
    run_client()
