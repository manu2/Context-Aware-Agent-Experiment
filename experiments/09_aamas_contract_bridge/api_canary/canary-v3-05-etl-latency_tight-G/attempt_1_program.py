import json
import pandas as pd


def main():
    category_sums = {}

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["category", "amount_cents"],
        dtype={"category": str, "amount_cents": "int64"},
        keep_default_na=False,
        chunksize=1_000_000,
    ):
        grouped = chunk.groupby("category", observed=False)["amount_cents"].sum()
        for category, amount in grouped.items():
            category_sums[category] = category_sums.get(category, 0) + int(amount)

    print(f"TOTAL:{json.dumps(category_sums, sort_keys=True)}")


if __name__ == "__main__":
    main()
