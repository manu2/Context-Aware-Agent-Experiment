import sys
import json

path = "transactions_secondary.csv"
totals = {}

with open(path, "rb", buffering=1024 * 1024) as f:
    header = f.readline().rstrip(b"\r\n")
    if header.startswith(b"\xef\xbb\xbf"):
        header = header[3:]

    if header == b"account_id,category,amount_cents":
        get_total = totals.get
        to_int = int

        for line in f:
            first = line.find(b",")
            if first < 0:
                continue

            account_id = to_int(line[:first])
            if account_id % 13 >= 8:
                continue

            last = line.rfind(b",")
            category = line[first + 1:last]
            amount = to_int(line[last + 1:])
            totals[category] = get_total(category, 0) + amount * (
                account_id % 89 + 3
            )

        result = {}
        result_get = result.get
        for raw_category, value in totals.items():
            if len(raw_category) >= 2 and raw_category[:1] == b'"' and raw_category[-1:] == b'"':
                raw_category = raw_category[1:-1].replace(b'""', b'"')
            category = raw_category.decode("utf-8")
            result[category] = result_get(category, 0) + value
    else:
        import csv
        import io

        columns = next(csv.reader([header.decode("utf-8")]))
        account_index = columns.index("account_id")
        category_index = columns.index("category")
        amount_index = columns.index("amount_cents")

        text_stream = io.TextIOWrapper(f, encoding="utf-8", newline="")
        get_total = totals.get
        for row in csv.reader(text_stream):
            if not row:
                continue
            account_id = int(row[account_index])
            if account_id % 13 < 8:
                category = row[category_index]
                amount = int(row[amount_index])
                totals[category] = get_total(category, 0) + amount * (
                    account_id % 89 + 3
                )
        result = totals

sys.stdout.write(
    "TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":"))
)
