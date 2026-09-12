import json
import sys

import numpy as np
import pandas as pd


df = pd.read_csv(
    "transactions.csv",
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
mask = (accounts % 11) < 7

selected_accounts = accounts[mask]
selected_amounts = amounts[mask]
codes = df["category"].cat.codes.to_numpy(copy=False)[mask]
categories = df["category"].cat.categories

if selected_amounts.size == 0:
    totals = {}
else:
    lo = int(selected_amounts.min())
    hi = int(selected_amounts.max())
    max_abs_amount = max(abs(lo), abs(hi))
    safe_bound = max_abs_amount * 97 * int(selected_amounts.size)

    if safe_bound <= np.iinfo(np.int64).max:
        weighted = selected_amounts * ((selected_accounts % 97) + 1)
        grouped = pd.Series(weighted, copy=False).groupby(
            codes, sort=False
        ).sum()
        totals = {
            str(categories[int(code)]): int(value)
            for code, value in grouped.items()
        }
    else:
        sums = [0] * len(categories)
        for code, account, amount in zip(
            codes, selected_accounts, selected_amounts
        ):
            sums[int(code)] += int(amount) * ((int(account) % 97) + 1)
        totals = {
            str(categories[code]): total
            for code, total in enumerate(sums)
            if total != 0
        }

sys.stdout.write(
    "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
