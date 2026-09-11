import csv
import json

totals = {}

with open("transactions_secondary.csv", "r", encoding="utf-8-sig", newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        account_id = int(row["account_id"])
        if account_id % 13 < 8:
            category = row["category"]
            amount_cents = int(row["amount_cents"])
            weighted_amount = amount_cents * ((account_id % 89) + 3)
            totals[category] = totals.get(category, 0) + weighted_amount

print("TOTAL:" + json.dumps(totals, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
