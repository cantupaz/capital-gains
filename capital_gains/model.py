"""Defines Transactions and Lots"""

from dataclasses import dataclass
from dataclasses import replace
import datetime
import decimal


@dataclass(frozen=True)
class Transaction(object):
    """Represents one transaction (sale, purchase)."""

    index: int
    date: datetime.datetime
    symbol: str
    name: str
    shares: decimal.Decimal
    price: decimal.Decimal
    fee: decimal.Decimal

    def split(self, shares):
        first = replace(self, shares=shares, fee=self.fee * shares / self.shares)

        second = replace(
            self, shares=self.shares - first.shares, fee=self.fee - first.fee
        )

        return first, second


# Mutable! `adjustment`, `sale`, and `wash_sale` are assigned in main logic
@dataclass
class Lot(object):
    purchase: Transaction
    adjustment: decimal.Decimal = decimal.Decimal(0)
    sale: Transaction = None
    wash_sale: decimal.Decimal = decimal.Decimal(0)

    @property
    def index(self):
        return self.purchase.index

    @property
    def symbol(self):
        return self.purchase.symbol

    @property
    def name(self):
        return self.purchase.name

    @property
    def shares(self):
        return self.purchase.shares

    @property
    def cost_basis(self):
        if "call" in (self.purchase.symbol.lower()) or (
            "put" in self.purchase.symbol.lower()
        ):
            c = (
                self.shares * self.purchase.price - self.purchase.fee + self.adjustment
            )  # TODO: why neg fee??
        else:
            c = self.shares * self.purchase.price + self.purchase.fee + self.adjustment
        return c

    @property
    def proceeds(self):
        if self.sale is None:
            return None
        if "call" in (self.sale.symbol.lower()) or ("put" in self.sale.symbol.lower()):
            p = self.shares * self.sale.price + self.sale.fee
        else:
            p = self.shares * self.sale.price - self.sale.fee
        return p

    @property
    def gain(self):
        if self.proceeds is None:
            return None
        if "call" in (self.sale.symbol.lower()) or ("put" in self.sale.symbol.lower()):
            g = self.cost_basis - self.proceeds + self.wash_sale
        else:
            g = self.proceeds - self.cost_basis + self.wash_sale  # original
        return g

    def split(self, shares):
        first_purchase, second_purchase = self.purchase.split(shares)

        first_lot = Lot(
            purchase=first_purchase, adjustment=self.adjustment * shares / self.shares
        )

        second_lot = Lot(
            purchase=second_purchase, adjustment=self.adjustment - first_lot.adjustment
        )

        return first_lot, second_lot
