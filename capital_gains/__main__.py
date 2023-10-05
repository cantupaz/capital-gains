"""Calculates capital gains from brokerage transactions."""

import collections
import logging

import argument_parser
import formatter
import loader
import logic


def main():
    parser = argument_parser.get_parser()
    args = parser.parse_args()

    logging.basicConfig(
        format="%(asctime)s: %(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.WARNING,
    )

    open_lots, sales = loader.load_transactions(
        args.filename, args.fiscal_year)
    closed_lots = collections.defaultdict(list)

    for symbol, symbol_sales in sales.items():
        closed_lots[symbol] = logic.process_sales(
            open_lots[symbol], symbol_sales, args.wash_sales
        )

    output = formatter.format(
        closed_lots,
        open_lots,
        args.decimal_places,
        args.shares_decimal_places,
        args.totals,
    )
    print(output)


if __name__ == "__main__":
    main()
