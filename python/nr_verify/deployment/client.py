"""
Client to connect to blockchain
"""

import os
import pickle

from dotenv import load_dotenv
from web3 import Web3

from nr_verify.schemas.schnorr_signature import SchnorrSignature
from nr_verify.schemas.node_ring_schnorr import NodeRingSchnorr
from nr_verify.schemas.util import bn128_point_to_list, randsn
from py_ecc.bn128 import multiply, G1


def initialize_web3_instance(uri: str):
    """
    Initialize Web3 instance with HTTPProvider.
    """
    return Web3(Web3.HTTPProvider(uri))


def load_compiled_contracts(filename='contracts.bin'):
    """
    Load compiled contracts from a binary file.
    """
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_file_dir, filename), 'rb') as file:
        return pickle.load(file)


def get_contract_instance(w3_instance, contract_address, contract_abi):
    """
    Get the contract instance.
    """
    return w3_instance.eth.contract(address=contract_address, abi=contract_abi)


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


def _convert_nr_sign_sigma_to_sol(msg, signature):
    """
    Returns solidity compatibile values to insert to contract
    uint256 message,
    uint256[2] memory newPublicKey, // G1
    uint256[2][] memory ephemeralRandomness, // list of G1
    uint256[2][] memory xsigmas, // list of sigmas X's
    uint256[] memory ssigmas, // list of sigmas S's
    uint256 masterSum, // Fr
    uint256[2][] memory publicKeys // list of G1
    """
    _new_public_key, _ephemeral_randomness, _sigmas, \
        master_sum, _ext_public_keys = signature
    sol_new_public_key = bn128_point_to_list(_new_public_key)
    sol_ephemeral_randomness = [bn128_point_to_list(
        eph) for eph in _ephemeral_randomness]
    sol_xsigmas = [bn128_point_to_list(sigma[0]) for sigma in _sigmas]
    sol_ssigmas = [sigma[1] for sigma in _sigmas]
    sol_ext_public_keys = [bn128_point_to_list(
        pubkey) for pubkey in _ext_public_keys]

    return msg, sol_new_public_key, sol_ephemeral_randomness, sol_xsigmas, \
        sol_ssigmas, master_sum, sol_ext_public_keys


def _gen_nr_signature():
    """
    Generates random signature and returns arguments for solidity
    """
    pub_keys = [multiply(G1, randsn()) for _ in range(10)]
    priv_key = randsn()
    msg = 3123231342432
    node_ring_schnorr = NodeRingSchnorr()
    signature = node_ring_schnorr.nr_sign(priv_key, msg, pub_keys)
    arguments = _convert_nr_sign_sigma_to_sol(msg, signature)
    return arguments


def store_signature(w3_instance, contract):
    """
    Test contract for storing signatures
    """
    private_key = input('PRIVATE_KEY: ')
    account = w3_instance.eth.account.from_key(private_key)
    nonce = w3_instance.eth.get_transaction_count(account.address)

    arguments = _gen_nr_signature()
    public_key_in_sig = arguments[-1][0]

    transaction = contract.functions.storeSignature(
        *arguments
    ).build_transaction({
        'from': account.address,
        # 'gas': 1000000,  # adjust gas limit as needed
        'gasPrice': w3_instance.eth.gas_price,
        'nonce': nonce,
    })
    # Sign the transaction
    signed_tx = w3_instance.eth.account.sign_transaction(
        transaction, private_key)

    # Send the transaction
    tx_hash = w3_instance.eth.send_raw_transaction(signed_tx.rawTransaction)
    w3_instance.eth.wait_for_transaction_receipt(tx_hash)

    num_of_signatures = contract.functions.getSignatureCount().call()
    assert num_of_signatures > 0

    signature_details = contract.functions.getSignatureDetails(
        num_of_signatures-1).call()
    print(f"{signature_details=}")

    signature_details = contract.functions.getSignaturesForPublicKey(
        public_key_in_sig).call()
    print(f"{signature_details=}")


def run_client():
    """
    Connect to Ganache blockchain and call transaction function.
    """
    load_dotenv()
    w3_instance = Web3(Web3.HTTPProvider(
        f"http://{os.getenv('IP')}:{os.getenv('PORT')}"))
    compiled_contracts = load_compiled_contracts()

    contract_address = input("Provide contract address: ")
    contract_abi = compiled_contracts['SignaturesStorage']['abi']

    storage_contract = get_contract_instance(
        w3_instance, contract_address, contract_abi)
    store_signature(w3_instance, storage_contract)
