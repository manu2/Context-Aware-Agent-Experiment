import json
import sys
import numpy as np
import pandas as pd


def main():
    csv_path = "transactions_secondary.csv"
    totals = {}

    # Process in chunks to maintain low peak memory (<50 MiB)
    # and fast C-engine vectorized throughput.
    chunk_size = 250_000

    try:
        reader = pd.read_csv(
            csv_path,
            usecols=["account_id", "category", "amount_cents"],
            dtype={
                "account_id": np.int64,
                "category": "string",
                "amount_cents": np.int64,
            },
            engine="c",
            chunksize=chunk_size,
        )
    except Exception:
        # Fallback without explicit dtypes if type coercion fails
        reader = pd.read_csv(
            csv_path,
            usecols=["account_id", "category", "amount_cents"],
            engine="c",
            chunksize=chunk_size,
        )

    for chunk in reader:
        acc = chunk["account_id"].to_numpy()
        mask = (acc % 13) < 8
        if not np.any(mask):
            continue

        acc_filtered = acc[mask]
        amt_filtered = chunk["amount_cents"].to_numpy()[mask]
        cat_filtered = chunk["category"].to_numpy()[mask]

        mult = (acc_filtered % 89) + 3

        # Guard against 64-bit overflow if amounts are unusually large
        if np.max(np.abs(amt_filtered)) > 10**14:
            vals = amt_filtered.astype(object) * mult
        else:
            vals = amt_filtered * mult

        s = pd.Series(vals, index=cat_filtered)
        grouped = s.groupby(level=0).sum()

        for cat, val in grouped.items():
            cat_str = str(cat)
            totals[cat_str] = totals.get(cat_str, 0) + int(val)

    # Output formatted as TOTAL:<JSON object> with sorted keys and no whitespace
    json_str = json.dumps(totals, sort_keys=True, separators=(",", ":"))
    sys.stdout.write(f"TOTAL:{json_str}\n")


if __name__ == "__main__":
    main()
