import json
import pandas as pd


def main():
    totals = {}
    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "amount_cents": "int64"},
        chunksize=250000,
    ):
        mask = (chunk["account_id"] % 11) < 7
        sub = chunk[mask]
        if sub.empty:
            continue
        weights = (sub["account_id"] % 97) + 1
        weighted_cents = sub["amount_cents"] * weights
        for cat, val in weighted_cents.groupby(sub["category"]).sum().items():
            totals[cat] = totals.get(cat, 0) + int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
