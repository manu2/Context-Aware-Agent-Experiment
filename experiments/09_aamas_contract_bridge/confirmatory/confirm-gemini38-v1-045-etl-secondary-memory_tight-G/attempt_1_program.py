from collections import defaultdict
import json
import pandas as pd


def main():
    totals = defaultdict(int)

    # Process in chunks to balance memory usage and execution speed
    chunk_size = 250_000
    int64_safe_max = 100_000_000_000  # 10^11 cents; chunk sum won't exceed int64

    for chunk in pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "str",
            "amount_cents": "int64",
        },
        keep_default_na=False,
        chunksize=chunk_size,
    ):
        # Filter rows where account_id % 13 < 8
        mask = (chunk["account_id"] % 13) < 8
        sub = chunk[mask]
        if sub.empty:
            continue

        mult = (sub["account_id"] % 89) + 3

        # Guard against potential 64-bit integer overflow for exact arithmetic
        if sub["amount_cents"].abs().max() > int64_safe_max:
            vals = sub["amount_cents"].astype(object) * mult
        else:
            vals = sub["amount_cents"] * mult

        grouped = vals.groupby(sub["category"], sort=False).sum()
        for cat, val in grouped.items():
            totals[cat] += int(val)

    output_json = json.dumps(totals, sort_keys=True)
    print(f"TOTAL:{output_json}")


if __name__ == "__main__":
    main()
