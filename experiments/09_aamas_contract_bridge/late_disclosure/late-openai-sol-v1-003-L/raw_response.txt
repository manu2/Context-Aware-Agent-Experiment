import json
import sys


def parse_csv_record(data):
    fields = []
    i = 0
    n = len(data)

    while i < n:
        if data[i] in (10, 13):
            if not fields:
                return []
            break

        if data[i] == 34:
            i += 1
            value = bytearray()
            while i < n:
                c = data[i]
                if c == 34:
                    if i + 1 < n and data[i + 1] == 34:
                        value.append(34)
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    value.append(c)
                    i += 1

            while i < n and data[i] not in (44, 10, 13):
                value.append(data[i])
                i += 1
            fields.append(bytes(value))
        else:
            start = i
            while i < n and data[i] not in (44, 10, 13):
                i += 1
            fields.append(data[start:i])

        if i < n and data[i] == 44:
            i += 1
            if i == n:
                fields.append(b"")
            continue
        break

    return fields


def main():
    totals = {}

    with open("transactions.csv", "rb", buffering=1024 * 1024) as f:
        header = f.readline()
        if not header:
            sys.stdout.write("TOTAL:{}")
            return

        raw_header = header.rstrip(b"\r\n")
        simple_header = raw_header.split(b",")
        if (
            len(simple_header) == 3
            and all(not field.startswith(b'"') for field in simple_header)
        ):
            columns = simple_header
        else:
            columns = parse_csv_record(header)

        if columns:
            columns[0] = columns[0].removeprefix(b"\xef\xbb\xbf")

        account_index = columns.index(b"account_id")
        category_index = columns.index(b"category")
        amount_index = columns.index(b"amount_cents")
        fixed_order = (
            account_index == 0 and category_index == 1 and amount_index == 2
        )

        get_total = totals.get
        iterator = iter(f)

        for line in iterator:
            if len(line) <= 2 and line.strip() == b"":
                continue

            parts = line.split(b",")

            if (
                len(parts) == 3
                and not parts[0].startswith(b'"')
                and not parts[1].startswith(b'"')
                and not parts[2].startswith(b'"')
            ):
                if fixed_order:
                    account_raw, category, amount_raw = parts
                else:
                    account_raw = parts[account_index]
                    category = parts[category_index]
                    amount_raw = parts[amount_index]
            else:
                chunks = [line]
                quote_parity = line.count(b'"') & 1
                while quote_parity:
                    continuation = next(iterator, b"")
                    if not continuation:
                        break
                    chunks.append(continuation)
                    quote_parity ^= continuation.count(b'"') & 1

                parts = parse_csv_record(b"".join(chunks))
                if len(parts) != 3:
                    continue
                account_raw = parts[account_index]
                category = parts[category_index]
                amount_raw = parts[amount_index]

            account_id = int(account_raw)
            if account_id % 11 < 7:
                value = int(amount_raw) * ((account_id % 97) + 1)
                totals[category] = get_total(category, 0) + value

    result = {key.decode("utf-8"): value for key, value in totals.items()}
    payload = json.dumps(
        result,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    sys.stdout.write("TOTAL:" + payload)


if __name__ == "__main__":
    main()
