import json
from collections import defaultdict
import pandas as pd


def main():
    chunksize = 250_000
    totals = defaultdict(int)

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        chunksize=chunksize,
    ):
        mask = (chunk["account_id"] % 11) < 7
        filtered = chunk[mask]
        if filtered.empty:
            continue

        multiplier = (filtered["account_id"] % 97) + 1
        weighted_amounts = filtered["amount_cents"] * multiplier

        grouped = weighted_amounts.groupby(filtered["category"]).sum()
        for cat, val in grouped.items():
            totals[str(cat)] += int(val)

    result_json = json.dumps(totals, sort_keys=True)
    print(f"TOTAL:{result_json}")


if __name__ == "__main__":
    main()
