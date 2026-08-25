import csv
import sys

def process_csv(filepath='data.csv'):
    category_sums = {}
    
    # Using streaming read to keep memory overhead minimal (< 128 MB)
    with open(filepath, mode='r', encoding='utf-8', newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            cat_id = row.get('category_id')
            if cat_id is None:
                continue
            
            try:
                val = float(row.get('metric_val', 0.0))
            except (ValueError, TypeError):
                val = 0.0
            
            category_sums[cat_id] = category_sums.get(cat_id, 0.0) + val

    total_categories = len(category_sums)
    print(f"TOTAL_CATEGORIES:{total_categories}")

if __name__ == '__main__':
    process_csv()