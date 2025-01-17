"""Configures the argparse we use."""
import argparse

from __version__ import __version__


def get_parser():
    """Returns an argparser."""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [<options>] [--] <input file>",
        description="Capital gains calculator",
    )

    parser.add_argument(
        "filename", type=str, help=argparse.SUPPRESS, metavar="<input file>"
    )

    parser.add_argument(
        "-y",
        "--fiscal-year",
        dest="fiscal_year",
        type=int,
        default=0,
        help="fiscal year to process, if specified transactions from other years will be ignored.",
        metavar="<n>",
    )

    parser.add_argument(
        "-d",
        "--decimal-places",
        dest="decimal_places",
        type=int,
        default=0,
        help="round $ to %(metavar)s decimal places (default: %(default)s)",
        metavar="<n>",
    )
    parser.add_argument(
        "-s",
        "--shares-decimal-places",
        dest="shares_decimal_places",
        type=int,
        default=0,
        help="round shares to %(metavar)s decimal places (default: %(default)s)",
        metavar="<n>",
    )
    parser.add_argument(
        "-t", "--totals", action="store_true", help="output totals")
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="verbose output")
    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s " + __version__
    )
    parser.add_argument(
        "-w",
        "--wash-sales",
        dest="wash_sales",
        action=argparse.BooleanOptionalAction,
        help="identify wash sales and adjust cost basis",
        default=True,
    )

    return parser
