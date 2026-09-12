import json
import sys


def parse_csv_record(data):
    fields = []
    field = bytearray()
    in_quotes = False
    at_field_start = True
    i = 0
    n = len(data)

    while i < n:
        ch = data[i]

        if in_quotes:
            if ch == 34:
                if i + 1 < n and data[i + 1] == 34:
                    field.append(34)
                    i += 2
                else:
                    in_quotes = False
                    i += 1
            else:
                field.append(ch)
                i += 1
        else:
            if ch == 44:
                fields.append(bytes(field))
                field.clear()
                at_field_start = True
                i += 1
            elif ch == 34 and at_field_start:
                in_quotes = True
                at_field_start = False
                i += 1
            elif ch == 10 or ch == 13:
                fields.append(bytes(field))
                return fields, True
            else:
                field.append(ch)
                at_field_start = False
                i += 1

    if in_quotes:
        return None, False

    fields.append(bytes(field))
    return fields, True


def read_record(first_part, readline):
    data = first_part
    while True:
        fields, complete = parse_csv_record(data)
        if complete:
            return fields
        continuation = readline()
        if not continuation:
            return parse_csv_record(data)[0] or []
        data += continuation


def remove_eol(line):
    if line.endswith(b"\n"):
        line = line[:-1]
        if line.endswith(b"\r"):
            line = line[:-1]
    elif line.endswith(b"\r"):
        line = line[:-1]
    return line


def main():
    totals = {}

    with open("transactions.csv", "rb", buffering=1024 * 1024) as file:
        readline = file.readline
        header_line = readline()
        if not header_line:
            sys.stdout.write("TOTAL:{}")
            return

        if b'"' in header_line:
            header = read_record(header_line, readline)
        else:
            header = remove_eol(header_line).split(b",")

        if header and header[0].startswith(b"\xef\xbb\xbf"):
            header[0] = header[0][3:]

        positions = {name: i for i, name in enumerate(header)}
        account_index = positions[b"account_id"]
        category_index = positions[b"category"]
        amount_index = positions[b"amount_cents"]

        standard_order = (
            account_index == 0 and category_index == 1 and amount_index == 2
        )

        get_total = totals.get

        while True:
            line = readline()
            if not line:
                break
            if line in (b"\n", b"\r\n", b"\r"):
                continue

            if standard_order:
                parts = line.split(b",", 2)
                if (
                    len(parts) == 3
                    and not parts[0].startswith(b'"')
                    and not parts[1].startswith(b'"')
                    and not parts[2].startswith(b'"')
                ):
                    account_bytes, category, amount_bytes = parts
                else:
                    fields = read_record(line, readline)
                    account_bytes = fields[account_index]
                    category = fields[category_index]
                    amount_bytes = fields[amount_index]
            else:
                if b'"' in line:
                    fields = read_record(line, readline)
                else:
                    fields = remove_eol(line).split(b",")
                account_bytes = fields[account_index]
                category = fields[category_index]
                amount_bytes = fields[amount_index]

            account_id = int(account_bytes)
            if account_id % 11 < 7:
                value = int(amount_bytes) * ((account_id % 97) + 1)
                totals[category] = get_total(category, 0) + value

    result = {key.decode("utf-8"): value for key, value in totals.items()}
    output = json.dumps(
        result,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    sys.stdout.write("TOTAL:" + output)


if __name__ == "__main__":
    main()
