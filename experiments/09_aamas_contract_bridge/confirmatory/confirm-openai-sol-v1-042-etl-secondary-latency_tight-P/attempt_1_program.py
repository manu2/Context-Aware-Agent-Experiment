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
        engine="c",
        na_filter=False,
        chunksize=750_000,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(accounts, 13) < 8
        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].array[mask]
        weights = np.remainder(selected_accounts, 89) + 3

        max_abs_amount = max(
            abs(int(amounts.min())),
            abs(int(amounts.max())),
        )
        safe_bound = max_abs_amount * int(weights.max()) * len(amounts)

        if safe_bound <= int64_max:
            weighted = amounts * weights
            grouped = pd.Series(weighted, copy=False).groupby(
                categories, observed=True, sort=False
            ).sum()

            for category, value in grouped.items():
                key = str(category)
                totals[key] = totals.get(key, 0) + int(value)
        else:
            for category, amount, weight in zip(categories, amounts, weights):
                key = str(category)
                totals[key] = totals.get(key, 0) + int(amount) * int(weight)

    output = json.dumps(totals, sort_keys=True, separators=(",", ":"))
    sys.stdout.write("TOTAL:" + output)


if __name__ == "__main__":
    main()
