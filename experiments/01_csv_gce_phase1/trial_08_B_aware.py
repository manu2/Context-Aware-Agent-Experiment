import csv


def process_csv(file_path):
    category_sums = {}

    with open(file_path, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            print("TOTAL_CATEGORIES:0")
            return

        try:
            cat_idx = header.index("category_id")
            val_idx = header.index("metric_val")
        except ValueError:
            cat_idx = 0
            val_idx = 1

        for row in reader:
            if len(row) > max(cat_idx, val_idx):
                cat = row[cat_idx]
                try:
                    val = float(row[val_idx])
                    category_sums[cat] = category_sums.get(cat, 0.0) + val
                except ValueError:
                    continue

    print(f"TOTAL_CATEGORIES:{len(category_sums)}")


if __name__ == "__main__":
    process_csv("data.csv")