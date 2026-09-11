import csv
import json

totals = {}

with open("transactions.csv", "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        account_id = int(row["account_id"])
        if account_id % 11 < 7:
            category = row["category"]
            amount_cents = int(row["amount_cents"])
            weighted_amount = amount_cents * ((account_id % 97) + 1)
            totals[category] = totals.get(category, 0) + weighted_amount

print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))
