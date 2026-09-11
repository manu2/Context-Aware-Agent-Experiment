import pandas as pd
import json
import sys

def main():
    df = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "category": "category", "amount_cents": "int64"},
        engine="c",
    )

    acc = df["account_id"].to_numpy()
    mod13 = acc % 13
    mask = mod13 < 8

    if not mask.any():
        print("TOTAL:" + json.dumps({}))
        return

    acc_f = acc[mask]
    amt_f = df["amount_cents"].to_numpy()[mask]
    cat_f = df["category"].to_numpy()[mask]

    multiplier = (acc_f % 89) + 3
    values = amt_f * multiplier

    result_series = pd.Series(values).groupby(cat_f, sort=False).sum()
    result = {str(k): int(v) for k, v in result_series.items()}

    sorted_result = dict(sorted(result.items()))
    sys.stdout.write("TOTAL:" + json.dumps(sorted_result))

if __name__ == "__main__":
    main()
