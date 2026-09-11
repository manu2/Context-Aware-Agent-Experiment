import json
import sys

import numpy as np
import pandas as pd


def main():
    totals = {}
    int64_max = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "category",
            "amount_cents": "int64",
        },
        chunksize=2_000_000,
        engine="c",
        memory_map=True,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(accounts, 13) < 8

        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        weights = np.remainder(selected_accounts, 89) + 3
        count = amounts.size

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))
        max_weight = int(weights.max())

        if max_abs_amount * max_weight * count <= int64_max:
            weighted = amounts * weights
            selected = chunk.loc[mask, ["category"]].copy()
            selected["_weighted"] = weighted
            grouped = selected.groupby(
                "category", observed=True, sort=False
            )["_weighted"].sum()

            for category, value in grouped.items():
                key = str(category)
                totals[key] = totals.get(key, 0) + int(value)
        else:
            categories = chunk["category"].array[mask]
            for category, account, amount in zip(
                categories, selected_accounts, amounts
            ):
                if pd.isna(category):
                    continue
                key = str(category)
                value = int(amount) * ((int(account) % 89) + 3)
                totals[key] = totals.get(key, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
