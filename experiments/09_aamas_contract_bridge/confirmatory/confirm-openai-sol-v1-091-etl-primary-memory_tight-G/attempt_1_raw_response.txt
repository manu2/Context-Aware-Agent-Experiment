import csv
import json


def main():
    totals = {}

    with open("transactions.csv", "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)
        account_idx = header.index("account_id")
        category_idx = header.index("category")
        amount_idx = header.index("amount_cents")

        for row in reader:
            account_id = int(row[account_idx])
            if account_id % 11 < 7:
                category = row[category_idx]
                weighted_amount = int(row[amount_idx]) * ((account_id % 97) + 1)
                totals[category] = totals.get(category, 0) + weighted_amount

    print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
