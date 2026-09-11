import csv
import json
from collections import defaultdict


def main():
    totals = defaultdict(int)

    with open("transactions.csv", mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_indices = {name.strip(): idx for idx, name in enumerate(header)}

        acc_idx = col_indices["account_id"]
        cat_idx = col_indices["category"]
        amt_idx = col_indices["amount_cents"]

        for row in reader:
            if not row:
                continue
            acc_id = int(row[acc_idx])
            if acc_id % 11 < 7:
                amt = int(row[amt_idx])
                cat = row[cat_idx]
                totals[cat] += amt * ((acc_id % 97) + 1)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
