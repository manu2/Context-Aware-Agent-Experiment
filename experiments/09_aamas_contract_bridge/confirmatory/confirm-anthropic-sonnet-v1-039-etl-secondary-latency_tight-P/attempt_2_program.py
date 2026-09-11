import pandas as pd
import numpy as np
import json

df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": np.int64, "amount_cents": np.int64},
    engine="c",
)

acc = df["account_id"].to_numpy(dtype=np.int64)
amt = df["amount_cents"].to_numpy(dtype=np.int64)
cat = df["category"].to_numpy()

mask = (acc % 13) < 8

acc_m = acc[mask]
amt_m = amt[mask]
cat_m = cat[mask]

mult = (acc_m % 89) + 3
values = amt_m * mult

codes, uniques = pd.factorize(cat_m, sort=False)
sums = np.zeros(len(uniques), dtype=np.int64)
np.add.at(sums, codes, values)

result = {str(u): int(s) for u, s in zip(uniques, sums)}
result = dict(sorted(result.items()))

print("TOTAL:" + json.dumps(result))
