import json
from collections import defaultdict
import numpy as np
import pandas as pd


def main():
    totals = defaultdict(int)
    chunksize = 500_000

    for chunk in pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": np.int64, "amount_cents": np.int64},
        chunksize=chunksize,
    ):
        mask = (chunk["account_id"] % 13) < 8
        if not mask.any():
            continue

        filtered = chunk[mask]
        multiplier = (filtered["account_id"] % 89) + 3

        # Guard against potential int64 overflow on multiplication
        if filtered["amount_cents"].abs().max() > 10**16:
            prod = filtered["amount_cents"].astype(object) * multiplier.astype(object)
        else:
            prod = filtered["amount_cents"] * multiplier

        chunk_totals = prod.groupby(filtered["category"], observed=True).sum()
        for cat, val in chunk_totals.items():
            totals[str(cat)] += int(val)

    result_json = json.dumps(totals, sort_keys=True)
    print(f"TOTAL:{result_json}")


if __name__ == "__main__":
    main()
