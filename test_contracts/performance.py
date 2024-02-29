import time

from deploy_util_for_tests import (
    TEST_CHAIN_ID,
    TEST_IP,
    TEST_PORT,
    deploy_contract_for_tests,
    get_account_address_and_priv_key,
)

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from test_contracts import CONTRACT_NAME, generate_random_nr_signature


def store_signatures_performance():
    """
    Test performance of storing of signature
    """
    contract_address = deploy_contract_for_tests(CONTRACT_NAME).contractAddress
    client = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)
    _, blockchain_priv_key = get_account_address_and_priv_key(0)
    time.sleep(10)
    max_num_of_ext_pubkeys = 40
    num_of_trials = 100
    i = 1
    print("idx,time[s],gas")
    while i < max_num_of_ext_pubkeys:
        avg_time = 0
        avg_gas = 0
        for _ in range(num_of_trials):
            msg, signature = generate_random_nr_signature(i)
            assert len(signature.ring_public_keys) == i + 1
            start_time = time.time()
            # try:
            receipt = client.store_signature(blockchain_priv_key, msg, signature)
            # get signature
            # except requests.exceptions.ReadTimeout as e:
            #     break
            end_time = time.time()
            elapsed_time = end_time - start_time
            avg_time += elapsed_time
            avg_gas += receipt.gasUsed

        avg_time /= num_of_trials
        avg_gas /= num_of_trials
        print(f"{i},{avg_time},{avg_gas}", flush=True)
        i += 1


if __name__ == "__main__":
    store_signatures_performance()
