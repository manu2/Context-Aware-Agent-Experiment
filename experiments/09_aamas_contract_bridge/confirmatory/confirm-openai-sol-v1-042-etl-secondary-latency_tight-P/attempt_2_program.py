import json
import sys

import numpy as np
import pandas as pd


df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={
        "account_id": "int64",
        "category": "category",
        "amount_cents": "int64",
    },
    engine="c",
    na_filter=False,
    memory_map=True,
)

accounts = df["account_id"].to_numpy(copy=False)
amounts = df["amount_cents"].to_numpy(copy=False)
codes = df["category"].cat.codes.to_numpy(copy=False)
categories = df["category"].cat.categories

mask = np.remainder(accounts, 13) < 8
selected_count = int(np.count_nonzero(mask))
totals = {}

if selected_count:
    i64 = np.iinfo(np.int64)
    minimum_amount = int(amounts[mask].min())
    maximum_amount = int(amounts[mask].max())
    product_is_safe = (
        minimum_amount >= i64.min // 91
        and maximum_amount <= i64.max // 91
    )

    if not product_is_safe:
        for index in np.flatnonzero(mask):
            code = int(codes[index])
            value = int(amounts[index]) * ((int(accounts[index]) % 89) + 3)
            totals[code] = totals.get(code, 0) + value
    else:
        np.remainder(accounts, 89, out=accounts)
        accounts += 3
        np.multiply(amounts, accounts, out=amounts)

        values = amounts[mask]
        groups = codes[mask]
        lower = int(values.min())
        upper = int(values.max())
        bound = max(abs(lower), abs(upper))

        if bound == 0 or bound * selected_count <= i64.max:
            grouped = pd.Series(values, copy=False).groupby(
                groups, sort=False
            ).sum()
            totals = {int(code): int(value) for code, value in grouped.items()}
        else:
            chunk_size = max(1, i64.max // bound)
            for start in range(0, selected_count, chunk_size):
                end = min(start + chunk_size, selected_count)
                grouped = pd.Series(
                    values[start:end], copy=False
                ).groupby(groups[start:end], sort=False).sum()
                for code, value in grouped.items():
                    key = int(code)
                    totals[key] = totals.get(key, 0) + int(value)

result = {str(categories[code]): value for code, value in totals.items()}
sys.stdout.write(
    "TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":"))
)
