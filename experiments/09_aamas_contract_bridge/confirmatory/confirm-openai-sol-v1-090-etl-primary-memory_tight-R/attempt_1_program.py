import csv
import json
import sys

sys.set_int_max_str_digits(0)

totals = {}

with open("transactions.csv", "r", encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        account_id = int(row["account_id"])
        if account_id % 11 < 7:
            category = row["category"]
            amount_cents = int(row["amount_cents"])
            weighted_amount = amount_cents * ((account_id % 97) + 1)
            totals[category] = totals.get(category, 0) + weighted_amount

sys.stdout.write("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))
