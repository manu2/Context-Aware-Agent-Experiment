import json
import sys

PATH = "transactions_secondary.csv"


def emit(totals):
    result = {key.decode("utf-8"): value for key, value in totals.items()}
    sys.stdout.write(
        "TOTAL:" + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )


def fallback():
    import csv

    totals = {}
    with open(
        PATH,
        "r",
        encoding="utf-8-sig",
        newline="",
        buffering=1024 * 1024,
    ) as file:
        reader = csv.reader(file)
        header = next(reader)
        account_index = header.index("account_id")
        category_index = header.index("category")
        amount_index = header.index("amount_cents")

        get = totals.get
        for row in reader:
            account = int(row[account_index])
            if account % 13 < 8:
                category = row[category_index]
                value = int(row[amount_index]) * (account % 89 + 3)
                totals[category] = get(category, 0) + value

    sys.stdout.write(
        "TOTAL:" + json.dumps(totals, sort_keys=True, separators=(",", ":"))
    )


with open(PATH, "rb", buffering=1024 * 1024) as file:
    header = file.readline()
    normalized_header = header.rstrip(b"\r\n")
    if normalized_header.startswith(b"\xef\xbb\xbf"):
        normalized_header = normalized_header[3:]

    if normalized_header != b"account_id,category,amount_cents":
        file.close()
        fallback()
        raise SystemExit

    totals = {}
    get = totals.get
    lines = iter(file)

    for line in lines:
        first_comma = line.find(b",")
        if first_comma < 0:
            continue

        account_raw = line[:first_comma]
        if account_raw.startswith(b'"') and account_raw.endswith(b'"'):
            account_raw = account_raw[1:-1]
        account = int(account_raw)
        selected = account % 13 < 8
        category_start = first_comma + 1

        if category_start < len(line) and line[category_start] == 34:
            record = line
            scan = category_start + 1

            while True:
                quote = record.find(b'"', scan)
                if quote < 0:
                    try:
                        record += next(lines)
                    except StopIteration:
                        raise ValueError("unterminated quoted CSV field")
                    continue

                if quote + 1 >= len(record):
                    try:
                        record += next(lines)
                    except StopIteration:
                        raise ValueError("unterminated quoted CSV field")
                    continue

                following = record[quote + 1]
                if following == 34:
                    scan = quote + 2
                    continue
                if following == 44:
                    break
                scan = quote + 1

            if selected:
                category = record[category_start + 1:quote].replace(b'""', b'"')
                amount_raw = record[quote + 2:].strip()
                if amount_raw.startswith(b'"') and amount_raw.endswith(b'"'):
                    amount_raw = amount_raw[1:-1].replace(b'""', b'"')
                value = int(amount_raw) * (account % 89 + 3)
                totals[category] = get(category, 0) + value
        elif selected:
            last_comma = line.rfind(b",")
            category = line[category_start:last_comma]
            amount_raw = line[last_comma + 1:].strip()
            if amount_raw.startswith(b'"') and amount_raw.endswith(b'"'):
                amount_raw = amount_raw[1:-1].replace(b'""', b'"')
            value = int(amount_raw) * (account % 89 + 3)
            totals[category] = get(category, 0) + value

emit(totals)
