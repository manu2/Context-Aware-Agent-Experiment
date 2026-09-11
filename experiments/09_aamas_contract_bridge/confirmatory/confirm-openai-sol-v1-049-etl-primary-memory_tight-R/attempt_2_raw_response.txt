import json
import sys
from collections import defaultdict

import numpy as np
import pandas as pd


def main() -> None:
    totals = defaultdict(int)
    int64_max = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": "category",
            "amount_cents": "int64",
        },
        chunksize=2_000_000,
        engine="c",
        memory_map=True,
        na_filter=False,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = np.remainder(accounts, 11) < 7
        if not mask.any():
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].array[mask]
        factors = np.remainder(selected_accounts, 97) + 1

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))
        max_factor = int(factors.max())

        if max_abs_amount == 0:
            continue

        safe_block_size = int64_max // (max_abs_amount * max_factor)

        if safe_block_size == 0:
            for category, amount, factor in zip(categories, amounts, factors):
                totals[str(category)] += int(amount) * int(factor)
            continue

        block_size = min(len(amounts), safe_block_size)

        for start in range(0, len(amounts), block_size):
            end = min(start + block_size, len(amounts))
            products = amounts[start:end] * factors[start:end]

            block = pd.DataFrame(
                {
                    "category": categories[start:end],
                    "value": products,
                },
                copy=False,
            )
            grouped = block.groupby(
                "category", sort=False, observed=True
            )["value"].sum()

            for category, value in grouped.items():
                totals[str(category)] += int(value)

    output = json.dumps(dict(totals), sort_keys=True, separators=(",", ":"))
    sys.stdout.write("TOTAL:" + output)


if __name__ == "__main__":
    main()
