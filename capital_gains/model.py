"""Defines Transactions and Lots"""

from dataclasses import dataclass
from dataclasses import replace
import datetime
import decimal


@dataclass(frozen=True)
class Transaction(object):
    """Represents one transaction."""

    index: int
    date: datetime.datetime
    symbol: str
    is_option: bool
    name: str
    shares: decimal.Decimal
    price: decimal.Decimal
    fee: decimal.Decimal

    def split(self, shares):
        """Splits the transaction in two."""
        first = replace(self, shares=shares, fee=self.fee * shares / self.shares)

        second = replace(
            self, shares=self.shares - first.shares, fee=self.fee - first.fee
        )

        return first, second


# Mutable! `adjustment`, `sale`, and `wash_sale` are assigned in main logic
@dataclass
class Lot(object):
    """Represents a taxable lot."""

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
        """Returns the cost basis."""
        if self.purchase.is_option:
            c = self.shares * self.purchase.price - self.purchase.fee + self.adjustment
        else:
            c = self.shares * self.purchase.price + self.purchase.fee + self.adjustment
        return c

    @property
    def proceeds(self):
        """Returns the proceeds from the sale."""
        if self.sale is None:
            return None
        if self.purchase.is_option:
            p = self.shares * self.sale.price + self.sale.fee
        else:
            p = self.shares * self.sale.price - self.sale.fee
        return p

    @property
    def gain(self):
        """Returns the gain"""
        if self.proceeds is None:
            return None
        if self.purchase.is_option:
            g = self.cost_basis - self.proceeds + self.wash_sale
        else:
            g = self.proceeds - self.cost_basis + self.wash_sale
        return g

    def split(self, shares):
        """Splits the Lot into two Lots."""
        first_purchase, second_purchase = self.purchase.split(shares)

        first_lot = Lot(
            purchase=first_purchase, adjustment=self.adjustment * shares / self.shares
        )

        second_lot = Lot(
            purchase=second_purchase, adjustment=self.adjustment - first_lot.adjustment
        )

        return first_lot, second_lot
