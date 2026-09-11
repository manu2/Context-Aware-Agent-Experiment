import json
import sys
from collections import defaultdict

import pandas as pd

totals = defaultdict(int)
limit = (1 << 63) - 1

reader = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={
        "account_id": "int64",
        "category": "category",
        "amount_cents": "int64",
    },
    keep_default_na=False,
    chunksize=1_000_000,
    memory_map=True,
)

for chunk in reader:
    account_ids = chunk["account_id"].to_numpy(copy=False)
    mask = (account_ids % 13) < 8
    count = int(mask.sum())

    if count == 0:
        continue

    selected_ids = account_ids[mask]
    amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
    weights = (selected_ids % 89) + 3
    categories = chunk.loc[mask, "category"].array

    minimum = int(amounts.min())
    maximum = int(amounts.max())
    max_abs_amount = max(abs(minimum), abs(maximum))
    max_weight = int(weights.max())

    if max_abs_amount * max_weight * count <= limit:
        products = amounts * weights
        grouped = pd.Series(products, copy=False).groupby(
            categories, observed=True, sort=False
        ).sum()

        for category, value in grouped.items():
            totals[str(category)] += int(value)
    else:
        for category, amount, weight in zip(categories, amounts, weights):
            totals[str(category)] += int(amount) * int(weight)

result = dict(totals)
sys.stdout.write(
    "TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":"))
)
