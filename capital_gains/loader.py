"""Loads transactions from a file."""

import collections
import csv
import datetime as dt
import decimal
import logging
from model import Transaction, Lot
from const import SHARES_PER_CONTRACT

OPTION_TRANSACTIONS = (
    "buy open",
    "option expire",
    "option assignment",
    "sell to close",
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


# Reads transactions from a csv file.
# To represent the starting portfolio, we need to add some lines with
# purchase transactions to the file. Those will get processed and added as Lots


def load_transactions(filename: str):
    """Returns dictionaries with open lots and sales. The dictionary keys are symbols."""

    open_lots = collections.defaultdict(list)
    sales = collections.defaultdict(list)

    with open(filename, "r", encoding="utf-8") as in_file:
        reader = csv.reader(in_file)

        # Skip header
        next(reader)

        for index, (
            date,
            order_type,
            symbol,
            cusip,
            desc,
            shares,
            price,
            fee,
            net,
        ) in enumerate(reader):
            date = dt.datetime.strptime(date, "%m/%d/%Y").date()
            name = None
            shares = decimal.Decimal(shares)
            price = decimal.Decimal(price)
            if price == 0:
                price = decimal.Decimal(net) / shares
            if fee == "N/A":
                fee = decimal.Decimal(0)
            else:
                fee = decimal.Decimal(fee)

            is_short_option = False
            if order_type.lower() in OPTION_TRANSACTIONS:
                price = price * SHARES_PER_CONTRACT
            if order_type.lower() in SHORT_OPTION_TRANSACTIONS:
                price = price * SHARES_PER_CONTRACT
                is_short_option = True

            transaction = Transaction(
                index, date, symbol, is_short_option, name, shares, price, fee
            )

            if order_type.lower() in OPEN_LOT_TRANSACTIONS:
                lot = Lot(transaction)
                open_lots[symbol].append(lot)
                logging.debug(f"Added lot: {lot}")
            elif order_type.lower() in CLOSE_LOT_TRANSACTIONS:
                sales[symbol].append(transaction)
                logging.debug(f"Added sale: {transaction}")

    return open_lots, sales
