import json
import os
from collections import defaultdict
import pandas as pd


def main():
    totals = defaultdict(int)
    file_path = "transactions.csv"

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        try:
            chunk_size = 1_000_000
            for chunk in pd.read_csv(
                file_path,
                usecols=["account_id", "category", "amount_cents"],
                dtype={
                    "account_id": "int64",
                    "category": "str",
                    "amount_cents": "int64",
                },
                keep_default_na=False,
                chunksize=chunk_size,
            ):
                mask = (chunk["account_id"] % 11) < 7
                chunk = chunk[mask]
                if chunk.empty:
                    continue

                weights = (chunk["account_id"] % 97) + 1

                max_amt = chunk["amount_cents"].max()
                min_amt = chunk["amount_cents"].min()
                # Guard against 64-bit integer overflow if amounts are unusually huge
                if max_amt > 10_000_000_000 or min_amt < -10_000_000_000:
                    vals = chunk["amount_cents"].astype(object) * weights.astype(
                        object
                    )
                else:
                    vals = chunk["amount_cents"] * weights

                grouped = vals.groupby(chunk["category"], sort=False).sum()
                for cat, val in grouped.items():
                    totals[cat] += int(val)
        except pd.errors.EmptyDataError:
            pass

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
