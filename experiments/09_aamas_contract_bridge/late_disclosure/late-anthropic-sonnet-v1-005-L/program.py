import csv
import json

sums = {}

with open("transactions_secondary.csv", "r", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    idx_account = header.index("account_id")
    idx_category = header.index("category")
    idx_amount = header.index("amount_cents")

    for row in reader:
        if not row:
            continue
        account_id = int(row[idx_account])
        if account_id % 13 < 8:
            category = row[idx_category]
            amount_cents = int(row[idx_amount])
            multiplier = (account_id % 89) + 3
            value = amount_cents * multiplier
            if category in sums:
                sums[category] += value
            else:
                sums[category] = value

result = {k: sums[k] for k in sorted(sums.keys())}
print("TOTAL:" + json.dumps(result))
