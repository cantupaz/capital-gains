"""Loads transactions from a file."""

import collections
import csv
import datetime as dt
import decimal
import functools
import logging
from model import Transaction, Lot
from const import SHARES_PER_CONTRACT

OPTION_TRANSACTIONS = (
    "buy open",
    "option expire",
    "option assignment",
    "sell to close",
    "sell to open",
    "buy to close",
)
SHORT_OPTION_TRANSACTIONS = (
    "sell to open",
    "buy to close",
)


OPEN_LOT_TRANSACTIONS = (
    "buy",
    "buy open",
    "sell to open",
)
CLOSE_LOT_TRANSACTIONS = (
    "sell",
    "option expire",
    "option assignment",
    "buy to close",
    "sell to close",
)


def compare_function(item1: list[any], item2: list[any]):
    """Compare function to sort the input file."""

    # first sort by date
    date_comp = item1[0] - item2[0]
    if date_comp.days != 0:
        return date_comp.days

    # if same date, then ensure that transactions that open lots are sorted
    # before transactions that close them
    # (they can be out of order if both happen the same day)
    comp = 0
    if (item1[1] in OPEN_LOT_TRANSACTIONS) and (item2[1] in CLOSE_LOT_TRANSACTIONS):
        comp = -1
    elif (item1[1] in CLOSE_LOT_TRANSACTIONS) and (item2[1] in OPEN_LOT_TRANSACTIONS):
        comp = 1
    return comp


# Reads transactions from a csv file.
# To represent the starting portfolio, we need to add some lines with
# purchase transactions to the file. Those will get processed and added as Lots
# alternatively, we can implement changes to have a separate file with the portfolio

def load_transactions(filename: str, fiscal_year: int = 0):
    """Returns dictionaries with open lots and sales. The dictionary keys are symbols."""

    open_lots = collections.defaultdict(list)
    sales = collections.defaultdict(list)

    with open(filename, "r", encoding="utf-8") as in_file:
        reader = csv.reader(in_file)

        # Skip header
        next(reader)

        rows = []
        for (date, order_type, symbol, cusip, desc, quantity, price, fee, net) in reader:
            date = dt.datetime.strptime(date, "%m/%d/%Y").date()
            name = None  # specific to Etrade
            quantity = decimal.Decimal(quantity)

            if price == 0:
                # specific to ETrade, sometimes price is blank!
                # however, maybe this is the right way to do it always because net includes
                # the option fees that are not included in 'fee'
                price = decimal.Decimal(net) / quantity
            else:
                price = decimal.Decimal(price)
            if fee == "N/A":
                # specific to ETrade
                fee = decimal.Decimal(0)
            else:
                fee = decimal.Decimal(fee)

            if order_type.lower() in OPTION_TRANSACTIONS:
                price = price * SHARES_PER_CONTRACT

            rows.append([date, order_type, symbol, cusip,
                        desc, quantity, price, fee, net])
        rows.sort(key=functools.cmp_to_key(compare_function))

    for index, (date, order_type, symbol, cusip, desc, quantity, price, fee, net) in enumerate(rows):

        is_short_option = order_type.lower() in SHORT_OPTION_TRANSACTIONS

        transaction = Transaction(
            index, date, symbol, is_short_option, name, quantity, price, fee)

        if order_type.lower() in OPEN_LOT_TRANSACTIONS:
            lot = Lot(transaction)
            open_lots[symbol].append(lot)
            logging.debug(f"Added lot: {lot}")
        elif order_type.lower() in CLOSE_LOT_TRANSACTIONS:
            if (fiscal_year == 0) or (fiscal_year == date.year):
                sales[symbol].append(transaction)
            logging.debug(f"Added sale: {transaction}")

    return open_lots, sales
