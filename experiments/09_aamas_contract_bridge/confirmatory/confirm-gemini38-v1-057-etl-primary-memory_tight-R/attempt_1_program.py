import csv
import json
from collections import defaultdict


def main():
    totals = defaultdict(int)

    with open("transactions.csv", mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_indices = {col.strip(): idx for idx, col in enumerate(header)}
        acc_col = col_indices["account_id"]
        cat_col = col_indices["category"]
        amt_col = col_indices["amount_cents"]

        for row in reader:
            if not row:
                continue
            account_id = int(row[acc_col])
            if account_id % 11 < 7:
                category = row[cat_col]
                amount_cents = int(row[amt_col])
                multiplier = (account_id % 97) + 1
                totals[category] += amount_cents * multiplier

    sorted_totals = {k: totals[k] for k in sorted(totals.keys())}
    print(f"TOTAL:{json.dumps(sorted_totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
