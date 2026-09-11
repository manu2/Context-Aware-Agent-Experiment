import json
import sys

COMMA = b","
totals = {}

with open("transactions.csv", "rb", buffering=1024 * 1024) as f:
    header = f.readline().rstrip(b"\r\n")
    if header.startswith(b"\xef\xbb\xbf"):
        header = header[3:]

    if header == b"account_id,category,amount_cents":
        get_total = totals.get
        int_ = int

        for line in f:
            if not line.strip():
                continue

            account_raw, category_raw, amount_raw = line.split(COMMA, 2)

            try:
                account_id = int_(account_raw)
            except ValueError:
                value = account_raw.strip()
                account_id = int_(value[1:-1]) if value[:1] == b'"' and value[-1:] == b'"' else int_(value)

            if account_id % 11 >= 7:
                continue

            try:
                amount = int_(amount_raw)
            except ValueError:
                last_comma = line.rfind(COMMA)
                category_raw = line[len(account_raw) + 1:last_comma]
                value = line[last_comma + 1:].strip()
                amount = int_(value[1:-1]) if value[:1] == b'"' and value[-1:] == b'"' else int_(value)

            totals[category_raw] = (
                get_total(category_raw, 0)
                + amount * ((account_id % 97) + 1)
            )
    else:
        import csv

        totals = {}
        with open("transactions.csv", "r", encoding="utf-8-sig", newline="") as text_file:
            reader = csv.reader(text_file)
            columns = next(reader)
            account_index = columns.index("account_id")
            category_index = columns.index("category")
            amount_index = columns.index("amount_cents")

            for row in reader:
                if not row:
                    continue
                account_id = int(row[account_index])
                if account_id % 11 < 7:
                    category = row[category_index]
                    amount = int(row[amount_index])
                    totals[category] = (
                        totals.get(category, 0)
                        + amount * ((account_id % 97) + 1)
                    )

if totals and isinstance(next(iter(totals)), bytes):
    decoded_totals = {}
    for raw_category, value in totals.items():
        if (
            len(raw_category) >= 2
            and raw_category[0] == 34
            and raw_category[-1] == 34
        ):
            raw_category = raw_category[1:-1].replace(b'""', b'"')
        category = raw_category.decode("utf-8")
        decoded_totals[category] = decoded_totals.get(category, 0) + value
    totals = decoded_totals

sys.stdout.write(
    "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
)
