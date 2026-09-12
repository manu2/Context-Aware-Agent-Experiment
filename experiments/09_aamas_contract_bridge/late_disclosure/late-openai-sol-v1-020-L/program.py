import json
import sys

import pandas as pd

totals = {}

reader = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={
        "account_id": "int64",
        "category": "category",
        "amount_cents": "int64",
    },
    chunksize=1_000_000,
    engine="c",
    memory_map=True,
    na_filter=False,
)

for chunk in reader:
    account_ids = chunk["account_id"].to_numpy(copy=False)
    keep = (account_ids % 13) < 8
    if not keep.any():
        continue

    selected_ids = account_ids[keep]
    amounts = chunk["amount_cents"].to_numpy(copy=False)[keep]
    weighted = amounts * ((selected_ids % 89) + 3)
    categories = chunk["category"].array[keep]

    grouped = pd.Series(weighted, copy=False).groupby(
        categories, sort=False, observed=True
    ).sum()

    for category, value in grouped.items():
        totals[category] = totals.get(category, 0) + int(value)

sys.stdout.write(
    "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
