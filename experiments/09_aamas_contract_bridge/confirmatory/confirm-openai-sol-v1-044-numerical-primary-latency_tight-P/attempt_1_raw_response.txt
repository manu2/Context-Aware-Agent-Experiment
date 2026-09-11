import os

for name in (
    "OPENBLAS_NUM_THREADS",
    "OMP_NUM_THREADS",
    "MKL_NUM_THREADS",
    "BLIS_NUM_THREADS",
    "VECLIB_MAXIMUM_THREADS",
    "NUMEXPR_NUM_THREADS",
):
    os.environ[name] = "1"

import ctypes
import glob
from pathlib import Path

import numpy as np


def try_ssyrk(x, out):
    numpy_dir = Path(np.__file__).resolve().parent
    search_dirs = [
        numpy_dir.parent / "numpy.libs",
        numpy_dir / ".libs",
        numpy_dir.parent,
    ]

    libraries = []
    patterns = (
        "*openblas*.so*",
        "*openblas*.dylib",
        "*openblas*.dll",
        "*blas*.so*",
        "*blas*.dylib",
        "*blas*.dll",
    )
    for directory in search_dirs:
        for pattern in patterns:
            libraries.extend(glob.glob(str(directory / pattern)))

    symbol_specs = (
        ("scipy_cblas_ssyrk64_", ctypes.c_longlong),
        ("cblas_ssyrk64_", ctypes.c_longlong),
        ("scipy_cblas_ssyrk", ctypes.c_int),
        ("cblas_ssyrk", ctypes.c_int),
    )

    n, k = x.shape
    for library_path in dict.fromkeys(libraries):
        try:
            library = ctypes.CDLL(library_path)
        except OSError:
            continue

        for symbol, blas_int in symbol_specs:
            try:
                func = getattr(library, symbol)
            except AttributeError:
                continue

            func.restype = None
            func.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                blas_int,
                blas_int,
                ctypes.c_float,
                ctypes.c_void_p,
                blas_int,
                ctypes.c_float,
                ctypes.c_void_p,
                blas_int,
            ]
            func(
                101,                         # CblasRowMajor
                121,                         # CblasUpper
                111,                         # CblasNoTrans
                n,
                k,
                ctypes.c_float(1.0),
                ctypes.c_void_p(x.ctypes.data),
                k,
                ctypes.c_float(0.0),
                ctypes.c_void_p(out.ctypes.data),
                n,
            )
            return True

    return False


def main():
    x = np.load("vectors.npy", allow_pickle=False)
    if x.dtype != np.float32 or not x.flags.c_contiguous:
        x = np.ascontiguousarray(x, dtype=np.float32)

    n = x.shape[0]
    gram = np.empty((n, n), dtype=np.float32)

    if not try_ssyrk(x, gram):
        gram[:] = x @ x.T

    norms = np.diagonal(gram).copy()
    total = 0.0

    for i in range(n - 1):
        distances = gram[i, i + 1:]
        distances *= np.float32(-2.0)
        distances += norms[i]
        distances += norms[i + 1:]
        np.maximum(distances, np.float32(0.0), out=distances)
        np.sqrt(distances, out=distances)
        total += float(np.sum(distances, dtype=np.float64))

    print("TOTAL:" + repr(total * 2.0))


if __name__ == "__main__":
    main()
