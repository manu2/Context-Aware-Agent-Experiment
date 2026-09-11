import csv
from collections import defaultdict
import json


def main():
    totals = defaultdict(int)
    with open("transactions.csv", "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        cat_idx = header.index("category")
        amt_idx = header.index("amount_cents")
        for row in reader:
            if row:
                totals[row[cat_idx]] += int(row[amt_idx])

    print("TOTAL:" + json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
