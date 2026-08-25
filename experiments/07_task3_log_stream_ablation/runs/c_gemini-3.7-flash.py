import collections
import tempfile

def process_logs(file_path: str = "server_logs.txt") -> None:
    errors = 0
    endpoint_counts = collections.Counter()

    num_shards = 32
    shard_files = [
        tempfile.TemporaryFile(mode="w+", encoding="utf-8", buffering=65536)
        for _ in range(num_shards)
    ]

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 5:
                    continue

                ip = parts[1]
                endpoint = parts[3]
                status_str = parts[4]

                try:
                    status = int(status_str)
                    if 500 <= status < 600:
                        errors += 1
                except ValueError:
                    pass

                endpoint_counts[endpoint] += 1

                shard_idx = hash(ip) % num_shards
                shard_files[shard_idx].write(ip + "\n")

        unique_ips = 0
        for shard_file in shard_files:
            shard_file.seek(0)
            seen_ips = set()
            for ip_line in shard_file:
                seen_ips.add(ip_line.rstrip("\n"))
            unique_ips += len(seen_ips)
            seen_ips.clear()

    finally:
        for shard_file in shard_files:
            shard_file.close()

    top_5_endpoints = [ep for ep, _ in endpoint_counts.most_common(5)]

    print(f"ERRORS:{errors}")
    print(f"TOP_ENDPOINTS:{','.join(top_5_endpoints)}")
    print(f"UNIQUE_IPS:{unique_ips}")

if __name__ == "__main__":
    process_logs("server_logs.txt")
