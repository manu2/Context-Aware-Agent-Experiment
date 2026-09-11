from collections import defaultdict
import csv
import json


def main():
    totals = defaultdict(int)

    with open("transactions.csv", "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print(f"TOTAL:{json.dumps({}, sort_keys=True)}")
            return

        header_clean = [col.strip() for col in header]
        aid_idx = header_clean.index("account_id")
        cat_idx = header_clean.index("category")
        amt_idx = header_clean.index("amount_cents")

        for row in reader:
            if not row:
                continue
            account_id = int(row[aid_idx])
            if account_id % 11 < 7:
                amount_cents = int(row[amt_idx])
                category = row[cat_idx]
                totals[category] += amount_cents * ((account_id % 97) + 1)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
