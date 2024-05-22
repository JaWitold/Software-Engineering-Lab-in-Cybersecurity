import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from test_performance import Attribute, TestType


def setup_figure():
    """
    Set up the plotting environment with predefined font sizes and figure size.

    This function configures the default text sizes for various plot elements
    (font, axes title, labels, tick labels, figure title) and sets up a grid.

    """
    small_size = 10
    medium_size = 12
    bigger_size = 14
    fig_width = 6  # Width in inches for a two-column layout
    fig_height = 5  # Height in inches for a two-column layout

    plt.rc("font", size=small_size)  # controls default text sizes
    plt.rc("axes", titlesize=small_size)  # fontsize of the axes title
    plt.rc("axes", labelsize=medium_size)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=small_size)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=small_size)  # fontsize of the tick labels
    plt.rc("legend", fontsize=small_size)  # legend fontsize
    plt.rc("figure", titlesize=bigger_size)  # fontsize of the figure title

    plt.figure(figsize=(fig_width, fig_height))
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

    df["X_AXIS"] = "(" + df["RING_SIZE"].astype(str) + ", " + df["TREE_HEIGHT"].astype(str) + ")"
    x = np.arange(len(df["X_AXIS"]))  # the label locations
    bar_width = 0.2  # width of the bars
    for attribute in Attribute:
        setup_figure()
        plt.grid(False)
        for i, test_type in enumerate(TestType):
            test_type_data = df["_".join([test_type.name, attribute.name])]
            plt.bar(x + i * bar_width, test_type_data, bar_width, label=test_type.name)
        plt.xticks(x + bar_width, df["X_AXIS"])
        plt.xlabel("ring size ^ tree height")
        plt.ylabel(attribute.label_str())
        # plt.title(attribute.label_str() + " vs ring size ^ tree height")
        plt.legend()
        plt.tight_layout()
        filename = os.path.join(dir_for_plots, "full_tree_" + attribute.name.lower() + ".pdf")
        plt.savefig(filename, dpi=300)
        plt.close()


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
    mean_multiplicity = (df[Attribute.ADDING_GAS.name] / df[Attribute.VERIFYING_GAS.name]).mean().mean()
    print(f"{Attribute.ADDING_GAS.name} / {Attribute.VERIFYING_GAS.name} mean =  {mean_multiplicity}")

    # Gas usage
    setup_figure()
    x_label = "RING_SIZE"
    plt.plot(
        df[x_label], df[Attribute.ADDING_GAS.name], marker="o", linestyle="-", color="b", label="adding single node"
    )
    plt.plot(
        df[x_label],
        df[Attribute.VERIFYING_GAS.name],
        marker="+",
        linestyle="--",
        color="r",
        label="verification only",
    )
    # plt.title("Gas usage vs Size of a ring")
    plt.xlabel("Size of a ring")
    plt.ylabel("Gas usage")
    plt.legend()
    plt.tight_layout()
    filename = os.path.join(dir_for_plots, "storing_vs_verifying_gas_usage.pdf")
    plt.savefig(filename, dpi=300)
    plt.close()

    # Block size
    setup_figure()
    plt.plot(
        df[x_label], df[Attribute.BLOCK_SIZE.name], marker="o", linestyle="-", color="b", label="block size [bytes]"
    )
    # plt.title("Block size [bytes] vs Size of a ring")
    plt.xlabel("Size of a ring")
    plt.ylabel("Block size [bytes]")
    # plt.legend()
    plt.tight_layout()
    filename = os.path.join(dir_for_plots, "storing_vs_verifying_" + Attribute.BLOCK_SIZE.name.lower() + ".pdf")
    plt.savefig(filename, dpi=300)
    plt.close()


if __name__ == "__main__":
    test_types = ["full_tree", "storing_vs_verifying"]
    plot_functions_list = [plot_full_tree_test, plot_storing_vs_verifying]
    current_directory = os.path.dirname(os.path.realpath(__file__))
    results_dir = os.path.join(current_directory, "results")
    csv_filenames_list = [os.path.join(results_dir, "csv_files", test_type + ".csv") for test_type in test_types]
    dir_for_plots = os.path.join(results_dir, "plots")

    for i, csv_filename in enumerate(csv_filenames_list):
        if os.path.exists(csv_filename):
            df = pd.read_csv(csv_filename)
            plot_functions_list[i](df, dir_for_plots)
            print(f"Plots saved to {dir_for_plots} directory with prefix: {test_types[i]}")
        else:
            print(csv_filename, "doesn't exists")
