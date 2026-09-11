import json
import sys

import pandas as pd

totals = {}
limit = (1 << 63) - 1

for chunk in pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": str, "amount_cents": "int64"},
    keep_default_na=False,
    chunksize=1_000_000,
):
    account_ids = chunk["account_id"].to_numpy(copy=False)
    mask = (account_ids % 13) < 8
    count = int(mask.sum())
    if count == 0:
        continue

    selected_amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
    maximum_absolute = max(
        int(selected_amounts.max()),
        -int(selected_amounts.min()),
    )
    selected_categories = chunk.loc[mask, "category"]

    if maximum_absolute * 91 * count <= limit:
        factors = (account_ids[mask] % 89) + 3
        weighted = selected_amounts * factors
        grouped = pd.Series(weighted, index=selected_categories.index).groupby(
            selected_categories, sort=False
        ).sum()

        for category, value in grouped.items():
            totals[category] = totals.get(category, 0) + int(value)
    else:
        selected_ids = account_ids[mask]
        for category, account_id, amount in zip(
            selected_categories,
            selected_ids,
            selected_amounts,
        ):
            totals[category] = totals.get(category, 0) + (
                int(amount) * ((int(account_id) % 89) + 3)
            )

sys.stdout.write(
    "TOTAL:"
    + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
