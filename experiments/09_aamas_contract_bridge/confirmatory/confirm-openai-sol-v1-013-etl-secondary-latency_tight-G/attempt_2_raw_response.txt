import json

import numpy as np
import pandas as pd


def main() -> None:
    totals: dict[str, int] = {}
    int64_max = np.iinfo(np.int64).max

    reader = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": np.int64,
            "category": "category",
            "amount_cents": np.int64,
        },
        chunksize=2_000_000,
        memory_map=True,
        keep_default_na=False,
        na_filter=False,
    )

    for chunk in reader:
        accounts = chunk["account_id"].to_numpy(copy=False)
        amounts = chunk["amount_cents"].to_numpy(copy=False)
        categories = chunk["category"].array

        mask = np.remainder(accounts, 13) < 8
        selected_count = int(mask.sum())
        if selected_count == 0:
            continue

        np.remainder(accounts, 89, out=accounts)
        accounts += 3

        selected_amounts = amounts[mask]
        selected_weights = accounts[mask]
        selected_categories = categories[mask]

        minimum = int(selected_amounts.min())
        maximum = int(selected_amounts.max())
        max_abs_amount = max(abs(minimum), abs(maximum))
        max_weight = int(selected_weights.max())

        if max_abs_amount * max_weight * selected_count <= int64_max:
            np.multiply(selected_amounts, selected_weights, out=selected_weights)
            grouped = pd.Series(selected_weights, copy=False).groupby(
                selected_categories,
                observed=True,
                sort=False,
            ).sum()

            for category, value in grouped.items():
                key = str(category)
                totals[key] = totals.get(key, 0) + int(value)
        else:
            for category, amount, weight in zip(
                selected_categories, selected_amounts, selected_weights
            ):
                key = str(category)
                totals[key] = totals.get(key, 0) + int(amount) * int(weight)

    print(
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
