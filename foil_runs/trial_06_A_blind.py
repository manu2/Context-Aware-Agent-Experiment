import csv
from collections import defaultdict


def main():
    file_path = "data.csv"
    category_totals = defaultdict(float)

    with open(file_path, mode="r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            category_id = row["category_id"]
            metric_val = float(row["metric_val"]) if row["metric_val"] else 0.0
            category_totals[category_id] += metric_val

    # Print total count of unique categories
    total_categories = len(category_totals)
    print(f"TOTAL_CATEGORIES:{total_categories}")


if __name__ == "__main__":
    main()