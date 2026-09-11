import csv
import json
import sys

def main():
    totals = {}

    with open("transactions.csv", "r", encoding="utf-8", newline="", buffering=1024 * 1024) as file:
        reader = csv.reader(file)
        header = next(reader)

        account_idx = header.index("account_id")
        category_idx = header.index("category")
        amount_idx = header.index("amount_cents")

        get_total = totals.get

        for row in reader:
            account_id = int(row[account_idx])
            if account_id % 11 < 7:
                category = row[category_idx]
                value = int(row[amount_idx]) * (account_id % 97 + 1)
                totals[category] = get_total(category, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )

if __name__ == "__main__":
    main()
