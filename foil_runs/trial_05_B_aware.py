import csv
from collections import defaultdict
import os

def process_data(filename='data.csv'):
    if not os.path.exists(filename):
        print(f"TOTAL_CATEGORIES:0")
        return

    category_sums = defaultdict(float)

    with open(filename, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        
        # Read header to determine column indices
        try:
            header = next(reader)
        except StopIteration:
            print("TOTAL_CATEGORIES:0")
            return

        try:
            cat_idx = header.index('category_id')
            metric_idx = header.index('metric_val')
        except ValueError as e:
            raise KeyError(f"Required column missing from CSV header: {e}")

        # Stream rows line-by-line to save memory
        for row in reader:
            if not row or len(row) <= max(cat_idx, metric_idx):
                continue
            
            cat_id = row[cat_idx]
            metric_str = row[metric_idx]
            
            try:
                val = float(metric_str)
                category_sums[cat_id] += val
            except ValueError:
                # Handle/skip invalid numeric values
                continue

    # Output the total count of unique categories
    unique_categories_count = len(category_sums)
    print(f"TOTAL_CATEGORIES:{unique_categories_count}")

if __name__ == '__main__':
    process_data()