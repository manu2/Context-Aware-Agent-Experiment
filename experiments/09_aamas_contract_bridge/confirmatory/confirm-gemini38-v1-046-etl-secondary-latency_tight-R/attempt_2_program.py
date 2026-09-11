import json
import pandas as pd


def main():
    totals = {}

    for chunk in pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        chunksize=1_000_000,
        engine="c",
    ):
        mask = (chunk["account_id"] % 13) < 8
        filtered = chunk[mask]
        if filtered.empty:
            continue

        mult = (filtered["account_id"] % 89) + 3
        prod = filtered["amount_cents"] * mult

        agg = prod.groupby(filtered["category"]).sum()
        for cat, val in agg.items():
            cat_str = str(cat)
            totals[cat_str] = totals.get(cat_str, 0) + int(val)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
