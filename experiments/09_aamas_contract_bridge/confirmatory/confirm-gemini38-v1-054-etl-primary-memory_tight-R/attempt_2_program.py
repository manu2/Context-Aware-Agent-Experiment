import csv
from collections import defaultdict
import json


def main():
    totals = defaultdict(int)

    with open('transactions.csv', 'r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        col_map = {col.strip(): idx for idx, col in enumerate(header)}
        acc_idx = col_map['account_id']
        cat_idx = col_map['category']
        amt_idx = col_map['amount_cents']

        for row in reader:
            if not row:
                continue
            account_id = int(row[acc_idx])
            if account_id % 11 < 7:
                category = row[cat_idx]
                amount_cents = int(row[amt_idx])
                multiplier = (account_id % 97) + 1
                totals[category] += amount_cents * multiplier

    output_json = json.dumps(totals, sort_keys=True)
    print(f'TOTAL:{output_json}')


if __name__ == '__main__':
    main()
