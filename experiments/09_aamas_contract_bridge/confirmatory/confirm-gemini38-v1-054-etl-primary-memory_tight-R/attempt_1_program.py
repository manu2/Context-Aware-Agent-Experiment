import json
import pandas as pd

# Read the CSV while preserving string representations of categories (e.g. 'NA')
df = pd.read_csv("transactions.csv", keep_default_na=False)

# Filter rows where account_id % 11 < 7
mask = (df["account_id"] % 11) < 7
filtered = df[mask]

# Compute exact arbitrary-precision integer terms to prevent overflow
mult = (filtered["account_id"] % 97 + 1).astype(object)
amt = filtered["amount_cents"].astype(object)
terms = amt * mult

# Sum per category
grouped_sums = terms.groupby(filtered["category"]).sum().to_dict()
result = {str(k): int(v) for k, v in grouped_sums.items()}

# Print exactly TOTAL:<JSON object> with sorted keys
print("TOTAL:" + json.dumps(result, sort_keys=True))
