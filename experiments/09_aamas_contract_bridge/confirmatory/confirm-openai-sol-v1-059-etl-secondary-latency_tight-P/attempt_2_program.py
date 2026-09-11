import json
import sys

import pandas as pd

totals = {}
limit = (1 << 63) - 1

for chunk in pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={
        "account_id": "int64",
        "category": "category",
        "amount_cents": "int64",
    },
    keep_default_na=False,
    chunksize=2_000_000,
):
    accounts = chunk["account_id"].to_numpy(copy=False)
    mask = accounts % 13 < 8
    if not mask.any():
        continue

    selected_accounts = accounts[mask]
    amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
    factors = selected_accounts % 89 + 3
    categories = chunk["category"].array[mask]

    minimum = int(amounts.min())
    maximum = int(amounts.max())
    max_abs_amount = max(abs(minimum), abs(maximum))

    if max_abs_amount * 91 * len(amounts) <= limit:
        weighted = amounts * factors
        grouped = pd.Series(weighted, copy=False).groupby(
            categories, observed=True, sort=False
        ).sum()
        for category, subtotal in grouped.items():
            totals[str(category)] = totals.get(str(category), 0) + int(subtotal)
    else:
        for category, amount, factor in zip(
            categories.tolist(), amounts.tolist(), factors.tolist()
        ):
            key = str(category)
            totals[key] = totals.get(key, 0) + amount * factor

sys.stdout.write(
    "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
