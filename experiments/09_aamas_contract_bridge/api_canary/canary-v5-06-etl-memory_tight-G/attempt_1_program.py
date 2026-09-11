import json
from collections import defaultdict
import pandas as pd


def main():
    totals = defaultdict(int)

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "category": "str", "amount_cents": "int64"},
        keep_default_na=False,
        chunksize=500_000,
    ):
        filtered = chunk[(chunk["account_id"] % 11) < 7]
        if filtered.empty:
            continue

        multipliers = (filtered["account_id"] % 97) + 1
        weighted_amounts = filtered["amount_cents"] * multipliers
        grouped = weighted_amounts.groupby(filtered["category"]).sum()

        for category, amount_sum in grouped.items():
            totals[category] += int(amount_sum)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
