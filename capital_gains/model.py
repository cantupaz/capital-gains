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
    is_short_option: bool
    name: str
    quantity: decimal.Decimal
    price: decimal.Decimal
    fee: decimal.Decimal

    def split(self, quantity):
        """Splits the transaction in two."""
        first = replace(self, quantity=quantity,
                        fee=self.fee * quantity / self.quantity)

        second = replace(
            self, quantity=self.quantity - first.quantity, fee=self.fee - first.fee
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
        """Returns index."""
        return self.purchase.index

    @property
    def symbol(self):
        """Returns symbol."""
        return self.purchase.symbol

    @property
    def name(self):
        """Returns the lot's name."""
        return self.purchase.name

    @property
    def quantity(self):
        """Returns the number of securities transacted."""
        return self.purchase.quantity

    @property
    def cost_basis(self):
        """Returns the cost basis."""
        if self.purchase.is_short_option:
            c = self.quantity * self.sale.price + self.sale.fee  # adjustent??
        else:
            c = self.quantity * self.purchase.price + self.purchase.fee + self.adjustment

        return c

    @property
    def proceeds(self):
        """Returns the proceeds from the sale."""
        if self.sale is None:
            return None
        if self.purchase.is_short_option:
            p = self.quantity * self.purchase.price - self.purchase.fee + self.adjustment
        else:
            p = self.quantity * self.sale.price - self.sale.fee
        return p

    @property
    def gain(self):
        """Returns the gain"""
        if self.proceeds is None:
            return None

        return self.proceeds - self.cost_basis + self.wash_sale

    def split(self, quantity):
        """Splits the Lot into two Lots."""
        first_purchase, second_purchase = self.purchase.split(quantity)

        first_lot = Lot(
            purchase=first_purchase, adjustment=self.adjustment * quantity / self.quantity
        )

        second_lot = Lot(
            purchase=second_purchase, adjustment=self.adjustment - first_lot.adjustment
        )

        return first_lot, second_lot
