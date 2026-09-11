import csv
import json
from collections import defaultdict


def main():
    category_totals = defaultdict(int)

    with open(
        "transactions_secondary.csv", mode="r", newline="", encoding="utf-8"
    ) as f:
        reader = csv.DictReader(f)
        for row in reader:
            account_id = int(row["account_id"])
            if account_id % 13 < 8:
                amount_cents = int(row["amount_cents"])
                multiplier = (account_id % 89) + 3
                category_totals[row["category"]] += amount_cents * multiplier

    print(f"TOTAL:{json.dumps(category_totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
