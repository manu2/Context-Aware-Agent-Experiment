import json
from collections import defaultdict
import pandas as pd


def main():
    totals = defaultdict(int)
    chunksize = 500_000

    for chunk in pd.read_csv(
        "transactions_secondary.csv",
        chunksize=chunksize,
        usecols=["account_id", "category", "amount_cents"],
        na_filter=False,
    ):
        mask = (chunk["account_id"] % 13) < 8
        sub = chunk[mask]
        if sub.empty:
            continue

        weights = (sub["account_id"] % 89) + 3
        vals = sub["amount_cents"] * weights
        chunk_sums = vals.groupby(sub["category"]).sum()

        for cat, s in chunk_sums.items():
            totals[cat] += int(s)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
