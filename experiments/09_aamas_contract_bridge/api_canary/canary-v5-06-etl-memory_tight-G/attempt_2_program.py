import collections
import json
import pandas as pd


def main():
    totals = collections.defaultdict(int)

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "str",
            "amount_cents": "int64",
        },
        keep_default_na=False,
        chunksize=100_000,
    ):
        filtered = chunk[(chunk["account_id"] % 11) < 7]
        if filtered.empty:
            continue

        weights = (filtered["account_id"] % 97) + 1
        val = filtered["amount_cents"] * weights

        grouped = val.groupby(filtered["category"]).sum()
        for cat, subtotal in grouped.items():
            totals[cat] += int(subtotal)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
