import json
import pandas as pd

def main():
    df = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={"account_id": "int64", "amount_cents": "int64", "category": "str"},
    )

    mask = (df["account_id"].to_numpy() % 11) < 7
    if not mask.any():
        print("TOTAL:{}")
        return

    acc = df["account_id"].to_numpy()[mask]
    amt = df["amount_cents"].to_numpy()[mask]
    cat = df["category"].to_numpy()[mask]

    weight = (acc % 97) + 1
    weighted = amt.astype(object) * weight.astype(object)

    tmp = pd.DataFrame({"category": cat, "weighted": weighted})
    result = tmp.groupby("category")["weighted"].apply(lambda s: sum(s.tolist()))

    out = {str(k): int(v) for k, v in result.items()}
    out = dict(sorted(out.items()))

    print("TOTAL:" + json.dumps(out))

if __name__ == "__main__":
    main()
