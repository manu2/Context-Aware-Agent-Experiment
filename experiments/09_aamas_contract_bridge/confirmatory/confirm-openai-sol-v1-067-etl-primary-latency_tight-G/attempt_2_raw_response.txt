import json
import sys

import numpy as np
import pandas as pd


def main() -> None:
    base = 1 << 32
    totals: dict[str, int] = {}

    chunks = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": np.int64,
            "category": str,
            "amount_cents": np.int64,
        },
        chunksize=1_000_000,
        engine="c",
        memory_map=True,
        na_filter=False,
    )

    for chunk in chunks:
        account_ids = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(account_ids, 11) < 7
        if not mask.any():
            continue

        weights = np.remainder(account_ids[mask], 97)
        weights += 1

        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        high, low = np.divmod(amounts, base)
        np.multiply(high, weights, out=high)
        np.multiply(low, weights, out=low)

        frame = pd.DataFrame(
            {
                "category": chunk["category"].to_numpy(copy=False)[mask],
                "_high": high,
                "_low": low,
            },
            copy=False,
        )
        grouped = frame.groupby("category", sort=False)[["_high", "_low"]].sum()

        for category, high_sum, low_sum in grouped.itertuples(name=None):
            value = int(high_sum) * base + int(low_sum)
            totals[category] = totals.get(category, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
