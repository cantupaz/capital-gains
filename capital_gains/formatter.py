import decimal
import itertools


def format(closed_lots, open_lots, decimal_places, shares_decimal_places, totals):
    output = ''

    if closed_lots:
        flattened_closed_lots = list(
            itertools.chain.from_iterable(closed_lots.values()))

        table = tabulate_closed_lots(
            flattened_closed_lots, decimal_places, shares_decimal_places)
        output += f'# Closed lots\n\n{format_table(table)}'

        if totals:
            table = tabulate_closed_totals(
                flattened_closed_lots, decimal_places, shares_decimal_places)
            output += f'\n\n# Closed totals\n\n{format_table(table)}'

    if any(open_lots.values()):
        if closed_lots:
            output += '\n\n'

        flattened_open_lots = list(
            itertools.chain.from_iterable(open_lots.values()))

        table = tabulate_open_lots(
            flattened_open_lots, decimal_places, shares_decimal_places)
        output += f'# Open lots\n\n{format_table(table)}'

        if totals:
            table = tabulate_open_totals(
                flattened_open_lots, decimal_places, shares_decimal_places)
            output += f'\n\n# Open totals\n\n{format_table(table)}'

    return output


def format_decimal(value, decimal_places):
    return str(value.quantize(
        decimal.Decimal('0.1') ** decimal_places, rounding=decimal.ROUND_HALF_UP))


def tabulate_closed_lots(closed_lots, decimal_places, shares_decimal_places):
    # Group parts of lots that were split (e.g. partially adjusted)
    # Only group if sold on the same day, and keep gains and losses separate
    grouped_lots = [list(group) for _, group in itertools.groupby(
        closed_lots, lambda lot: (lot.index, lot.sale.date, lot.proceeds > lot.cost_basis))]

    header = [
        'symbol',
        'name',
        'quantity',
        'acquired',
        'sold',
        'proceeds',
        'cost basis',
        'wash sale',
        'gain']

    return [header] + [
        [
            lots[0].symbol,
            lots[0].name or '',
            format_decimal(sum(lot.quantity for lot in lots),
                           shares_decimal_places),
            str(lots[0].purchase.date),
            str(lots[0].sale.date),
            format_decimal(sum(lot.proceeds for lot in lots), decimal_places),
            format_decimal(sum(lot.cost_basis for lot in lots),
                           decimal_places),
            format_decimal(sum(lot.wash_sale for lot in lots), decimal_places),
            format_decimal(sum(lot.gain for lot in lots), decimal_places)]
        for lots in grouped_lots]


def tabulate_closed_totals(closed_lots, decimal_places, shares_decimal_places):
    grouped_lots = [list(group) for _, group in itertools.groupby(
        closed_lots, lambda lot: (lot.sale.date.year, lot.symbol))]

    table = [['sold', 'symbol', 'quantity',
              'proceeds', 'cost basis', 'wash sale', 'gain']]

    for lots in grouped_lots:
        table += [[
            str(lots[0].sale.date.year),
            lots[0].symbol,
            format_decimal(sum(lot.quantity for lot in lots),
                           shares_decimal_places),
            format_decimal(sum(lot.proceeds for lot in lots), decimal_places),
            format_decimal(sum(lot.cost_basis for lot in lots),
                           decimal_places),
            format_decimal(sum(lot.wash_sale for lot in lots), decimal_places),
            format_decimal(sum(lot.gain for lot in lots), decimal_places)]]

    return table


def tabulate_open_lots(open_lots, decimal_places, shares_decimal_places):
    # Group parts of lots that were split (e.g. partially adjusted)
    grouped_lots = [list(group) for _, group in itertools.groupby(
        open_lots, lambda lot: lot.index)]

    header = ['symbol', 'name', 'quantity', 'acquired', 'cost basis']

    return [header] + [
        [
            lots[0].symbol,
            lots[0].name or '',
            format_decimal(sum(lot.quantity for lot in lots),
                           shares_decimal_places),
            str(lots[0].purchase.date),
            format_decimal(sum(lot.cost_basis for lot in lots), decimal_places)]
        for lots in grouped_lots]


def tabulate_open_totals(open_lots, decimal_places, shares_decimal_places):
    grouped_lots = [list(group) for _, group in itertools.groupby(
        open_lots, lambda lot: lot.symbol)]

    table = [['symbol', 'quantity', 'estimated proceeds',
              'cost basis', 'estimated gain']]

    for lots in grouped_lots:
        total_quantity = sum(lot.quantity for lot in lots)
        estimated_proceeds = total_quantity * lots[-1].purchase.price
        total_cost_basis = sum(lot.cost_basis for lot in lots)
        estimated_gain = estimated_proceeds - total_cost_basis
        table += [[
            lots[0].symbol,
            format_decimal(total_quantity, shares_decimal_places),
            format_decimal(estimated_proceeds, decimal_places),
            format_decimal(total_cost_basis, decimal_places),
            format_decimal(estimated_gain, decimal_places)]]

    return table


def format_table(table):
    widths = [max(map(len, column)) for column in zip(*table)]

    return '\n'.join(
        ' | '.join(
            value.rjust(width)
            for value, width in zip(row, widths))
        for row in table)
