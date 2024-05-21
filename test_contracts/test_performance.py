import argparse
import os
import random
import sys
import time
from enum import Enum
from itertools import product

from deploy_util_for_tests import deploy_contract_and_get_account

from software_engineering_lab_in_cybersecurity.client.client import BlockchainClient
from software_engineering_lab_in_cybersecurity.node_ring_schnorr_signature.node_ring_schnorr_signature import (
    NodeRingSchnorrSignature,
    generate_random_scalar,
)
from test_contracts import generate_and_register_keys


class Tee:
    """
    A class to enable writing to multiple file-like objects simultaneously.

    :param files: The file-like objects to write to.
    :type files: list[file]
    """

    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        """
        Write the given object to all file-like objects.

        :param obj: The object to write.
        :type obj: str
        """
        for f in self.files:
            f.write(obj)
            f.flush()

    def flush(self):
        """
        Flush all file-like objects.
        """
        for f in self.files:
            f.flush()


class TestType(Enum):
    """
    Enumeration for different types of tests.
    """

    SINGLE = 0
    PATH = 1
    EQUIVALENT = 2


class Attribute(Enum):
    """
    Enumeration for different attributes being tested.
    """

    ADDING_GAS = 0
    VERIFYING_GAS = 1
    BLOCK_SIZE = 2
    SIGNING_TIME = 3

    def label_str(self):
        """
        Function that is used for plots' labels
        """
        attributes_strs = {
            Attribute.ADDING_GAS: "Gas usage for adding signature",
            Attribute.VERIFYING_GAS: "Gas usage for verifying signature",
            Attribute.BLOCK_SIZE: "Block size [bytes]",
            Attribute.SIGNING_TIME: "Duration [s] of signature creation",
        }
        return attributes_strs.get(self, "Unknown attribute")


def _chunked(iterable, size):
    """
    Yield successive chunks of a given size from an iterable.

    :param iterable: The iterable to chunk.
    :type iterable: iterable
    :param size: The size of each chunk.
    :type size: int

    :yield: Chunks of the specified size from the iterable.
    :rtype: generator
    """
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def storing_vs_verifying(max_ring_size: int, num_of_trials: int):
    # pylint: disable=R0914
    """
    Test the performance of storing and verifying signatures on the blockchain.

    :param max_ring_size: The maximum ring size for the test.
    :type max_ring_size: int

    :param num_of_trials: The number of trials to run for each ring size.
    :type num_of_trials: int
    """
    client, blockchain_priv_key = deploy_contract_and_get_account()
    results = [0 for _ in range(len(Attribute))]
    header = "RING_SIZE,"
    header += ",".join(f"{attribute.name}" for attribute in Attribute)
    print(header)

    for curr_ring_size in range(1, max_ring_size + 1):
        for _ in range(num_of_trials):
            # python generation part
            priv_keys_list, pub_keys_keys_list = generate_and_register_keys(blockchain_priv_key, client, curr_ring_size)
            signing_priv_key, _ = priv_keys_list.pop(), pub_keys_keys_list.pop()
            message = generate_random_scalar()
            signature = NodeRingSchnorrSignature.sign(message, signing_priv_key, pub_keys_keys_list)

            # action on blockchain
            receipt_add = client.store_signature(blockchain_priv_key, message, signature)
            results[Attribute.ADDING_GAS.value] += receipt_add.gasUsed
            arguments_to_verify = client.convert_nr_sign_sigma_to_sol_arguments(signature)
            gas_estimate = client.contract.functions.testVerifyNodeRingSignature(
                message, *arguments_to_verify
            ).estimate_gas()
            results[Attribute.VERIFYING_GAS.value] += gas_estimate

        latest_block_number = client.web3.eth.block_number
        start_block_number = latest_block_number - num_of_trials + 1
        for block_number in range(start_block_number, latest_block_number + 1):
            block = client.web3.eth.get_block(block_number)
            results[Attribute.BLOCK_SIZE.value] += block.size

        results = [element / num_of_trials for element in results]
        row_to_print = f"{curr_ring_size},"
        row_to_print += ",".join(str(results[attribute.value]) for attribute in Attribute)
        print(row_to_print, flush=True)


