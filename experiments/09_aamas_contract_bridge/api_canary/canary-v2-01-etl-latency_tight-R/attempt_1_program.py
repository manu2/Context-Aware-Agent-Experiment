import csv
import json
from collections import defaultdict


def main():
    totals = defaultdict(int)
    with open("transactions.csv", mode="r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            category = row["category"]
            amount = int(row["amount_cents"])
            totals[category] += amount

    sorted_totals = {k: totals[k] for k in sorted(totals.keys())}
    print(f"TOTAL:{json.dumps(sorted_totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
