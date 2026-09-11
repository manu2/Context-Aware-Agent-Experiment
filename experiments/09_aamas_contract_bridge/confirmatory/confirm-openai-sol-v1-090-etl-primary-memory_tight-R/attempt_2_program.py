import json
import sys

import numpy as np
import pandas as pd

MAX_INT64 = (1 << 63) - 1
totals = {}


def add_total(category, value):
    totals[category] = totals.get(category, 0) + int(value)


for chunk in pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": np.int64, "amount_cents": np.int64, "category": str},
    keep_default_na=False,
    chunksize=2_000_000,
    memory_map=True,
):
    accounts = chunk["account_id"].to_numpy(copy=False)
    mask = accounts % 11 < 7
    if not np.any(mask):
        continue

    selected_accounts = accounts[mask]
    amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
    categories = chunk["category"].to_numpy(copy=False)[mask]
    weights = selected_accounts % 97 + 1

    minimum = int(amounts.min())
    maximum = int(amounts.max())
    max_abs = max(abs(minimum), abs(maximum))
    max_weight = int(weights.max())

    if max_abs == 0:
        continue

    if max_abs <= MAX_INT64 // max_weight:
        block_size = max(1, MAX_INT64 // (max_abs * max_weight))
        for start in range(0, len(amounts), block_size):
            stop = min(start + block_size, len(amounts))
            products = amounts[start:stop] * weights[start:stop]
            grouped = pd.Series(products).groupby(
                categories[start:stop], sort=False
            ).sum()
            for category, value in grouped.items():
                add_total(category, value)
    else:
        block_size = max(1, MAX_INT64 // max_abs)
        for start in range(0, len(amounts), block_size):
            stop = min(start + block_size, len(amounts))
            frame = pd.DataFrame(
                {
                    "category": categories[start:stop],
                    "weight": weights[start:stop],
                    "amount": amounts[start:stop],
                }
            )
            grouped = frame.groupby(
                ["category", "weight"], sort=False, observed=True
            )["amount"].sum()
            for (category, weight), amount in grouped.items():
                add_total(category, int(amount) * int(weight))

sys.stdout.write(
    "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