def full_tree_test(
    ring_size: int,
    height_of_tree: int,
    num_of_initial_pub_keys: int,
    blockchain_priv_key: str,
    client: BlockchainClient,
):
    # pylint: disable=R0914
    """
    Test the performance of creating a full tree of signatures.

    :param ring_size: The ring size for each level of the tree.
    :type ring_size: int

    :param height_of_tree: The height of the tree (excluding the root node).
    :type height_of_tree: int

    :param num_of_initial_pub_keys: The number of initial public keys.
    :type num_of_initial_pub_keys: int

    :param blockchain_priv_key: The private key of the blockchain account.
    :type blockchain_priv_key: str

    :param client: An instance of BlockchainClient for interacting with the blockchain.
    :type client: BlockchainClient

    :returns: A list of results for different test types and attributes.
    :rtype: list[list[float]]
    """
    num_of_all_nodes = num_of_initial_pub_keys - 1
    results = [[0 for _ in range(len(Attribute))] for _ in range(len(TestType))]
    all_priv_keys_list, all_pub_keys_list = generate_and_register_keys(
        blockchain_priv_key, client, num_of_initial_pub_keys
    )
    priv_keys_list, pub_keys_keys_list = all_priv_keys_list, all_pub_keys_list

    for lvl in range(height_of_tree, 0, -1):
        priv_keys_list_for_next_lvl, pub_keys_list_for_next_lvl = [], []
        is_first_chunk = True
        for priv_keys_chunk, pub_keys_chunk in zip(
            _chunked(priv_keys_list, ring_size), _chunked(pub_keys_keys_list, ring_size)
        ):
            idx_to_use = 0 if is_first_chunk else random.randint(0, len(priv_keys_chunk) - 1)
            signing_priv_key, _ = priv_keys_chunk.pop(idx_to_use), pub_keys_chunk.pop(idx_to_use)
            message = generate_random_scalar()
            start_time = time.time()
            signature = NodeRingSchnorrSignature.sign(message, signing_priv_key, pub_keys_chunk)
            end_time = time.time()
            elapsed_time = end_time - start_time
            priv_keys_list_for_next_lvl.append(signing_priv_key)
            pub_keys_list_for_next_lvl.append(signature.signature_public_key)

            # action on blockchain
            receipt_add = client.store_signature(blockchain_priv_key, message, signature)
            arguments_to_verify = client.convert_nr_sign_sigma_to_sol_arguments(signature)
            gas_estimate = client.contract.functions.testVerifyNodeRingSignature(
                message, *arguments_to_verify
            ).estimate_gas()

            # single
            results[TestType.SINGLE.value][Attribute.SIGNING_TIME.value] += elapsed_time
            results[TestType.SINGLE.value][Attribute.ADDING_GAS.value] += receipt_add.gasUsed
            results[TestType.SINGLE.value][Attribute.VERIFYING_GAS.value] += gas_estimate

            # path
            if is_first_chunk:
                block_number = client.web3.eth.block_number
                block = client.web3.eth.get_block(block_number)
                results[TestType.PATH.value][Attribute.BLOCK_SIZE.value] += block.size
                results[TestType.PATH.value][Attribute.SIGNING_TIME.value] += elapsed_time
                results[TestType.PATH.value][Attribute.ADDING_GAS.value] += receipt_add.gasUsed
                results[TestType.PATH.value][Attribute.VERIFYING_GAS.value] += gas_estimate

            is_first_chunk = False
        # After whole tree generation
        # Calculate average block size
        priv_keys_list, pub_keys_keys_list = priv_keys_list_for_next_lvl, pub_keys_list_for_next_lvl
        num_of_signatures_on_next_lvl = ring_size ** (lvl - 1)
        assert (
            len(priv_keys_list_for_next_lvl) == num_of_signatures_on_next_lvl
        ), f"{len(priv_keys_list_for_next_lvl)}, {num_of_signatures_on_next_lvl}"

    latest_block_number = client.web3.eth.block_number
    start_block_number = latest_block_number - num_of_all_nodes + 1
    for block_number in range(start_block_number, latest_block_number + 1):
        block = client.web3.eth.get_block(block_number)
        results[TestType.SINGLE.value][Attribute.BLOCK_SIZE.value] += block.size

    results[TestType.SINGLE.value] = [value / num_of_all_nodes for value in results[TestType.SINGLE.value]]
    assert len(all_priv_keys_list) == num_of_initial_pub_keys, f"{len(all_priv_keys_list)=}"
    return results


def equivalent_test(results: list, num_of_initial_pub_keys: int, blockchain_priv_key: str, client: BlockchainClient):
    # pylint: disable=R0914
    """
    Test the performance of an equivalent signature process on the blockchain.

    :param results: The list to store the test results.
    :type results: list

    :param num_of_initial_pub_keys: The number of initial public keys.
    :type num_of_initial_pub_keys: int

    :param blockchain_priv_key: The private key of the blockchain account.
    :type blockchain_priv_key: str

    :param client: An instance of BlockchainClient for interacting with the blockchain.
    :type client: BlockchainClient
    """
    priv_keys_list, pub_keys_list = generate_and_register_keys(blockchain_priv_key, client, num_of_initial_pub_keys)
    signing_priv_key, _ = priv_keys_list.pop(0), pub_keys_list.pop(0)
    message = generate_random_scalar()
    start_time = time.time()
    signature = NodeRingSchnorrSignature.sign(message, signing_priv_key, pub_keys_list)
    end_time = time.time()
    elapsed_time = end_time - start_time

    receipt_add = client.store_signature(blockchain_priv_key, message, signature)
    arguments_to_verify = client.convert_nr_sign_sigma_to_sol_arguments(signature)
    gas_estimate = client.contract.functions.testVerifyNodeRingSignature(message, *arguments_to_verify).estimate_gas()
    block_number = client.web3.eth.block_number
    block = client.web3.eth.get_block(block_number)
    # equivalent
    results[TestType.EQUIVALENT.value][Attribute.SIGNING_TIME.value] += elapsed_time
    results[TestType.EQUIVALENT.value][Attribute.ADDING_GAS.value] += receipt_add.gasUsed
    results[TestType.EQUIVALENT.value][Attribute.VERIFYING_GAS.value] += gas_estimate
    results[TestType.EQUIVALENT.value][Attribute.BLOCK_SIZE.value] += block.size


