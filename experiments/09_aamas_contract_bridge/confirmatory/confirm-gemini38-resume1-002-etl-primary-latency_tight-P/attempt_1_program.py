import json
import os
import sys
import pandas as pd


def main():
    filepath = "transactions.csv"
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        print("TOTAL:{}")
        return

    df = pd.read_csv(
        filepath,
        usecols=["account_id", "category", "amount_cents"],
        keep_default_na=False,
    )
    df.columns = df.columns.str.strip()

    acc = df["account_id"].astype("int64")
    mask = (acc % 11) < 7
    df = df[mask]

    if df.empty:
        print("TOTAL:{}")
        return

    acc_filt = df["account_id"].astype("int64")
    mult = (acc_filt % 97) + 1

    amt = df["amount_cents"]
    try:
        amt_int = amt.astype("int64")
        max_abs = max(abs(int(amt_int.min())), abs(int(amt_int.max())))
        # Check if 64-bit signed integer cannot overflow
        if max_abs * 97 * len(df) < 9223372036854775800:
            df["val"] = amt_int * mult
            grouped = df.groupby("category", dropna=False)["val"].sum()
            result = {str(k): int(v) for k, v in grouped.items()}
            print(f"TOTAL:{json.dumps(result, sort_keys=True)}")
            return
    except Exception:
        pass

    # Fallback to arbitrary precision Python integers if overflow is possible
    res = {}
    cats = df["category"].tolist()
    acc_list = acc_filt.tolist()
    amt_list = [int(x) for x in df["amount_cents"].tolist()]

    for c, a, m in zip(cats, acc_list, amt_list):
        factor = (a % 97) + 1
        val = m * factor
        c_str = str(c)
        res[c_str] = res.get(c_str, 0) + val

    print(f"TOTAL:{json.dumps(res, sort_keys=True)}")


if __name__ == "__main__":
    main()
