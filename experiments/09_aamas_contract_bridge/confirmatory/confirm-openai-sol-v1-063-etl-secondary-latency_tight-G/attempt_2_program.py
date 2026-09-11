import json
import sys

import numpy as np
import pandas as pd


MAX_INT64 = np.iinfo(np.int64).max

df = pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={
        "account_id": np.int64,
        "category": "category",
        "amount_cents": np.int64,
    },
    na_filter=False,
    memory_map=True,
)

accounts = df["account_id"].to_numpy(copy=False)
amounts = df["amount_cents"].to_numpy(copy=False)
category_series = df["category"]
category_names = category_series.cat.categories
category_codes = category_series.cat.codes.to_numpy(copy=False)

remainders = np.remainder(accounts, 1157).astype(np.int16, copy=False)
eligible_table = (np.arange(1157) % 13) < 8
selected = eligible_table[remainders]

if np.any(selected):
    values = amounts[selected]
    codes = category_codes[selected]
    factors = (remainders[selected] % 89 + 3).astype(np.int64, copy=False)
else:
    values = np.empty(0, dtype=np.int64)
    codes = np.empty(0, dtype=np.int32)
    factors = np.empty(0, dtype=np.int64)

del df, accounts, amounts, category_codes, remainders, selected

totals_by_code = {}


def add_python_rows(start, end):
    local = {}
    for code, value, factor in zip(
        codes[start:end], values[start:end], factors[start:end]
    ):
        key = int(code)
        local[key] = local.get(key, 0) + int(value) * int(factor)
    for key, value in local.items():
        totals_by_code[key] = totals_by_code.get(key, 0) + value


def aggregate_block(start, end):
    count = end - start
    if count == 0:
        return

    block_values = values[start:end]
    minimum = int(block_values.min())
    maximum = int(block_values.max())
    maximum_abs = max(maximum, -minimum)
    maximum_factor = int(factors[start:end].max())

    if maximum_abs <= MAX_INT64 // (maximum_factor * count):
        products = block_values * factors[start:end]
        grouped = pd.Series(products, copy=False).groupby(
            codes[start:end], sort=False
        ).sum()
        for code, value in grouped.items():
            key = int(code)
            totals_by_code[key] = totals_by_code.get(key, 0) + int(value)
        return

    if count <= 4096:
        add_python_rows(start, end)
        return

    middle = start + count // 2
    aggregate_block(start, middle)
    aggregate_block(middle, end)


aggregate_block(0, len(values))

totals = {
    str(category_names[code]): value
    for code, value in totals_by_code.items()
}

sys.stdout.write(
    "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
