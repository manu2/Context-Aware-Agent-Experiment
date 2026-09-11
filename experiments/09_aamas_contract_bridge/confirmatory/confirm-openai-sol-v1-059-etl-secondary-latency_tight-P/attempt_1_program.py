import json
import sys

import numpy as np
import pandas as pd


def main():
    totals = {}
    limit = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"category": str},
        chunksize=500_000,
        engine="c",
        na_filter=False,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)

        if np.issubdtype(accounts.dtype, np.integer):
            mod13 = np.remainder(accounts, 13)
            mask = mod13 < 8
            if not mask.any():
                continue
            multipliers = np.remainder(accounts[mask], 89).astype(np.int64) + 3
        else:
            account_values = accounts.tolist()
            mask = np.fromiter(
                (int(value) % 13 < 8 for value in account_values),
                dtype=bool,
                count=len(account_values),
            )
            if not mask.any():
                continue
            multipliers = np.fromiter(
                (int(value) % 89 + 3 for value, keep in zip(account_values, mask) if keep),
                dtype=np.int64,
                count=int(mask.sum()),
            )

        categories = chunk["category"].to_numpy(copy=False)[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        count = len(amounts)

        safe_int64 = np.issubdtype(amounts.dtype, np.integer)
        if safe_int64:
            low = int(amounts.min())
            high = int(amounts.max())
            max_abs = max(abs(low), abs(high))
            safe_int64 = max_abs * int(multipliers.max()) * count <= limit

        if safe_int64:
            products = amounts.astype(np.int64, copy=False) * multipliers
        else:
            products = np.fromiter(
                (int(amount) * int(multiplier)
                 for amount, multiplier in zip(amounts, multipliers)),
                dtype=object,
                count=count,
            )

        grouped = pd.Series(products, copy=False).groupby(
            categories, sort=False, dropna=False
        ).sum()

        for category, value in grouped.items():
            key = str(category)
            totals[key] = totals.get(key, 0) + int(value)

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
