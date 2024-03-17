import time

from deploy_util_for_tests import (
    TEST_CHAIN_ID,
    TEST_IP,
    TEST_PORT,
    deploy_contract_for_tests,
    get_account_address_and_priv_key,
)

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from test_contracts import generate_random_nr_signature


def store_signatures_maps_comparison():
    """
    Test performance of storing of signature
    """
    # pylint: disable=R0914
    contract_address = deploy_contract_for_tests("SignatureStorageSingleMapping").contractAddress
    client_single_map = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)
    _, blockchain_priv_key = get_account_address_and_priv_key(0)
    time.sleep(2)

    contract_address = deploy_contract_for_tests("SignatureStorage").contractAddress
    client_nested_map = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)
    _, blockchain_priv_key = get_account_address_and_priv_key(0)
    time.sleep(2)

    clients = [client_single_map, client_nested_map]

    max_num_of_ext_pubkeys = 70
    num_of_trials = 100
    i = 1
    assert i > 0
    print("num_of_ext_keys,single_time[s],single_gas,nested_time[s],nested_gas")
    while i <= max_num_of_ext_pubkeys:
        avg_time = [0 for _ in clients]
        avg_gas = [0 for _ in clients]
        for _ in range(num_of_trials):
            msg, signature = generate_random_nr_signature(i)
            assert len(signature.ring_public_keys) == i + 1
            # try:
            for client_idx, client in enumerate(clients):
                start_time = time.time()
                receipt = client.store_signature(blockchain_priv_key, msg, signature)
                end_time = time.time()
                elapsed_time = end_time - start_time
                avg_time[client_idx] += elapsed_time
                avg_gas[client_idx] += receipt.gasUsed

            # get signature
            # except requests.exceptions.ReadTimeout as e:
            #     break
        for idx, val in enumerate(avg_time):
            avg_time[idx] = val / num_of_trials
        for idx, val in enumerate(avg_gas):
            avg_gas[idx] = val / num_of_trials

        print(f"{i},{avg_time[0]},{avg_gas[0]},{avg_time[1]},{avg_gas[1]}", flush=True)
        i += 1


if __name__ == "__main__":
    store_signatures_maps_comparison()
