import csv
from collections import defaultdict
import json


def main():
    totals = defaultdict(int)
    with open("transactions.csv", "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_map = {col.strip(): i for i, col in enumerate(header)}
        cat_idx = col_map["category"]
        amt_idx = col_map["amount_cents"]

        for row in reader:
            if row:
                totals[row[cat_idx]] += int(row[amt_idx])

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
