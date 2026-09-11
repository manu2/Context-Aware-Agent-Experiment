import json
import pandas as pd


def main():
    totals = {}

    try:
        reader = pd.read_csv(
            "transactions.csv",
            chunksize=100000,
            usecols=["account_id", "category", "amount_cents"],
            dtype={"category": str},
            keep_default_na=False,
        )

        for chunk in reader:
            mask = (chunk["account_id"] % 11) < 7
            if not mask.any():
                continue

            sub = chunk.loc[mask]
            weights = (sub["account_id"] % 97) + 1

            # Convert to Python object arithmetic to prevent 64-bit integer overflow
            contrib = sub["amount_cents"].astype(object) * weights.astype(object)
            chunk_totals = contrib.groupby(sub["category"]).sum()

            for cat, val in chunk_totals.items():
                totals[cat] = totals.get(cat, 0) + int(val)

    except pd.errors.EmptyDataError:
        pass

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == "__main__":
    main()
