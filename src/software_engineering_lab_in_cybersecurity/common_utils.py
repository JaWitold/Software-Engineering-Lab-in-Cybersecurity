import argparse
import logging
import sys
from typing import Any, Dict, List


def parse_args(description: str, args: List[str], config: Dict[str, Any]) -> argparse.Namespace:
    """
    Generic command line parameter parser.

    :param description: Description of the command line tool.
    :type description: str
    :param args: Command line parameters as list of strings.
    :type args: List[str]
    :param config: Configuration for additional arguments, including version and custom arguments.
    :type config: Dict[str, Any]
    :returns: Command line parameters namespace.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--version", action="version", version=config.get("version"))
    parser.add_argument(
        "-v", "--verbose", dest="loglevel", help="Set loglevel to INFO.", action="store_const", const=logging.INFO
    )
    parser.add_argument(
        "-vv",
        "--very-verbose",
        dest="loglevel",
        help="Set loglevel to DEBUG.",
        action="store_const",
        const=logging.DEBUG,
    )

    # Dynamically add custom arguments based on config
    for arg_name, arg_config in config.get("custom_args", {}).items():
        parser.add_argument(arg_name, **arg_config)

    return parser.parse_args(args)


def setup_logging(loglevel: int | str | None) -> None:
    """
    Setup basic logging.

    :param loglevel: Minimum loglevel for emitting messages.
    :type loglevel: int | str | None
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout, format=logformat, datefmt="%Y-%m-%d %H:%M:%S")
