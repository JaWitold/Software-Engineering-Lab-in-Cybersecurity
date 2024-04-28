import time

from deploy_util_for_tests import (
    TEST_CHAIN_ID,
    TEST_IP,
    TEST_PORT,
    deploy_contract_for_tests,
)

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from test_contracts import (
    convert_nr_sign_sigma_to_sol_arguments,
    generate_random_nr_signature,
)

CONTRACT_NAME = "SignatureStorage"


def store_signatures_performance():
    """
    Test performance of storing of signature
    """
    contract_address = deploy_contract_for_tests(CONTRACT_NAME).contractAddress
    client = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)
    time.sleep(10)
    max_num_of_ext_pubkeys = 70
    num_of_trials = 100
    i = 1
    assert i > 0
    print("ring_size,time[s],gas_estimate")
    while i < max_num_of_ext_pubkeys:
        avg_time = 0
        avg_gas_estimate = 0
        for _ in range(num_of_trials):
            msg, signature = generate_random_nr_signature(i)
            assert len(signature.ring_public_keys) == i + 1
            arguments = convert_nr_sign_sigma_to_sol_arguments(signature)
            gas_estimate = client.contract.functions.testVerifyNodeRingSignature(msg, *arguments).estimate_gas()
            avg_gas_estimate += gas_estimate

            start_time = time.time()
            result = client.contract.functions.testVerifyNodeRingSignature(msg, *arguments).call()
            end_time = time.time()
            elapsed_time = end_time - start_time
            avg_time += elapsed_time
            assert result, f"{CONTRACT_NAME} verification failed"

        avg_time /= num_of_trials
        avg_gas_estimate /= num_of_trials
        print(f"{i+1},{avg_time},{avg_gas_estimate}", flush=True)
        i += 1


if __name__ == "__main__":
    store_signatures_performance()
