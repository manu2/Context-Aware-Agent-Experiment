#!/usr/bin/env python3
"""
Deterministic Dataset Generator for Substrate-Aware Code Generation Benchmark.

Generates data/vectors.npy (8,000 x 1,024 float32 matrix, ~32.8 MB on disk)
with exact seed 42, matching the frozen SHA-256 hash:
199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085
"""

import os
import sys
import hashlib
import numpy as np

EXPECTED_SHA256 = "199a60e06bcda58ec741348972ad881f50d5fa67b2f9fb6ea09f37c514ec6085"

def generate_dataset(output_path: str = "data/vectors.npy") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if os.path.exists(output_path):
        with open(output_path, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        if h == EXPECTED_SHA256:
            print(f"[+] Dataset already exists and matches SHA-256: {h}")
            return output_path
        print(f"[!] Existing dataset hash ({h}) differs from expected. Regenerating...")

    print(f"[*] Generating deterministic 8,000 x 1,024 float32 matrix (seed=42) to {output_path}...")
    np.random.seed(42)
    mat = np.random.randn(8000, 1024).astype(np.float32)
    np.save(output_path, mat)

    with open(output_path, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()

    assert h == EXPECTED_SHA256, f"Hash mismatch: got {h}, expected {EXPECTED_SHA256}"
    print(f"[+] Successfully generated {output_path} with SHA-256: {h}")
    return output_path

if __name__ == "__main__":
    generate_dataset()
