import json
from collections import defaultdict
import pandas as pd


def main():
    totals = defaultdict(int)

    try:
        reader = pd.read_csv(
            "transactions.csv",
            usecols=["account_id", "category", "amount_cents"],
            dtype={"category": str},
            keep_default_na=False,
            chunksize=500_000,
        )

        for chunk in reader:
            if chunk.empty:
                continue

            mask = (chunk["account_id"] % 11) < 7
            sub = chunk[mask]
            if sub.empty:
                continue

            weights = (sub["account_id"] % 97) + 1
            amt = sub["amount_cents"]

            # Guard against potential 64-bit integer overflow on multiplication
            if amt.dtype == object:
                products = amt * weights.astype(object)
            elif amt.abs().max() > 90_000_000_000_000_000:
                products = amt.astype(object) * weights.astype(object)
            else:
                products = amt * weights

            grouped = products.groupby(sub["category"]).sum()
            for cat, val in grouped.items():
                totals[cat] += int(val)

    except pd.errors.EmptyDataError:
        pass

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
