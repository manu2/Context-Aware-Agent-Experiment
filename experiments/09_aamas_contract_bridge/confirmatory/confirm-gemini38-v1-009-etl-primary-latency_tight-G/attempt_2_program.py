import json
import os
import sys
import numpy as np
import pandas as pd


def main():
    filepath = "transactions.csv"
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print("TOTAL:{}")
        return

    totals = {}
    chunksize = 500_000

    try:
        reader = pd.read_csv(
            filepath,
            usecols=["account_id", "category", "amount_cents"],
            dtype={"account_id": "int64", "amount_cents": "int64", "category": "str"},
            keep_default_na=False,
            encoding="utf-8-sig",
            chunksize=chunksize,
        )
    except pd.errors.EmptyDataError:
        print("TOTAL:{}")
        return

    for chunk in reader:
        if chunk.empty:
            continue

        acc = chunk["account_id"].to_numpy()
        mask = (acc % 11) < 7
        if not np.any(mask):
            continue

        sub_acc = acc[mask]
        sub_amt = chunk["amount_cents"].to_numpy()[mask]
        sub_cat = chunk["category"].to_numpy()[mask]

        weights = (sub_acc % 97) + 1

        # Check if int64 sum could potentially overflow within the chunk.
        # Max weight is 97. If theoretical upper bound on chunk sum > 9e18,
        # use Python arbitrary precision objects.
        max_abs_amt = int(np.max(np.abs(sub_amt))) if len(sub_amt) > 0 else 0
        if max_abs_amt * 97 * len(sub_amt) > 9_000_000_000_000_000_000:
            vals = sub_amt.astype(object) * weights.astype(object)
        else:
            vals = sub_amt * weights

        df_sub = pd.DataFrame({"category": sub_cat, "val": vals})
        chunk_sum = df_sub.groupby("category", sort=False)["val"].sum()

        for cat, val in chunk_sum.items():
            totals[cat] = totals.get(cat, 0) + int(val)

    print("TOTAL:" + json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
