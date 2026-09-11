import json

import numpy as np
import pandas as pd


def main():
    totals = {}
    limit = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": np.int64,
            "category": str,
            "amount_cents": np.int64,
        },
        chunksize=1_000_000,
        na_filter=False,
        memory_map=True,
    )

    for chunk in reader:
        account_ids = chunk["account_id"].to_numpy(copy=False)
        mask = (account_ids % 11) < 7
        if not mask.any():
            continue

        selected_ids = account_ids[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].to_numpy(copy=False)[mask]
        factors = (selected_ids % 97) + 1

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs = max(abs(minimum), abs(maximum))
        safe = max_abs * int(factors.max()) * len(amounts) <= limit

        if safe:
            weighted = amounts * factors
            grouped = pd.Series(weighted, copy=False).groupby(
                categories, sort=False
            ).sum()
            for category, subtotal in grouped.items():
                totals[category] = totals.get(category, 0) + int(subtotal)
        else:
            for category, amount, factor in zip(categories, amounts, factors):
                totals[category] = (
                    totals.get(category, 0) + int(amount) * int(factor)
                )

    print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
