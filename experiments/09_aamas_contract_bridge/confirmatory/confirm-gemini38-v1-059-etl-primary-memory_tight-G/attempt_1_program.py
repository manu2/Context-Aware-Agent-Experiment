import json
from collections import defaultdict
import pandas as pd


def main():
    totals = defaultdict(int)

    chunk_size = 250_000
    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"category": str},
        keep_default_na=False,
        chunksize=chunk_size,
    ):
        filtered = chunk[chunk["account_id"] % 11 < 7]
        if filtered.empty:
            continue

        mod97_plus1 = (filtered["account_id"] % 97) + 1
        amounts = filtered["amount_cents"]

        # Safeguard against potential 64-bit integer overflow
        if amounts.dtype == object or (
            hasattr(amounts, "abs")
            and (amounts.abs().max() > 90_000_000_000_000_000)
        ):
            weighted = amounts.astype(object) * mod97_plus1.astype(object)
        else:
            weighted = amounts * mod97_plus1

        # Accumulate arbitrary-precision exact sums per category
        for cat, val in (
            weighted.astype(object).groupby(filtered["category"]).sum().items()
        ):
            totals[cat] += val

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
