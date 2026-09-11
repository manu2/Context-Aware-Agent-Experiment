import json
import pandas as pd


def main():
    totals = {}

    # Stream the file in chunks to bound memory consumption
    # keep_default_na=False ensures string categories like 'NA' or 'null' are preserved
    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["category", "amount_cents"],
        chunksize=250000,
        keep_default_na=False,
        dtype={"category": str},
    ):
        grouped = chunk.groupby("category")["amount_cents"].sum()
        for cat, amt in grouped.items():
            cat_str = str(cat)
            totals[cat_str] = totals.get(cat_str, 0) + int(amt)

    print("TOTAL:" + json.dumps(totals, sort_keys=True))


if __name__ == "__main__":
    main()
