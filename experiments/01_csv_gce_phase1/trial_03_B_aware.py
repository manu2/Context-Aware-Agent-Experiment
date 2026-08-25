import csv
from collections import defaultdict


def process_csv(filename="data.csv"):
    category_sums = defaultdict(float)

    try:
        with open(filename, mode="r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)

            # Read and parse header
            header = next(reader, None)
            if not header:
                print("TOTAL_CATEGORIES:0")
                return

            header = [col.strip() for col in header]

            try:
                cat_idx = header.index("category_id")
                val_idx = header.index("metric_val")
            except ValueError:
                print("TOTAL_CATEGORIES:0")
                return

            # Process rows line-by-line to minimize RAM usage
            for row in reader:
                if len(row) > max(cat_idx, val_idx):
                    cat_id = row[cat_idx]
                    try:
                        val = float(row[val_idx])
                        category_sums[cat_id] += val
                    except ValueError:
                        # Skip row if metric value is not a valid number
                        continue

    except FileNotFoundError:
        print("TOTAL_CATEGORIES:0")
        return

    # Output total count of unique categories
    total_categories = len(category_sums)
    print(f"TOTAL_CATEGORIES:{total_categories}")


if __name__ == "__main__":
    process_csv()