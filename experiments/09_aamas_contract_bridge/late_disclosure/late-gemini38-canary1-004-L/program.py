import json
from collections import defaultdict
import numpy as np
import pandas as pd


def main():
    totals = defaultdict(int)

    # Process in chunks to stay well within the 512 MiB memory limit
    # while leveraging pandas C-engine parsing speed to beat the 1.4s limit.
    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": np.int64, "amount_cents": np.int64},
        na_filter=False,
        chunksize=250000,
    ):
        acc = chunk["account_id"]
        mask = (acc % 11) < 7
        if not mask.any():
            continue

        filtered = chunk[mask]
        multiplier = (filtered["account_id"] % 97) + 1
        weighted_amounts = filtered["amount_cents"] * multiplier

        agg = weighted_amounts.groupby(filtered["category"]).sum()
        for cat, val in agg.items():
            totals[cat] += int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
