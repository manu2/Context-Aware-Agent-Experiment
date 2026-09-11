import csv
import json
from collections import defaultdict


def main():
    totals = defaultdict(int)

    with open("transactions.csv", mode="r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_indices = {col.strip(): idx for idx, col in enumerate(header)}

        idx_acc = col_indices["account_id"]
        idx_cat = col_indices["category"]
        idx_amt = col_indices["amount_cents"]

        for row in reader:
            if not row:
                continue
            account_id = int(row[idx_acc])
            if account_id % 11 < 7:
                category = row[idx_cat]
                amount = int(row[idx_amt])
                weight = (account_id % 97) + 1
                totals[category] += amount * weight

    print("TOTAL:" + json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
