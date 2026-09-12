import json
import sys

import numpy as np
import pandas as pd


def main():
    df = pd.read_csv(
        "transactions_secondary.csv",
        usecols=["account_id", "category", "amount_cents"],
        dtype={
            "account_id": np.int64,
            "category": "category",
            "amount_cents": np.int64,
        },
        keep_default_na=False,
        na_filter=False,
        engine="c",
    )

    if df.empty:
        print("TOTAL:{}")
        return

    accounts = df["account_id"].to_numpy(copy=False)
    amounts = df["amount_cents"].to_numpy(copy=False)
    categories = df["category"]
    codes = categories.cat.codes.to_numpy(copy=False)
    labels = categories.cat.categories

    selected = np.remainder(accounts, 13) < 8
    selected_count = int(np.count_nonzero(selected))

    if selected_count == 0:
        print("TOTAL:{}")
        return

    selected_codes = np.unique(codes[selected])
    seen = np.zeros(len(labels), dtype=bool)
    seen[selected_codes] = True

    maximum_absolute_amount = max(
        abs(int(amounts.min())),
        abs(int(amounts.max())),
    )
    int64_safe = (
        maximum_absolute_amount * 91 * selected_count
        <= np.iinfo(np.int64).max
    )

    if int64_safe:
        np.remainder(accounts, 89, out=accounts)
        accounts += 3
        amounts *= accounts
        amounts[~selected] = 0

        grouped = df.groupby(
            "category", observed=True, sort=False
        )["amount_cents"].sum()
        grouped_values = {str(key): int(value) for key, value in grouped.items()}
        result = {
            str(labels[code]): grouped_values[str(labels[code])]
            for code in selected_codes
        }
    else:
        sums = [0] * len(labels)
        for index in np.flatnonzero(selected):
            code = int(codes[index])
            account = int(accounts[index])
            amount = int(amounts[index])
            sums[code] += amount * ((account % 89) + 3)

        result = {
            str(labels[code]): sums[code]
            for code in selected_codes
            if seen[code]
        }

    print(
        "TOTAL:"
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )


if __name__ == "__main__":
    main()
