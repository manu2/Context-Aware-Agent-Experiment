import json
import pandas as pd

df = pd.read_csv("transactions_secondary.csv")
mask = (df["account_id"] % 13) < 8
sub = df[mask]

cats = sub["category"].tolist()
aids = sub["account_id"].tolist()
amts = sub["amount_cents"].tolist()

totals = {}
for cat, aid, amt in zip(cats, aids, amts):
    val = amt * ((aid % 89) + 3)
    totals[cat] = totals.get(cat, 0) + val

print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")
