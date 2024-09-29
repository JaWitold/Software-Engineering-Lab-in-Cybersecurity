"""
@ TODO: Use numpy for results and calculate standard deviation
"""

import argparse
import copy
import os
import random
import sys
import time
from datetime import datetime
from enum import Enum
from itertools import product
from socket import timeout as socket_timeout

import numpy as np
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


class TestedAttr(Enum):
    """
    Enumeration for different attributes being tested.
    """

    ADDING_GAS = 0
    VERIFYING_GAS = 1
    SIGNING_TIME = 2


class FinalAttr(Enum):
    """
    Enumeration for attributes that will be single values with final result
    """

    MEAN_ADDING_GAS = TestedAttr.ADDING_GAS.value
    MEAN_VERIFYING_GAS = TestedAttr.VERIFYING_GAS.value
    MEAN_SIGNING_TIME = TestedAttr.SIGNING_TIME.value
    STD_DEV_ADDING_GAS = TestedAttr.SIGNING_TIME.value + 1
    STD_DEV_VERIFYING_GAS = TestedAttr.SIGNING_TIME.value + 2
    STD_DEV_SIGNING_TIME = TestedAttr.SIGNING_TIME.value + 3
    BLOCK_SIZE = TestedAttr.SIGNING_TIME.value + 4

    def label_str(self):
        """
        Function that is used for plots' labels
        """
        attributes_strs = {
            FinalAttr.MEAN_ADDING_GAS: "Mean gas usage for adding signature",
            FinalAttr.MEAN_VERIFYING_GAS: "Mean gas usage for verifying signature",
            FinalAttr.BLOCK_SIZE: "Block size [bytes]",
            FinalAttr.MEAN_SIGNING_TIME: "Mean duration [s] of signature creation",
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
    header = "RING_SIZE,"
    header += ",".join(f"{attribute.name}" for attribute in FinalAttr)
    print(header)
    intermediate_results = np.zeros((num_of_trials, len(TestedAttr)), dtype=float)

    for curr_ring_size in range(1, max_ring_size + 1):
        for i in range(num_of_trials):
            # python generation part
            priv_keys_list, pub_keys_list = generate_and_register_keys(blockchain_priv_key, client, curr_ring_size)
            signing_priv_key, _ = priv_keys_list.pop(), pub_keys_list.pop()
            message = generate_random_scalar()
            start_time = time.time()
            signature = NodeRingSchnorrSignature.sign(message, signing_priv_key, pub_keys_list)[1]
            end_time = time.time()
            intermediate_results[i][TestedAttr.SIGNING_TIME.value] = end_time - start_time

            # action on blockchain
            receipt_add = client.store_signature(blockchain_priv_key, message, signature)
            intermediate_results[i][TestedAttr.ADDING_GAS.value] = receipt_add.gasUsed
            arguments_to_verify = client.convert_nr_sign_sigma_to_sol_arguments(signature)
            gas_estimate = client.contract.functions.testVerifyNodeRingSignature(
                message, *arguments_to_verify
            ).estimate_gas()
            intermediate_results[i][TestedAttr.VERIFYING_GAS.value] = gas_estimate

        mean_values = np.mean(intermediate_results, axis=0)
        std_values = np.std(intermediate_results, axis=0)
        latest_block_number = client.web3.eth.block_number
        block_size = client.web3.eth.get_block(latest_block_number).size

        row_to_print = f"{curr_ring_size},"
        row_to_print += ",".join(str(mean_values[attr.value]) for attr in TestedAttr)
        row_to_print += ","
        row_to_print += ",".join(str(std_values[attr.value]) for attr in TestedAttr)
        row_to_print += "," + str(block_size)
        print(row_to_print, flush=True)


def full_tree_test(
    ring_size: int,
    tree_height: int,
    all_priv_keys_list: list[int],
    all_pub_keys_list: list,
    blockchain_priv_key: str,
    client: BlockchainClient,
):
    # pylint: disable=R0914
    """
    Test the performance of creating a full tree of signatures.

    :param ring_size: The ring size for each level of the tree.
    :type ring_size: int

    :param tree_height: The height of the tree (defined as the number of edges
        from the leaf node to the root node)
    :type tree_height: int

    :param all_priv_keys_list: List of the private keys for which
        the public keys have been registered.
    :type all_priv_keys_list: list

    :param all_pub_keys_list: List of registered public keys.
    :type all_pub_keys_list: list

    :param blockchain_priv_key: The private key of the blockchain account.
    :type blockchain_priv_key: str

    :param client: An instance of BlockchainClient for interacting with the blockchain.
    :type client: BlockchainClient

    :returns: A list of results for different test types and attributes.
    :rtype: list[list[float]]
    """
    num_of_added_nodes = 0
    num_of_all_nodes = int((ring_size ** (tree_height + 1) - 1) // (ring_size - 1))
    intermediate_results = np.zeros((num_of_all_nodes, len(TestedAttr)), dtype=float)

    for lvl in range(tree_height + 1, 0, -1):  # +1 bcs edge-based definiton of height is used
        priv_keys_list_for_next_lvl, pub_keys_list_for_next_lvl = [], []
        is_first_chunk = True
        for priv_keys_chunk, pub_keys_chunk in zip(
            _chunked(all_priv_keys_list, ring_size), _chunked(all_pub_keys_list, ring_size)
        ):
            idx_to_use = 0 if is_first_chunk else random.randint(0, len(priv_keys_chunk) - 1)
            curr_lvl_signature_priv_key = priv_keys_chunk.pop(idx_to_use)
            pub_keys_chunk.pop(idx_to_use)
            message = generate_random_scalar()
            start_time = time.time()
            next_lvl_signature_private_key, signature = NodeRingSchnorrSignature.sign(
                message, curr_lvl_signature_priv_key, pub_keys_chunk
            )
            elapsed_time = time.time() - start_time
            priv_keys_list_for_next_lvl.append(next_lvl_signature_private_key)
            pub_keys_list_for_next_lvl.append(signature.signature_public_key)

            # action on blockchain
            receipt_add = client.store_signature(blockchain_priv_key, message, signature)
            arguments_to_verify = client.convert_nr_sign_sigma_to_sol_arguments(signature)
            gas_estimate = client.contract.functions.testVerifyNodeRingSignature(
                message, *arguments_to_verify
            ).estimate_gas()

            intermediate_results[num_of_added_nodes][TestedAttr.ADDING_GAS.value] = receipt_add.gasUsed
            intermediate_results[num_of_added_nodes][TestedAttr.SIGNING_TIME.value] = elapsed_time
            intermediate_results[num_of_added_nodes][TestedAttr.VERIFYING_GAS.value] = gas_estimate
            num_of_added_nodes += 1

        # After whole level generation
        all_priv_keys_list, all_pub_keys_list = priv_keys_list_for_next_lvl, pub_keys_list_for_next_lvl
        num_of_signatures_on_next_lvl = ring_size ** (lvl - 1)
        assert (
            len(priv_keys_list_for_next_lvl) == num_of_signatures_on_next_lvl
        ), f"{len(priv_keys_list_for_next_lvl)=} != {num_of_signatures_on_next_lvl=}"
    assert num_of_added_nodes == num_of_all_nodes, f"{num_of_added_nodes=} != {num_of_all_nodes=}"

    return np.mean(intermediate_results, axis=0)


def equivalent_test(
    all_priv_keys_list: list[int],
    all_pub_keys_list: list,
    blockchain_priv_key: str,
    client: BlockchainClient,
):
    # pylint: disable=R0914
    """
    Test the performance of an equivalent signature process on the blockchain.

    :param all_priv_keys_list: List of the private keys for which
        the public keys have been registered.
    :type all_priv_keys_list: list

    :param all_pub_keys_list: List of registered public keys.
    :type all_pub_keys_list: list

    :param blockchain_priv_key: The private key of the blockchain account.
    :type blockchain_priv_key: str

    :param client: An instance of BlockchainClient for interacting with the blockchain.
    :type client: BlockchainClient
    """
    signing_priv_key, _ = all_priv_keys_list.pop(0), all_pub_keys_list.pop(0)
    message = generate_random_scalar()
    start_time = time.time()
    signature = NodeRingSchnorrSignature.sign(message, signing_priv_key, all_pub_keys_list)[1]
    end_time = time.time()
    elapsed_time = end_time - start_time

    receipt_add = client.store_signature(blockchain_priv_key, message, signature)
    arguments_to_verify = client.convert_nr_sign_sigma_to_sol_arguments(signature)
    gas_estimate = client.contract.functions.testVerifyNodeRingSignature(message, *arguments_to_verify).estimate_gas()

    results = np.zeros((len(TestedAttr)), dtype=float)
    results[TestedAttr.ADDING_GAS.value] = receipt_add.gasUsed
    results[TestedAttr.VERIFYING_GAS.value] = gas_estimate
    results[TestedAttr.SIGNING_TIME.value] = elapsed_time

    return results


def aggregated_tests_tree(ring_sizes_list: list[int], heights_of_tree: list[int], num_of_trials):
    # pylint: disable=R0914
    """
    Perform aggregated tests for a range of ring sizes and heights of tree.

    :param ring_sizes_list: List of ring sizes to test.
    :type ring_sizes_list: list[int]

    :param heights_of_tree: List of heights of tree to test.
    :type heights_of_tree: list[int]

    :param num_of_trials: Number of trials to run for each combination of ring size and height.
    :type num_of_trials: int
    """
    combinations = product(TestType, FinalAttr)
    header = "RING_SIZE,TREE_HEIGHT,NUM_OF_INITAIL_PUB_KEYS,"
    header += ",".join(f"{test_type.name}_{attribute.name}" for test_type, attribute in combinations)
    print(header, flush=True)

    for ring_size, tree_height in zip(ring_sizes_list, heights_of_tree):
        num_of_initial_pub_keys = ring_size ** (tree_height + 1)
        intermediate_results = np.zeros((num_of_trials, len(TestType), len(TestedAttr)), dtype=float)
        block_sizes = np.zeros(len(TestType), dtype=int)
        for trial_idx in range(num_of_trials):
            client, blockchain_priv_key = deploy_contract_and_get_account()
            priv_keys_list, pub_keys_list = generate_and_register_keys(
                blockchain_priv_key, client, num_of_initial_pub_keys
            )
            priv_keys_list_copy = copy.deepcopy(priv_keys_list)
            pub_keys_list_copy = copy.deepcopy(pub_keys_list)

            # equivalent
            try:
                intermediate_results[trial_idx][TestType.EQUIVALENT.value] = equivalent_test(
                    priv_keys_list, pub_keys_list, blockchain_priv_key, client
                )

            except socket_timeout:
                intermediate_results[trial_idx][TestType.EQUIVALENT.value] = [0 for _ in range(len(FinalAttr))]
            if trial_idx == 0:
                latest_block_number = client.web3.eth.block_number
                block_sizes[TestType.EQUIVALENT.value] = client.web3.eth.get_block(latest_block_number).size

            # single
            intermediate_results[trial_idx][TestType.SINGLE.value] = full_tree_test(
                ring_size, tree_height, priv_keys_list_copy, pub_keys_list_copy, blockchain_priv_key, client
            )
            if trial_idx == 0:
                latest_block_number = client.web3.eth.block_number
                block_sizes[TestType.SINGLE.value] = client.web3.eth.get_block(latest_block_number).size

            # path
            intermediate_results[trial_idx][TestType.PATH.value] = intermediate_results[trial_idx][
                TestType.SINGLE.value
            ] * (tree_height + 1)
            if trial_idx == 0:
                block_sizes[TestType.PATH.value] = block_sizes[TestType.SINGLE.value] * (tree_height + 1)

        mean_values = np.mean(intermediate_results, axis=0)
        std_values = np.std(intermediate_results, axis=0)

        row_to_print = f"{ring_size},{tree_height},{num_of_initial_pub_keys}"
        for test_type in TestType:
            row_to_print += ","
            row_to_print += ",".join(str(mean_values[test_type.value][attribute.value]) for attribute in TestedAttr)
            row_to_print += ","
            row_to_print += ",".join(str(std_values[test_type.value][attribute.value]) for attribute in TestedAttr)
            row_to_print += "," + str(block_sizes[test_type.value])
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
    tree_parser.add_argument(
        "--heights_of_tree",
        type=parse_range_list,
        required=True,
        help="Height of tree defined as the number of edges from the leaf node to the root node",
    )
    tree_parser.add_argument("--num_of_trials", type=int, required=True, help="Number of trials")

    return parser.parse_args()


def main():
    """
    Main function to handle argument parsing and execution of tests.
    """
    dt_string = datetime.now().isoformat()
    args = parse_arguments()
    current_directory = os.path.dirname(os.path.realpath(__file__))
    output_filename = os.path.join(current_directory, "results/csv_files", args.command + "_" + dt_string + ".csv")

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
