import csv
import json
from collections import defaultdict

sums = defaultdict(int)

with open("transactions.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        account_id = int(row["account_id"])
        if account_id % 11 < 7:
            category = row["category"]
            amount_cents = int(row["amount_cents"])
            weight = (account_id % 97) + 1
            sums[category] += amount_cents * weight

result = {k: sums[k] for k in sorted(sums.keys())}
print("TOTAL:" + json.dumps(result))
