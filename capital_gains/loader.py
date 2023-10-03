"""Loads transactions from a file."""

import collections
import csv
import datetime as dt
import decimal
import logging

from model import Transaction, Lot

# Reads transactions from a csv file.
# To represent the starting portfolio, we need to add some lines with
# purchase transactions to the file. Those will get processed and added as Lots


def load_transactions(filename: str):
    """Returns dictionaries with open lots and sales. The dictionary key are symbols."""

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

            # option transaction, assume 100 shares per contract
            # or move this "logic" to model.py
            if order_type.lower() in [
                "sell to open",
                "option expire",
                "option assignment",
                "buy to close",
            ]:
                price = price * 100

            transaction = Transaction(index, date, symbol, name, (shares), price, fee)

            if order_type.lower() in ["buy", "sell to open"]:
                lot = Lot(transaction)
                open_lots[symbol].append(lot)
                logging.debug(f"Added lot: {lot}")
            elif order_type.lower() in [
                "sale",
                "option expire",
                "option assignment",
                "buy to close",
            ]:
                sales[symbol].append(transaction)
                logging.debug(f"Added sale: {transaction}")

    return open_lots, sales
