import csv
import json
import sys

def main():
    totals = {}

    with open("transactions.csv", "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)

        account_index = header.index("account_id")
        category_index = header.index("category")
        amount_index = header.index("amount_cents")

        for row in reader:
            account_id = int(row[account_index])
            if account_id % 11 < 7:
                category = row[category_index]
                value = int(row[amount_index]) * ((account_id % 97) + 1)
                totals[category] = totals.get(category, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(
            totals,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    )

if __name__ == "__main__":
    main()
