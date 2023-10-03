"""Constants for capital-gains"""

from enum import Enum

WASHSALE_PERIOD = 30


class TransactionType(str, Enum):
    """Types of Transactions"""

    SELL_TO_OPEN = "sell to open"
    OPTION_EXPIRATION = "option expire"
    OPTION_ASSIGNMENT = "option assignment"
    OPTION_BUY_TO_CLOSE = "buy to close"
