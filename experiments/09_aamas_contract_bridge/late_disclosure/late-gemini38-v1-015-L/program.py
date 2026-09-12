import json
import os
import sys
import numpy as np
import pandas as pd


def main():
    csv_file = "transactions.csv"
    if not os.path.exists(csv_file):
        print("TOTAL:{}")
        return

    totals = {}

    # Chunking ensures memory stays well under 512 MiB while maximizing throughput
    chunk_size = 500_000
    reader = pd.read_csv(
        csv_file,
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": np.int64, "amount_cents": np.int64, "category": str},
        chunksize=chunk_size,
    )

    for chunk in reader:
        # Filter rows where account_id % 11 < 7
        mask = (chunk["account_id"] % 11) < 7
        if not mask.any():
            continue

        filtered = chunk[mask]
        multiplier = (filtered["account_id"] % 97) + 1
        vals = filtered["amount_cents"] * multiplier

        grouped = vals.groupby(filtered["category"]).sum()
        for cat, amount in grouped.items():
            totals[cat] = totals.get(cat, 0) + int(amount)

    output = json.dumps(totals, sort_keys=True)
    print(f"TOTAL:{output}")


if __name__ == "__main__":
    main()
