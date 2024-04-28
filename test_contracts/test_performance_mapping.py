import sys
import time

from deploy_util_for_tests import (
    TEST_CHAIN_ID,
    TEST_IP,
    TEST_PORT,
    deploy_contract_for_tests,
    get_account_address_and_priv_key,
)

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.elliptic_curve import (
    convert_point_2d_to_list,
)
from test_contracts import generate_random_nr_signature


def store_signatures_performance_test(contract_name):
    """
    Test performance of storing of signature
    """
    # pylint: disable=R0914
    # pylint: disable=R0801
    contract_address = deploy_contract_for_tests(contract_name).contractAddress
    client = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)
    _, blockchain_priv_key = get_account_address_and_priv_key(0)
    account = client.web3.eth.account.from_key(blockchain_priv_key)
    assert account is not None, "Failed to create account from provided private key."
    time.sleep(2)

    max_num_of_ext_pubkeys = 70
    num_of_trials = 4
    i = 1
    print("ring_size,preparing_transaction_time[s],wait_receipt_time[s],gas_used,block_size[bytes]")
    while i <= max_num_of_ext_pubkeys:
        avg_wait_receipt_time = 0
        avg_preparing_transaction_time = 0
        avg_gas = 0
        avg_block_size = 0
        for _ in range(num_of_trials):
            message, signature = generate_random_nr_signature(i)
            assert len(signature.ring_public_keys) == i + 1
            # try:
            contract_function = client.contract.functions.addSignature(
                message,
                convert_point_2d_to_list(signature.signature_public_key),
                [convert_point_2d_to_list(rp) for rp in signature.random_points],
                [convert_point_2d_to_list(sub_signature.r) for sub_signature in signature.sub_signatures],
                [sub_signature.s for sub_signature in signature.sub_signatures],
                signature.signature_sum,
                [convert_point_2d_to_list(pk) for pk in signature.ring_public_keys],
            )

            start_time = time.time()
            transaction_hash = client.prepare_transaction(contract_function, account, blockchain_priv_key)
            end_time = time.time()
            avg_preparing_transaction_time += end_time - start_time

            start_time = time.time()
            receipt = client.wait_for_receipt(transaction_hash)
            end_time = time.time()
            avg_wait_receipt_time += end_time - start_time

            avg_gas += receipt.gasUsed
            block_number = receipt.blockNumber
            block = client.web3.eth.get_block(block_number)
            assert block is not None
            avg_block_size += block.size

            avg_preparing_transaction_time /= num_of_trials
            avg_wait_receipt_time /= num_of_trials
            avg_gas /= num_of_trials
            avg_block_size /= num_of_trials
            print(
                f"{i+1},{avg_preparing_transaction_time},{avg_wait_receipt_time}," f"{avg_gas},{avg_block_size}",
                flush=True,
            )

        i += 1


if __name__ == "__main__":
    CONTACT_NAME = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "single":
            CONTACT_NAME = "SignatureStorageSingleMapping"
        elif sys.argv[1] == "nested":
            CONTACT_NAME = "SignatureStorage"

    if CONTACT_NAME is not None:
        store_signatures_performance_test(CONTACT_NAME)
    else:
        print("provide option: <single, nested>")
