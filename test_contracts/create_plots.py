import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from test_performance import Attribute, TestType

SMALL_SIZE = 12
MEDIUM_SIZE = 14
BIGGER_SIZE = 18


def setup_figure():
    """
    Set up the plotting environment with predefined font sizes and figure size.

    This function configures the default text sizes for various plot elements
    (font, axes title, labels, tick labels, figure title) and sets up a grid.

    """
    plt.rc("font", size=SMALL_SIZE)  # controls default text sizes
    plt.rc("axes", titlesize=SMALL_SIZE)  # fontsize of the axes title
    plt.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
    # plt.rc('legend', fontsize=MEDIUM_SIZE)   # legend fontsize
    plt.rc("figure", titlesize=BIGGER_SIZE)  # fontsize of the figure title
    plt.figure(figsize=(10, 7))
    plt.grid(True)


def plot_full_tree_test(df, dir_for_plots: str):
    # pylint: disable=W0621
    """
    Generate and save bar plots for each attribute, grouped by test type.

    This function creates bar plots for each attribute of the test results, with bars
    grouped by test type. The X-axis represents concatenated values of RING_SIZE and TREE_HEIGHT.

    :param df: DataFrame containing the test results.
    :type df: pd.DataFrame

    :param dir_for_plots: Directory where the plots will be saved.
    :type dir_for_plots: str

    """
    df["X_AXIS"] = df["RING_SIZE"].astype(str) + "*" + df["TREE_HEIGHT"].astype(str)
    x = np.arange(len(df["X_AXIS"]))  # the label locations
    bar_width = 0.2  # width of the bars
    for attribute_name in [attribute.name for attribute in Attribute]:
        setup_figure()
        plt.grid(False)
        for i, test_type_name in enumerate([test_type.name for test_type in TestType]):
            test_type_data = df["_".join([test_type_name, attribute_name])]
            plt.bar(x + i * bar_width, test_type_data, bar_width, label=test_type_name)
        plt.xticks(x+bar_width, df["X_AXIS"])
        plt.xlabel("RING_SIZE * HEIGHT_OF_TREE")
        plt.ylabel(attribute_name)
        plt.title(attribute_name + " vs RING_SIZE * HEIGHT_OF_TREE")
        plt.legend()
        filename = os.path.join(dir_for_plots, "full_tree_" + attribute_name.lower() + ".pdf")
        plt.savefig(filename, dpi=300)
        plt.close()
    print(f"Plots saved to {dir_for_plots} directory.")


def plot_storing_vs_verifying(df, dir_for_plots: str):
    # pylint: disable=W0621
    """
    Generate and save line plots for gas usage and block size against ring size.

    This function creates line plots for gas usage (adding gas and verify gas) and
    block size versus ring size, and saves them as PDF files.

    :param df: DataFrame containing the test results.
    :type df: pd.DataFrame

    :param dir_for_plots: Directory where the plots will be saved.
    :type dir_for_plots: str

    """
    setup_figure()
    x_label = "RING_SIZE"
    plt.plot(
        df[x_label], df[Attribute.ADDING_GAS.name], marker="o", linestyle="-", color="b", label="gas used for adding"
    )
    plt.plot(
        df[x_label],
        df[Attribute.VERIFY_GAS.name],
        marker="+",
        linestyle="--",
        color="r",
        label="gas used for verification only",
    )
    plt.title("Gas usage vs Size of a ring", fontsize=BIGGER_SIZE)
    plt.xlabel("Size of a ring")
    plt.ylabel("Gas usage")
    plt.legend()
    plt.tight_layout()
    filename = os.path.join(dir_for_plots, "storing_vs_verifying_gas_usage.pdf")
    plt.savefig(filename, dpi=300)
    plt.close()

    setup_figure()
    plt.plot(
        df[x_label], df[Attribute.BLOCK_SIZE.name], marker="o", linestyle="-", color="b", label="block size [bytes]"
    )
    plt.title("Block size [bytes] vs Size of a ring", fontsize=BIGGER_SIZE)
    plt.ylabel("Block size [bytes]")
    plt.legend()
    plt.tight_layout()
    filename = os.path.join(dir_for_plots, "storing_vs_verifying_" + Attribute.BLOCK_SIZE.name.lower() + ".pdf")
    plt.savefig(filename, dpi=300)
    plt.close()


def parse_arguments():
    """
    Parse command line arguments for the script.

    This function sets up argument parsing for the script, including options for specifying
    the test type (full_tree or storing_vs_verifying).

    :returns: Parsed command line arguments.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description="Process command line arguments")
    parser.add_argument(
        "--test_type", choices=["full_tree", "storing_vs_verifying"], help="Specify the test type (tree or storage)"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    current_directory = os.path.dirname(os.path.realpath(__file__))
    results_dir = os.path.join(current_directory, "results")
    csv_filename = os.path.join(results_dir, "csv_files", args.test_type + ".csv")
    df = pd.read_csv(csv_filename)
    dir_for_plots = os.path.join(results_dir, "plots")
    test_type = args.test_type
    print("Test Type:", test_type)

    if args.test_type == "full_tree":
        plot_full_tree_test(df, dir_for_plots)
    elif args.test_type == "storing_vs_verifying":
        plot_storing_vs_verifying(df, dir_for_plots)
    else:
        print("Wrong test type!")