def aggregated_tests_tree(ring_sizes_list: list[int], heights_of_tree: list[int], num_of_trials):
    """
    Perform aggregated tests for a range of ring sizes and heights of tree.

    :param ring_sizes_list: List of ring sizes to test.
    :type ring_sizes_list: list[int]

    :param heights_of_tree: List of heights of tree to test.
    :type heights_of_tree: list[int]

    :param num_of_trials: Number of trials to run for each combination of ring size and height.
    :type num_of_trials: int
    """
    combinations = product(TestType, Attribute)
    header = "RING_SIZE,TREE_HEIGHT,NUM_OF_INITAIL_PUB_KEYS,"
    header += ",".join(f"{test_type.name}_{attribute.name}" for test_type, attribute in combinations)
    print(header, flush=True)

    for ring_size, tree_height in zip(ring_sizes_list, heights_of_tree):
        num_of_initial_pub_keys = ring_size**tree_height
        results_for_all_trials = [[0 for _ in range(len(Attribute))] for _ in range(len(TestType))]
        for _ in range(num_of_trials):
            client, blockchain_priv_key = deploy_contract_and_get_account()
            results = full_tree_test(ring_size, tree_height, num_of_initial_pub_keys, blockchain_priv_key, client)
            client, blockchain_priv_key = deploy_contract_and_get_account()
            equivalent_test(results, num_of_initial_pub_keys, blockchain_priv_key, client)
            results_for_all_trials = [
                [results_for_all_trials[i][j] + results[i][j] for j in range(len(results_for_all_trials[0]))]
                for i in range(len(results_for_all_trials))
            ]
        results_for_all_trials = [[element / num_of_trials for element in row] for row in results]
        row_to_print = f"{ring_size},{tree_height},{num_of_initial_pub_keys},"
        row_to_print += ",".join(
            str(results_for_all_trials[test_type.value][attribute.value])
            for test_type in TestType
            for attribute in Attribute
        )
        print(row_to_print, flush=True)


def parse_range_list(arg):
    """
    Parse a string containing comma-separated numbers and ranges into a list of integers.

    Examples:
    - "1,3,5" -> [1, 3, 5]
    - "1-3,5" -> [1, 2, 3, 5]
    - "[1,,5,9]" -> [1, 5, 9] (Assuming input format includes square brackets)

    :param arg: The input string containing numbers and ranges.
    :type arg: str

    :return: A list of integers parsed from the input string.
    :rtype: list[int]
    """
    # Remove square brackets if present
    arg = arg.strip("[]")

    # Split by commas
    parts = arg.split(",")
    numbers = []

    # Handle each part
    for part in parts:
        if "-" in part:
            # Handle range
            start, end = map(int, part.split("-"))
            numbers.extend(range(start, end + 1))
        elif part:
            # Handle individual number
            numbers.append(int(part))

    return numbers


def parse_arguments():
    """
    Parse command-line arguments.

    :return: Parsed arguments.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Argument parser for storing_vs_verifying and tree configurations")

    # Creating subparsers
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Storing group
    storing_parser = subparsers.add_parser("storing_vs_verifying", help="storing_vs_verifying configurations")
    storing_parser.add_argument("--max_ring_size", type=int, required=True, help="Maximum ring size")
    storing_parser.add_argument("--num_of_trials", type=int, required=True, help="Number of trials")

    # Tree group
    tree_parser = subparsers.add_parser("full_tree", help="Tree configurations")
    tree_parser.add_argument("--ring_sizes", type=parse_range_list, required=True, help="Ring sizes")
    tree_parser.add_argument("--heights_of_tree", type=parse_range_list, required=True, help="Height of tree")
    tree_parser.add_argument("--num_of_trials", type=int, required=True, help="Number of trials")

    return parser.parse_args()


def main():
    """
    Main function to handle argument parsing and execution of tests.
    """
    args = parse_arguments()
    current_directory = os.path.dirname(os.path.realpath(__file__))
    output_filename = os.path.join(current_directory, "results/csv_files", args.command + ".csv")

    with open(output_filename, "w", encoding="ascii") as file:
        original_fd = sys.stdout
        sys.stdout = Tee(sys.stdout, file)
        # Handling the parsed arguments
        if args.command == "storing_vs_verifying":
            storing_vs_verifying(args.max_ring_size, args.num_of_trials)
        elif args.command == "full_tree":
            if len(args.ring_sizes) != len(args.heights_of_tree):
                print("There should be the same number of ring sizes and heights")
                sys.exit(1)
            aggregated_tests_tree(args.ring_sizes, args.heights_of_tree, args.num_of_trials)
        sys.stdout = original_fd


if __name__ == "__main__":
    main()
