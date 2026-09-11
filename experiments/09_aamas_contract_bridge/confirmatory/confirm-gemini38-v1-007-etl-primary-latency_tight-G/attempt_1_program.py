from collections import defaultdict
import json
import pandas as pd


def main():
    totals = defaultdict(int)
    chunksize = 250_000

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "amount_cents": "int64", "category": "str"},
        keep_default_na=False,
        chunksize=chunksize,
    ):
        mask = (chunk["account_id"] % 11) < 7
        if not mask.any():
            continue

        filtered = chunk[mask]
        multiplier = (filtered["account_id"] % 97) + 1
        weighted_cents = filtered["amount_cents"] * multiplier

        grouped = weighted_cents.groupby(filtered["category"]).sum()
        for category, subtotal in grouped.items():
            totals[category] += int(subtotal)

    result_json = json.dumps(totals, sort_keys=True)
    print(f"TOTAL:{result_json}")


if __name__ == "__main__":
    main()
