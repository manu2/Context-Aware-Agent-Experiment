import collections
import csv
import json


def main():
    totals = collections.defaultdict(int)

    with open(
        "transactions_secondary.csv", mode="r", newline="", encoding="utf-8"
    ) as f:
        reader = csv.DictReader(f)
        for row in reader:
            account_id = int(row["account_id"])
            if account_id % 13 < 8:
                amount_cents = int(row["amount_cents"])
                category = row["category"]
                multiplier = (account_id % 89) + 3
                totals[category] += amount_cents * multiplier

    print(f"TOTAL:{json.dumps(dict(totals), sort_keys=True)}")


if __name__ == "__main__":
    main()
