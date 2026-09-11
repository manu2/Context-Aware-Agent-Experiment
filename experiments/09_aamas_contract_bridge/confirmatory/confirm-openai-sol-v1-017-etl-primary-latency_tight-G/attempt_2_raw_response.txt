import json
import sys

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
        keep_default_na=False,
        chunksize=2_000_000,
        memory_map=True,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(accounts, 11) < 7
        if not mask.any():
            continue

        accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].to_numpy(copy=False)[mask]
        factors = np.remainder(accounts, 97) + 1

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))
        max_factor = int(factors.max())

        if len(amounts) * max_abs_amount * max_factor <= limit:
            weighted = amounts * factors
            grouped = pd.Series(weighted, copy=False).groupby(
                categories, sort=False
            ).sum()
            for category, value in grouped.items():
                totals[category] = totals.get(category, 0) + int(value)
        else:
            for category, account, amount in zip(
                categories, accounts, amounts
            ):
                value = int(amount) * ((int(account) % 97) + 1)
                totals[category] = totals.get(category, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
