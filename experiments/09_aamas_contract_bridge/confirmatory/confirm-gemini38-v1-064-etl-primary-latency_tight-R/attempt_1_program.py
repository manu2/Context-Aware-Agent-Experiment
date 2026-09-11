import csv
import json
from collections import defaultdict


def main():
    category_totals = defaultdict(int)

    with open("transactions.csv", mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_map = {col.strip(): idx for idx, col in enumerate(header)}

        acc_idx = col_map["account_id"]
        cat_idx = col_map["category"]
        amt_idx = col_map["amount_cents"]

        for row in reader:
            if not row:
                continue
            account_id = int(row[acc_idx])
            if account_id % 11 < 7:
                category = row[cat_idx]
                amount_cents = int(row[amt_idx])
                multiplier = (account_id % 97) + 1
                category_totals[category] += amount_cents * multiplier

    sorted_result = {k: category_totals[k] for k in sorted(category_totals.keys())}
    print(f"TOTAL:{json.dumps(sorted_result, sort_keys=True)}")


if __name__ == "__main__":
    main()
