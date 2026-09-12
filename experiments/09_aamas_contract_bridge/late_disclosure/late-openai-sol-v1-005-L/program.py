import csv
import json
import sys

sys.set_int_max_str_digits(0)
csv.field_size_limit(sys.maxsize)

totals = {}

with open(
    "transactions.csv",
    "r",
    encoding="utf-8-sig",
    newline="",
    buffering=1024 * 1024,
) as file:
    reader = csv.reader(file)
    header = next(reader)
    account_idx = header.index("account_id")
    category_idx = header.index("category")
    amount_idx = header.index("amount_cents")
    get_total = totals.get

    if (account_idx, category_idx, amount_idx) == (0, 1, 2):
        for account_text, category, amount_text in reader:
            account_id = int(account_text)
            if account_id % 11 < 7:
                totals[category] = (
                    get_total(category, 0)
                    + int(amount_text) * (account_id % 97 + 1)
                )
    else:
        for row in reader:
            account_id = int(row[account_idx])
            if account_id % 11 < 7:
                category = row[category_idx]
                totals[category] = (
                    get_total(category, 0)
                    + int(row[amount_idx]) * (account_id % 97 + 1)
                )

sys.stdout.write(
    "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
