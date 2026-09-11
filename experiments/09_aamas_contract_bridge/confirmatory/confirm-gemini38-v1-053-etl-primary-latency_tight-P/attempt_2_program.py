import json
import numpy as np
import pandas as pd


def main():
    df = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": np.int64, "category": str, "amount_cents": np.int64},
        keep_default_na=False,
        memory_map=True,
    )

    mask = (df["account_id"] % 11) < 7
    filtered_acc = df.loc[mask, "account_id"]
    filtered_amt = df.loc[mask, "amount_cents"]
    filtered_cat = df.loc[mask, "category"]

    weights = (filtered_acc % 97) + 1
    weighted_amounts = filtered_amt * weights

    res = weighted_amounts.groupby(filtered_cat).sum()
    output_dict = {str(k): int(v) for k, v in res.items()}

    print(f"TOTAL:{json.dumps(output_dict, sort_keys=True)}")


if __name__ == "__main__":
    main()
