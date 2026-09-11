import json
import sys

import numpy as np
import pandas as pd


def main() -> None:
    totals: dict[str, int] = {}

    chunks = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": str,
            "amount_cents": "int64",
        },
        keep_default_na=False,
        na_filter=False,
        chunksize=500_000,
    )

    for chunk in chunks:
        account_ids = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(account_ids, 11) < 7
        if not mask.any():
            continue

        selected_ids = account_ids[mask]
        weights = (np.remainder(selected_ids, 97) + 1).astype(object)
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask].astype(object)
        products = amounts * weights
        categories = chunk["category"].to_numpy(copy=False)[mask]

        grouped = pd.Series(products).groupby(categories, sort=False).sum()
        for category, subtotal in grouped.items():
            totals[category] = totals.get(category, 0) + int(subtotal)

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
