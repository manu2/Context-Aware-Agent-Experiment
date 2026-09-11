import csv
from collections import defaultdict
import json


def main():
    sums = defaultdict(int)

    with open("transactions_secondary.csv", "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_map = {col.strip(): idx for idx, col in enumerate(header)}

        aid_idx = col_map["account_id"]
        cat_idx = col_map["category"]
        amt_idx = col_map["amount_cents"]

        for row in reader:
            if not row:
                continue
            aid = int(row[aid_idx])
            if aid % 13 < 8:
                mult = (aid % 89) + 3
                amt = int(row[amt_idx])
                sums[row[cat_idx]] += amt * mult

    output = json.dumps(sums, sort_keys=True)
    print(f"TOTAL:{output}")


if __name__ == "__main__":
    main()
