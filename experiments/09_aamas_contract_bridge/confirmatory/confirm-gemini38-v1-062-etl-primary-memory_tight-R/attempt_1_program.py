import csv
from collections import defaultdict
import json


def main():
    totals = defaultdict(int)

    with open('transactions.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        acc_idx = header.index('account_id')
        cat_idx = header.index('category')
        amt_idx = header.index('amount_cents')

        for row in reader:
            if not row:
                continue
            acc_id = int(row[acc_idx])
            if acc_id % 11 < 7:
                multiplier = (acc_id % 97) + 1
                totals[row[cat_idx]] += int(row[amt_idx]) * multiplier

    sorted_totals = dict(sorted(totals.items()))
    print(f"TOTAL:{json.dumps(sorted_totals, sort_keys=True)}")


if __name__ == '__main__':
    main()
