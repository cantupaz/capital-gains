"""Converts a raw transactions file to a format like the one from the ETrade tax center. """

import csv
import datetime as dt

MAP_TRANSACTION_TYPE = {
    "option expiration": "option expire",
    "option assignment": "option assignment",
    "sold to close": "sell to close",
    "sold short": "sell to open",
    "bought to open": "buy open",
    "bought to cover": "buy to close",
    "bought": "buy",
    "sold": "sell",
}

IGNORE_TRANS = ("adjustment", "dividend", "interest",
                "reorganization", "transfer")

OUT_HEADER = ["Trade Date", "Order Type", "Security", "Cusip",
              "Transaction Description", "Quantity", "Executed Price", "Commission", "Net Amount"]


def main():
    in_filename = "transactions-20220101-20231004.csv"
    out_filename = "orders-20220101-20231004.csv"

    with open(in_filename, "r", encoding="utf-8") as in_file:
        reader = csv.DictReader(in_file, delimiter=",")

        next(reader)

        new_file = []
        for line in reader:
            if line["TransactionType"].lower() in IGNORE_TRANS:
                continue

            in_date = dt.datetime.strptime(line["TransactionDate"], "%m/%d/%y")
            out_date = in_date.strftime("%m/%d/%Y")
            new_line = (out_date,
                        MAP_TRANSACTION_TYPE[line["TransactionType"].lower()],
                        line["Symbol"], "",
                        line["Description"],
                        abs(float(line["Quantity"])),
                        line["Price"],
                        line["Commission"],
                        abs(float(line["Amount"]))
                        )
            new_file.append(new_line)

    new_file.sort()

    # write to the output file
    with open(out_filename, 'w', newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(OUT_HEADER)
        writer.writerows(new_file)


if __name__ == "__main__":
    main()
