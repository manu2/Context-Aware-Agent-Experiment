import json
import numpy as np
import pandas as pd

CHUNK_SIZE = 2_000_000
INT64_MAX = np.iinfo(np.int64).max
SAFE_AMOUNT_MIN = -((-np.iinfo(np.int64).min) // 97)
SAFE_AMOUNT_MAX = INT64_MAX // 97

totals = {}

reader = pd.read_csv(
    "transactions.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={"account_id": "int64", "category": "object", "amount_cents": "int64"},
    chunksize=CHUNK_SIZE,
    engine="c",
    na_filter=False,
    memory_map=True,
)

for chunk in reader:
    accounts = chunk["account_id"].to_numpy(copy=False)
    mask = np.remainder(accounts, 11) < 7
    if not mask.any():
        continue

    selected_accounts = accounts[mask]
    amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
    categories = chunk["category"].to_numpy(copy=False)[mask]
    factors = np.remainder(selected_accounts, 97) + 1

    amount_min = int(amounts.min())
    amount_max = int(amounts.max())

    use_fast_path = (
        amount_min >= SAFE_AMOUNT_MIN and amount_max <= SAFE_AMOUNT_MAX
    )

    if use_fast_path:
        products = amounts * factors
        product_min = int(products.min())
        product_max = int(products.max())
        max_abs_product = max(abs(product_min), abs(product_max))
        use_fast_path = len(products) * max_abs_product <= INT64_MAX

    if use_fast_path:
        grouped = pd.Series(products, copy=False).groupby(
            categories, sort=False
        ).sum()
        for category, value in grouped.items():
            totals[category] = totals.get(category, 0) + int(value)
    else:
        for category, amount, factor in zip(categories, amounts, factors):
            totals[category] = (
                totals.get(category, 0) + int(amount) * int(factor)
            )

print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))
