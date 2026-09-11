import pandas as pd
import json
from collections import defaultdict

totals = defaultdict(int)

usecols = ["account_id", "category", "amount_cents"]
dtypes = {"account_id": "int64", "amount_cents": "int64", "category": "category"}

for chunk in pd.read_csv(
    "transactions_secondary.csv",
    usecols=usecols,
    dtype=dtypes,
    chunksize=1_000_000,
):
    aid = chunk["account_id"].to_numpy()
    mask = (aid % 13) < 8
    if not mask.any():
        continue

    sub_aid = aid[mask]
    amt = chunk["amount_cents"].to_numpy()[mask]
    cat = chunk["category"].to_numpy()[mask]

    multiplier = (sub_aid % 89) + 3
    contrib = amt.astype("int64") * multiplier.astype("int64")

    grouped = pd.Series(contrib).groupby(cat, observed=True).sum()

    for k, v in grouped.items():
        totals[k] += int(v)

result = {k: totals[k] for k in sorted(totals.keys())}

print("TOTAL:" + json.dumps(result))
