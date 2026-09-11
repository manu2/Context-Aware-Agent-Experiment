import json
import sys

import numpy as np
import pandas as pd


def main():
    totals = {}
    limit = np.iinfo(np.int64).max
    product_limit = limit // 91

    reader = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "category": str, "amount_cents": "int64"},
        chunksize=1_000_000,
        na_filter=False,
        memory_map=True,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = (accounts % 13) < 8
        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        selected_amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        selected_categories = chunk["category"].to_numpy(copy=False)[mask]

        minimum = int(selected_amounts.min())
        maximum = int(selected_amounts.max())

        if minimum >= -product_limit and maximum <= product_limit:
            weights = (selected_accounts % 89) + 3
            weighted = selected_amounts * weights

            weighted_min = int(weighted.min())
            weighted_max = int(weighted.max())
            max_abs = max(abs(weighted_min), abs(weighted_max))

            if max_abs * len(weighted) <= limit:
                grouped = pd.Series(weighted, copy=False).groupby(
                    selected_categories, sort=False
                ).sum()
                for category, value in grouped.items():
                    totals[category] = totals.get(category, 0) + int(value)
                continue

        for category, account, amount in zip(
            selected_categories, selected_accounts, selected_amounts
        ):
            value = int(amount) * ((int(account) % 89) + 3)
            totals[category] = totals.get(category, 0) + value

    sys.stdout.write(
        "TOTAL:"
        + json.dumps(totals, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    )


if __name__ == "__main__":
    main()
