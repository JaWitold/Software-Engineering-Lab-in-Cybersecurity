import argparse

from deploy_util_for_tests import (
    TEST_CHAIN_ID,
    TEST_IP,
    TEST_PORT,
    deploy_contract_for_tests,
    get_account_address_and_priv_key,
)

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.node_ring_schnorr_signature import (
    SchnorrSignature,
    convert_point_2d_to_list,
)
from test_contracts import generate_random_nr_signature


def storing_vs_verifying(max_ring_size: int, num_of_trials: int):
    """
    Test performance of storing of signature
    """
    # pylint: disable=R0914
    contract_address = deploy_contract_for_tests().contractAddress
    client = BlockchainClient(TEST_IP, TEST_PORT, TEST_CHAIN_ID, contract_address)
    _, blockchain_priv_key = get_account_address_and_priv_key(0)
    account = client.web3.eth.account.from_key(blockchain_priv_key)
    assert account is not None, "Failed to create account from provided private key."

    print("ring_size,avg_gas_usage_adding,avg_gas_estimate_verifying,avg_block_size[bytes]")
    for curr_ring_size in range(1, max_ring_size + 1):
        sum_gas_usage_adding = 0
        sum_gas_estimate_verifying = 0
        sum_block_sizes = 0
        for _ in range(num_of_trials):
            priv_keys_list, message, signature = generate_random_nr_signature(curr_ring_size)
            for priv_key, pub_key in zip(priv_keys_list, signature.ring_public_keys):
                sigma = SchnorrSignature.sign(convert_point_2d_to_list(pub_key)[0], priv_key)
                client.register(blockchain_priv_key, pub_key, sigma.r, sigma.s)
            receipt_add = client.store_signature(blockchain_priv_key, message, signature)
            sum_gas_usage_adding += receipt_add.gasUsed

            arguments_to_verify = client.convert_nr_sign_sigma_to_sol_arguments(signature)
            gas_estimate = client.contract.functions.testVerifyNodeRingSignature(
                message, *arguments_to_verify
            ).estimate_gas()
            sum_gas_estimate_verifying += gas_estimate

        # after trials with one ring size
        latest_block_number = client.web3.eth.block_number
        start_block_number = latest_block_number - num_of_trials + 1

        for block_number in range(start_block_number, latest_block_number + 1):
            block = client.web3.eth.get_block(block_number)
            sum_block_sizes += block.size

        # Calculate average block size
        avg_block_size = sum_block_sizes / num_of_trials
        avg_gas_usage_adding = sum_gas_usage_adding / num_of_trials
        avg_gas_estimate_verifying = sum_gas_estimate_verifying / num_of_trials

        print(f"{curr_ring_size},{avg_gas_usage_adding},{avg_gas_estimate_verifying},{avg_block_size}", flush=True)


def parse_arguments():
    """
    Function that parses input arguments
    """
    parser = argparse.ArgumentParser(description="Test performance")
    parser.add_argument("--max_ring_size", type=int, required=True, help="Maximum ring size")
    parser.add_argument("--num_of_trials", type=int, required=True, help="Number of trials")
    return parser.parse_args()


def main():
    """
    Main function
    """
    args = parse_arguments()
    max_ring_size = args.max_ring_size
    num_of_trials = args.num_of_trials
    print("Max Ring Size:", max_ring_size)
    print("Number of Trials:", num_of_trials)
    storing_vs_verifying(max_ring_size, num_of_trials)


if __name__ == "__main__":
    main()
