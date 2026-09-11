import json
import sys

import numpy as np
import pandas as pd

sys.set_int_max_str_digits(0)

totals = {}
max_int64 = np.iinfo(np.int64).max

with pd.read_csv(
    "transactions_secondary.csv",
    usecols=["account_id", "category", "amount_cents"],
    dtype={
        "account_id": "int64",
        "category": "category",
        "amount_cents": "int64",
    },
    keep_default_na=False,
    chunksize=2_000_000,
    memory_map=True,
) as reader:
    for chunk in reader:
        account_ids = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(account_ids, 13) < 8
        count = int(mask.sum())
        if count == 0:
            continue

        selected_ids = account_ids[mask]
        selected_amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        selected_categories = chunk["category"].array[mask]

        minimum_amount = int(selected_amounts.min())
        maximum_amount = int(selected_amounts.max())
        maximum_magnitude = max(abs(minimum_amount), abs(maximum_amount))

        if maximum_magnitude <= max_int64 // 91:
            weights = np.remainder(selected_ids, 89) + 3
            values = selected_amounts * weights

            minimum_value = int(values.min())
            maximum_value = int(values.max())
            maximum_value_magnitude = max(abs(minimum_value), abs(maximum_value))

            if maximum_value_magnitude == 0:
                block_size = count
            else:
                block_size = max(1, max_int64 // maximum_value_magnitude)

            for start in range(0, count, block_size):
                stop = min(start + block_size, count)
                frame = pd.DataFrame(
                    {
                        "category": selected_categories[start:stop],
                        "value": values[start:stop],
                    },
                    copy=False,
                )
                grouped = frame.groupby(
                    "category", sort=False, observed=True
                )["value"].sum()
                for category, value in grouped.items():
                    totals[category] = totals.get(category, 0) + int(value)
        else:
            for account_id, category, amount in zip(
                selected_ids, selected_categories, selected_amounts
            ):
                value = int(amount) * ((int(account_id) % 89) + 3)
                totals[category] = totals.get(category, 0) + value

print("TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":")))
