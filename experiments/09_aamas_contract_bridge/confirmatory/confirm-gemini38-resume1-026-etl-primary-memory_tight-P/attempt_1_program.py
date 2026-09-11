import csv
import json
from collections import defaultdict


def main():
    sums = defaultdict(int)

    with open(
        "transactions.csv", "r", newline="", encoding="utf-8-sig", buffering=1048576
    ) as f:
        reader = csv.reader(f)
        header = next(reader)
        col_map = {name.strip(): idx for idx, name in enumerate(header)}

        acc_idx = col_map["account_id"]
        cat_idx = col_map["category"]
        amt_idx = col_map["amount_cents"]

        for row in reader:
            if not row:
                continue
            acc_id = int(row[acc_idx])
            if acc_id % 11 < 7:
                amt = int(row[amt_idx])
                cat = row[cat_idx]
                sums[cat] += amt * ((acc_id % 97) + 1)

    print(f"TOTAL:{json.dumps(sums, sort_keys=True)}")


if __name__ == "__main__":
    main()
