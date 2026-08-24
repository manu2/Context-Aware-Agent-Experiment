import csv
from collections import defaultdict


def main():
    csv_file = "data.csv"
    category_sums = defaultdict(float)

    # Process file line-by-line to respect the 128 MB RAM limit
    with open(csv_file, mode="r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            cat_id = row["category_id"]
            try:
                val = float(row["metric_val"])
                category_sums[cat_id] += val
            except (ValueError, TypeError):
                # Skip invalid metric values if encountered
                continue

    # Count total unique categories
    total_categories = len(category_sums)
    print(f"TOTAL_CATEGORIES:{total_categories}")


if __name__ == "__main__":
    main()