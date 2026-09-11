import json
import sys

import numpy as np
import pandas as pd


def main() -> None:
    totals: dict[str, int] = {}
    limit = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions_secondary.csv",
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
        mask = (accounts % 13) < 8
        count = int(mask.sum())
        if count == 0:
            continue

        selected_accounts = accounts[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        categories = chunk["category"].array[mask]
        factors = (selected_accounts % 89) + 3

        minimum = int(amounts.min())
        maximum = int(amounts.max())
        max_abs = max(abs(minimum), abs(maximum))

        if max_abs * 91 * count <= limit:
            weighted = amounts * factors
            grouped = (
                pd.Series(weighted, copy=False)
                .groupby(categories, observed=True, sort=False)
                .sum()
            )
            for category, value in grouped.items():
                key = str(category)
                totals[key] = totals.get(key, 0) + int(value)
        else:
            category_values = np.asarray(categories, dtype=object)
            for category, amount, factor in zip(
                category_values, amounts, factors
            ):
                key = str(category)
                totals[key] = (
                    totals.get(key, 0) + int(amount) * int(factor)
                )

    sys.stdout.write(
        "TOTAL:"
        + json.dumps(
            totals,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
    )


if __name__ == "__main__":
    main()
