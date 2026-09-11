import csv
import json
from collections import defaultdict


def main():
    totals = defaultdict(int)

    with open('transactions.csv', mode='r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        header = [col.strip() for col in next(reader)]
        
        acc_idx = header.index('account_id')
        cat_idx = header.index('category')
        amt_idx = header.index('amount_cents')

        for row in reader:
            if not row:
                continue
            account_id = int(row[acc_idx])
            if account_id % 11 < 7:
                multiplier = (account_id % 97) + 1
                amount_cents = int(row[amt_idx])
                totals[row[cat_idx]] += amount_cents * multiplier

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")


if __name__ == '__main__':
    main()
