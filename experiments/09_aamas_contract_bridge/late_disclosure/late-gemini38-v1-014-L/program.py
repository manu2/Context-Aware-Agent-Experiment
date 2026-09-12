import json
import pandas as pd

df = pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": "category", "amount_cents": "int64"},
    engine="c",
)

mask = (df["account_id"] % 11) < 7
cats = df.loc[mask, "category"]
vals = df.loc[mask, "amount_cents"] * ((df.loc[mask, "account_id"] % 97) + 1)

grouped = vals.groupby(cats, observed=True).sum()
result = {str(k): int(v) for k, v in grouped.items()}

print(f"TOTAL:{json.dumps(result, sort_keys=True)}")
