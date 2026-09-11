import csv
import json

totals = {}

with open("transactions.csv", mode="r", newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = [col.strip() for col in next(reader)]
    cat_idx = header.index("category")
    amt_idx = header.index("amount_cents")

    for row in reader:
        if not row:
            continue
        category = row[cat_idx]
        amount = int(row[amt_idx].strip())
        totals[category] = totals.get(category, 0) + amount

print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")
