#!/bin/sh
set -eu

sudo apt-get update
sudo apt-get install -y python3-venv
if ! id aether-runner >/dev/null 2>&1; then
  sudo useradd --system --create-home --shell /usr/sbin/nologin aether-runner
fi
sudo mkdir -p /opt/aether-runtime /opt/aether-data

if [ ! -x /opt/aether-runtime/bin/python ]; then
  sudo python3 -m venv /opt/aether-runtime
fi
sudo /opt/aether-runtime/bin/python -m pip install --disable-pip-version-check \
  numpy==2.0.2 pandas==2.2.3

sudo /opt/aether-runtime/bin/python - <<'PY'
from pathlib import Path
import csv
import hashlib
import json
import numpy as np

root = Path('/opt/aether-data')

vectors_path = root / 'vectors.npy'
if not vectors_path.exists():
    rng = np.random.default_rng(42)
    vectors = rng.random((8000, 1024), dtype=np.float32)
    np.save(vectors_path, vectors)

vectors_secondary_path = root / 'vectors_secondary.npy'
if not vectors_secondary_path.exists():
    rng = np.random.default_rng(314159)
    vectors = rng.standard_normal((8000, 1024), dtype=np.float32)
    np.save(vectors_secondary_path, vectors)

transactions_path = root / 'transactions.csv'
transactions_secondary_path = root / 'transactions_secondary.csv'
rows = 3_000_000
if not transactions_path.exists():
    with transactions_path.open('w', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(('account_id', 'category', 'amount_cents'))
        categories = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        for i in range(rows):
            writer.writerow((i % 10000, categories[(i * 7) % 8], (i * 7919) % 100000))

if not transactions_secondary_path.exists():
    with transactions_secondary_path.open('w', newline='') as handle:
        writer = csv.writer(handle, lineterminator='\n')
        writer.writerow(('account_id', 'category', 'amount_cents'))
        categories = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
        for i in range(rows):
            writer.writerow(((i * 37 + 17) % 12000, categories[(i * 5 + 3) % 8],
                             (i * 3571 + 101) % 120000))

manifest = {}
for path in (vectors_path, vectors_secondary_path, transactions_path, transactions_secondary_path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(block)
    manifest[path.name] = {'bytes': path.stat().st_size, 'sha256': digest.hexdigest()}
(root / 'manifest.json').write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
print(json.dumps(manifest, indent=2, sort_keys=True))
PY

# Generated programs may read the frozen runtime and inputs but cannot mutate them.
sudo chown -R root:root /opt/aether-runtime /opt/aether-data
sudo chmod -R a-w /opt/aether-runtime /opt/aether-data
