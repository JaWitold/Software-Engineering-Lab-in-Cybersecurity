import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from test_performance import FinalAttr, TestType

X_DOMAIN_STR = "RING_SIZE"


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

    df["X_AXIS"] = "(" + df[X_DOMAIN_STR].astype(str) + ", " + df["TREE_HEIGHT"].astype(str) + ")"
    x = np.arange(len(df["X_AXIS"]))  # the label locations
    bar_width = 0.2  # width of the bars
    for attribute in FinalAttr:
        setup_figure()
        plt.grid(False)
        for i, test_type in enumerate(TestType):
            test_type_data = df["_".join([test_type.name, attribute.name])]
            plt.bar(x + i * bar_width, test_type_data, bar_width, label=test_type.name)
        plt.xticks(x + bar_width, df["X_AXIS"])
        plt.xlabel("(ring size, tree height)")
        plt.ylabel(attribute.label_str())
        # plt.title(attribute.label_str() + " vs ring size ^ tree height")
        plt.legend()
        plt.tight_layout()
        filename = os.path.join(dir_for_plots, "full_tree_" + attribute.name.lower() + ".pdf")
        plt.savefig(filename, dpi=300)
        plt.close()


def plot_storing_vs_verifying(df, dir_for_plots: str):
    # pylint: disable=W0621
    # pylint: disable=R0914
    """
    Generate and save line plots for gas usage and block size against ring size.

    This function creates line plots for gas usage (adding gas and verify gas) and
    block size versus ring size, and saves them as PDF files.

    :param df: DataFrame containing the test results.
    :type df: pd.DataFrame

    :param dir_for_plots: Directory where the plots will be saved.
    :type dir_for_plots: str

    """
    mean_multiplicity = (df[FinalAttr.MEAN_ADDING_GAS.name] / df[FinalAttr.MEAN_VERIFYING_GAS.name]).mean().mean()
    print(f"{FinalAttr.MEAN_VERIFYING_GAS.name} / {FinalAttr.MEAN_VERIFYING_GAS.name} mean =  {mean_multiplicity}")

    setup_figure()
    _, ax1 = plt.subplots()
    ax2 = ax1.twinx()

    x_label = "Size of a ring"
    y1_label = "Gas usage"
    y2_label = "Block size [bytes]"

    ax1_color = "b"
    ax2_color = "g"

    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y1_label, color=ax1_color)
    ax2.set_ylabel(y2_label, color=ax2_color)

    # block size
    ax2.bar(
        df[X_DOMAIN_STR],
        df[FinalAttr.BLOCK_SIZE.name],
        0.1,
        color=ax2_color,
        label="mined block for node",
    )
    # Gas usage
    ax1.plot(
        df[X_DOMAIN_STR],
        df[FinalAttr.MEAN_ADDING_GAS.name],
        marker="o",
        linestyle="-",
        color=ax1_color,
        label="adding single node",
    )
    # verification
    ax1.plot(
        df[X_DOMAIN_STR],
        df[FinalAttr.MEAN_VERIFYING_GAS.name],
        marker="+",
        linestyle="--",
        color=ax1_color,
        label="verification only",
    )

    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()

    plt.tight_layout()
    ax1.legend(lines + lines2, labels + labels2, loc=0)
    filename = os.path.join(dir_for_plots, "gas_usage_and_block_size.pdf")
    plt.savefig(filename, dpi=300)
    plt.close()

    # Block size
    setup_figure()
    plt.plot(
        df[X_DOMAIN_STR],
        df[FinalAttr.BLOCK_SIZE.name],
        marker="o",
        linestyle="-",
        color="b",
        label="block size [bytes]",
    )
    # plt.title("Block size [bytes] vs Size of a ring")
    plt.xlabel("Size of a ring")
    plt.ylabel("Block size [bytes]")
    # plt.legend()
    plt.tight_layout()
    filename = os.path.join(dir_for_plots, "storing_vs_verifying_" + FinalAttr.BLOCK_SIZE.name.lower() + ".pdf")
    plt.savefig(filename, dpi=300)
    plt.close()

    # Signing time
    # setup_figure()
    # plt.plot(
    #     df[X_DOMAIN_STR],
    #     df[FinalAttr.MEAN_SIGNING_TIME.name] - df[FinalAttr.STD_DEV_SIGNING_TIME.name],
    #     marker="o",
    #     linestyle="-",
    #     color="g",
    #     label="MEAN - SD",
    # )
    plt.plot(df[X_DOMAIN_STR], df[FinalAttr.MEAN_SIGNING_TIME.name], marker="o", linestyle="-", color="b", label="MEAN")
    # plt.plot(
    #     df[X_DOMAIN_STR],
    #     df[FinalAttr.MEAN_SIGNING_TIME.name] + df[FinalAttr.STD_DEV_SIGNING_TIME.name],
    #     marker="o",
    #     linestyle="-",
    #     color="r",
    #     label="MEAN + SD",
    # )
    # plt.title("Block size [bytes] vs Size of a ring")
    plt.xlabel("Size of a ring")
    plt.ylabel(FinalAttr.MEAN_SIGNING_TIME.label_str())
    plt.legend()
    plt.tight_layout()
    filename = os.path.join(dir_for_plots, "storing_vs_verifying_" + FinalAttr.MEAN_SIGNING_TIME.name.lower() + ".pdf")
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
            X_DOMAIN_STR = list(df.columns)[0]
            plot_functions_list[i](df, dir_for_plots)
            print(f"Plots saved to {dir_for_plots} directory with prefix: {test_types[i]}")
        else:
            print(csv_filename, "doesn't exists")
