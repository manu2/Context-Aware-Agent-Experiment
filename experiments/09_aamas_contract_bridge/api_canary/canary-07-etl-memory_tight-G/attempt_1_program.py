import csv
import json
from collections import defaultdict


def main():
    totals = defaultdict(int)
    with open("transactions.csv", "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header:
            print("TOTAL:{}")
            return

        cat_idx = header.index("category")
        amt_idx = header.index("amount_cents")

        for row in reader:
            if row:
                totals[row[cat_idx]] += int(row[amt_idx])

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
