import json
import os
import sys
from collections import defaultdict
import pandas as pd


def main():
    csv_path = "transactions.csv"
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        print("TOTAL:{}")
        return

    totals = defaultdict(int)

    try:
        reader = pd.read_csv(
            csv_path,
            usecols=["category", "amount_cents"],
            dtype={"category": str},
            keep_default_na=False,
            chunksize=500_000,
        )
        for chunk in reader:
            if chunk.empty:
                continue
            grouped = chunk.groupby("category", sort=False)["amount_cents"].sum()
            for cat, amt in grouped.items():
                totals[str(cat)] += int(amt)
    except pd.errors.EmptyDataError:
        print("TOTAL:{}")
        return

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
