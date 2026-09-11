import json
import pandas as pd


def main():
    df = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"category": str},
        keep_default_na=False,
    )

    # Filter rows where account_id % 11 < 7
    mask = (df["account_id"] % 11) < 7
    df = df[mask]

    if df.empty:
        print("TOTAL:{}")
        return

    # Compute weights: ((account_id % 97) + 1)
    weights = (df["account_id"] % 97) + 1

    # Convert to Python object integers to ensure exact arbitrary-precision sums
    df["val"] = df["amount_cents"].astype(object) * weights.astype(object)

    grouped = df.groupby("category", sort=True)["val"].sum()
    result = {str(k): int(v) for k, v in grouped.items()}

    print(f"TOTAL:{json.dumps(result, sort_keys=True)}")


if __name__ == "__main__":
    main()
