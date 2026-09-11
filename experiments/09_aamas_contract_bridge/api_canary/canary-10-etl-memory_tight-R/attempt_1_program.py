import csv
import json
from collections import defaultdict

def main():
    totals = defaultdict(int)
    with open('transactions.csv', mode='r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            totals[row['category']] += int(row['amount_cents'])

    print(f"TOTAL:{json.dumps(totals, sort_keys=True)}")

if __name__ == '__main__':
    main()
