import csv
import json
import sys


def main():
    totals = {}

    with open("transactions_secondary.csv", "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)

        account_index = header.index("account_id")
        category_index = header.index("category")
        amount_index = header.index("amount_cents")

        for row in reader:
            account_id = int(row[account_index])
            if account_id % 13 < 8:
                category = row[category_index]
                amount_cents = int(row[amount_index])
                weighted_amount = amount_cents * ((account_id % 89) + 3)
                totals[category] = totals.get(category, 0) + weighted_amount

    result = json.dumps(totals, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("TOTAL:" + result)


if __name__ == "__main__":
    main()
