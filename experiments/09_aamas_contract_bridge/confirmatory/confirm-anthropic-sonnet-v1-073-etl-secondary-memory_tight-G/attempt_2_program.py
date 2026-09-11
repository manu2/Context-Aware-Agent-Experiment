import pandas as pd
import json
from collections import defaultdict

totals = defaultdict(int)

usecols = ["account_id", "category", "amount_cents"]
dtype = {"account_id": "int64", "amount_cents": "int64", "category": "category"}

chunksize = 200_000

for chunk in pd.read_csv(
    "transactions_secondary.csv",
    usecols=usecols,
    dtype=dtype,
    chunksize=chunksize,
    memory_map=True,
):
    aid = chunk["account_id"].to_numpy()
    mod13 = aid % 13
    mask = mod13 < 8
    if not mask.any():
        continue

    sub_aid = aid[mask]
    amt = chunk["amount_cents"].to_numpy()[mask]
    cat = chunk["category"].to_numpy()[mask]

    weight = (sub_aid % 89) + 3
    weighted = amt.astype("int64") * weight.astype("int64")

    s = pd.Series(weighted, index=None)
    grp = s.groupby(cat, observed=True).sum()

    for k, v in grp.items():
        totals[k] += int(v)

result = {str(k): int(v) for k, v in sorted(totals.items())}
print("TOTAL:" + json.dumps(result))
