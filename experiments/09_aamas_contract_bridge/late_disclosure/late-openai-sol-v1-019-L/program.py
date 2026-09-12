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
            "category": "category",
            "amount_cents": np.int64,
        },
        engine="c",
        chunksize=2_000_000,
        keep_default_na=False,
        na_filter=False,
        memory_map=True,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        selected = (accounts % 11) < 7
        if not selected.any():
            continue

        selected_accounts = accounts[selected]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[selected]
        categories = chunk["category"].array[selected]

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs = max(abs(minimum), abs(maximum))

        if len(amounts) * max_abs * 97 <= limit:
            weighted = amounts * ((selected_accounts % 97) + 1)
            grouped = pd.Series(weighted, copy=False).groupby(
                categories, observed=True, sort=False
            ).sum()
            for category, value in grouped.items():
                key = str(category)
                totals[key] = totals.get(key, 0) + int(value)
        else:
            for category, account, amount in zip(
                categories, selected_accounts, amounts
            ):
                key = str(category)
                value = int(amount) * ((int(account) % 97) + 1)
                totals[key] = totals.get(key, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
