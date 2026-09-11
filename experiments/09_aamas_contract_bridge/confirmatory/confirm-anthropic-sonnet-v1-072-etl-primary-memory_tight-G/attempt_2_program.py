import json
import pandas as pd
import numpy as np

def main():
    totals = {}

    usecols = ["account_id", "category", "amount_cents"]
    dtypes = {"account_id": "int64", "category": "category", "amount_cents": "int64"}

    chunksize = 500_000

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=usecols,
        dtype=dtypes,
        chunksize=chunksize,
        memory_map=True,
    ):
        acc = chunk["account_id"].to_numpy(dtype=np.int64, copy=False)
        mask = (acc % 11) < 7
        if not mask.any():
            continue

        acc_f = acc[mask]
        amt_f = chunk["amount_cents"].to_numpy(dtype=np.int64, copy=False)[mask]
        cat_f = chunk["category"].to_numpy()[mask]

        weight = (acc_f % 97) + 1
        contrib = amt_f * weight

        # Group by category using pandas groupby on a small temp frame
        tmp = pd.DataFrame({"category": cat_f, "contrib": contrib})
        grouped = tmp.groupby("category", observed=True)["contrib"].sum()

        for cat, val in grouped.items():
            cat = str(cat)
            totals[cat] = totals.get(cat, 0) + int(val)

    result = {k: totals[k] for k in sorted(totals.keys())}
    print("TOTAL:" + json.dumps(result))

if __name__ == "__main__":
    main()
