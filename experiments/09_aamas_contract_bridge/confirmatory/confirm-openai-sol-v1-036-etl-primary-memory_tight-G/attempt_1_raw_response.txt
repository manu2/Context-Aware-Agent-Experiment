import json
import sys

import pandas as pd


def main() -> None:
    totals: dict[str, int] = {}

    for chunk in pd.read_csv(
        "transactions.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": "int64",
            "category": str,
            "amount_cents": "int64",
        },
        keep_default_na=False,
        chunksize=250_000,
    ):
        accounts = chunk["account_id"].to_numpy(copy=False)
        mask = accounts % 11 < 7

        if not mask.any():
            continue

        categories = chunk["category"].to_numpy(copy=False)[mask]
        amounts = chunk["amount_cents"].to_numpy(copy=False)[mask]
        weights = accounts[mask] % 97 + 1

        for category, amount, weight in zip(categories, amounts, weights):
            totals[category] = (
                totals.get(category, 0) + int(amount) * int(weight)
            )

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
