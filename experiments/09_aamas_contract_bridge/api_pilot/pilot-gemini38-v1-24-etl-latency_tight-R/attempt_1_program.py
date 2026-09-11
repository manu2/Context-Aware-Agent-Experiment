import csv
import json
from collections import defaultdict


def main():
    totals = defaultdict(int)

    with open("transactions.csv", mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_map = {col: i for i, col in enumerate(header)}
        aid_idx = col_map["account_id"]
        cat_idx = col_map["category"]
        amt_idx = col_map["amount_cents"]

        for row in reader:
            aid = int(row[aid_idx])
            if aid % 11 < 7:
                amt = int(row[amt_idx])
                cat = row[cat_idx]
                totals[cat] += amt * ((aid % 97) + 1)

    print("TOTAL:" + json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
