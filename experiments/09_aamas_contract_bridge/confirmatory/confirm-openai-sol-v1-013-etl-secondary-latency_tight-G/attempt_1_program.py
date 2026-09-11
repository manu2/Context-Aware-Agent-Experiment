import csv
import json
from collections import defaultdict

totals = defaultdict(int)

with open("transactions_secondary.csv", "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.reader(file)
    header = next(reader)
    account_idx = header.index("account_id")
    category_idx = header.index("category")
    amount_idx = header.index("amount_cents")

    for row in reader:
        account_id = int(row[account_idx])
        if account_id % 13 < 8:
            totals[row[category_idx]] += int(row[amount_idx]) * (
                account_id % 89 + 3
            )

print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))
