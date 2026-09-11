import csv
import json

totals = {}

with open("transactions.csv", "r", encoding="utf-8", newline="") as file:
    for row in csv.DictReader(file):
        account_id = int(row["account_id"])
        if account_id % 11 < 7:
            category = row["category"]
            amount_cents = int(row["amount_cents"])
            totals[category] = totals.get(category, 0) + amount_cents * (
                account_id % 97 + 1
            )

print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))
