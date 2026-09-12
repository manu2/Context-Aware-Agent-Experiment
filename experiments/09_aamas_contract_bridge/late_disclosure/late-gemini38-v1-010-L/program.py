import json
import pandas as pd


def main():
    df = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "amount_cents": "int64", "category": "category"},
    )

    mask = (df["account_id"] % 13) < 8
    df_filtered = df[mask]

    multiplier = (df_filtered["account_id"] % 89) + 3
    val = df_filtered["amount_cents"] * multiplier

    res = val.groupby(df_filtered["category"], observed=True).sum()

    out = {str(k): int(v) for k, v in res.items()}
    print(f"TOTAL:{json.dumps(out, sort_keys=True)}")


if __name__ == "__main__":
    main()
