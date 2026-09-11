from collections import defaultdict
import json
import pandas as pd


def main():
    totals = defaultdict(int)

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "str",
            "amount_cents": "int64",
        },
        keep_default_na=False,
        chunksize=250_000,
    ):
        mask = (chunk["account_id"] % 11) < 7
        sub = chunk[mask]
        if sub.empty:
            continue

        mult = (sub["account_id"] % 97) + 1
        vals = sub["amount_cents"] * mult
        for cat, s in vals.groupby(sub["category"]).sum().items():
            totals[cat] += int(s)

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
