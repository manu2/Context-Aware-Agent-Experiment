import json
from collections import defaultdict
import pandas as pd
import numpy as np


def main():
    totals = defaultdict(int)
    chunksize = 1_000_000

    for chunk in pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": np.int64,
            "category": "category",
            "amount_cents": np.int64,
        },
        chunksize=chunksize,
    ):
        filtered = chunk[chunk["account_id"] % 13 < 8]
        if filtered.empty:
            continue

        weights = (filtered["account_id"] % 89) + 3
        vals = filtered["amount_cents"] * weights

        sub_totals = vals.groupby(filtered["category"], observed=True).sum()
        for cat, amount_sum in sub_totals.items():
            totals[str(cat)] += int(amount_sum)

    output = f"TOTAL:{json.dumps(totals, sort_keys=True)}"
    print(output)


if __name__ == "__main__":
    main()
