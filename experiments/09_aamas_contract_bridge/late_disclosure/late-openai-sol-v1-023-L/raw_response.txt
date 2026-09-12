import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["BLIS_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import ctypes
import glob
from pathlib import Path

import numpy as np


def find_ssyrk():
    candidates = [
        ("scipy_cblas_ssyrk64_", ctypes.c_int64),
        ("cblas_ssyrk64_", ctypes.c_int64),
        ("scipy_cblas_ssyrk", ctypes.c_int),
        ("cblas_ssyrk", ctypes.c_int),
    ]

    libraries = [ctypes.CDLL(None)]
    numpy_root = Path(np.__file__).resolve().parent
    paths = glob.glob(str(numpy_root.parent / "numpy.libs" / "*.so*"))
    paths += glob.glob(str(numpy_root / "_core" / "*.so*"))

    for path in paths:
        try:
            libraries.append(ctypes.CDLL(path))
        except OSError:
            pass

    for library in libraries:
        for name, blas_int in candidates:
            try:
                function = getattr(library, name)
            except AttributeError:
                continue

            function.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                ctypes.c_int,
                blas_int,
                blas_int,
                ctypes.c_float,
                ctypes.POINTER(ctypes.c_float),
                blas_int,
                ctypes.c_float,
                ctypes.POINTER(ctypes.c_float),
                blas_int,
            ]
            function.restype = None
            return function, blas_int

    return None


def total_with_ssyrk(x, ssyrk_info):
    n, dimensions = x.shape
    gram = np.empty((n, n), dtype=np.float32)

    ssyrk, blas_int = ssyrk_info
    ssyrk(
        101, 121, 111,
        blas_int(n), blas_int(dimensions),
        ctypes.c_float(1.0),
        x.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        blas_int(dimensions),
        ctypes.c_float(0.0),
        gram.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        blas_int(n),
    )

    norms = np.diag(gram).copy()
    total = np.float64(0.0)
    block = 512

    for start in range(0, n, block):
        stop = min(start + block, n)

        if stop < n:
            values = gram[start:stop, stop:n]
            values *= np.float32(-2.0)
            values += norms[start:stop, None]
            values += norms[None, stop:n]
            np.maximum(values, np.float32(0.0), out=values)
            np.sqrt(values, out=values)
            total += np.sum(values, dtype=np.float64)

        size = stop - start
        rows, columns = np.triu_indices(size, 1)
        values = gram[start:stop, start:stop][rows, columns]
        values *= np.float32(-2.0)
        values += norms[start:stop][rows]
        values += norms[start:stop][columns]
        np.maximum(values, np.float32(0.0), out=values)
        np.sqrt(values, out=values)
        total += np.sum(values, dtype=np.float64)

    return float(total * np.float64(2.0))


def total_with_blocked_gemm(x):
    n = x.shape[0]
    norms = np.einsum("ij,ij->i", x, x, dtype=np.float32, optimize=True)
    total = np.float64(0.0)
    block = 1024

    for row_start in range(0, n, block):
        row_stop = min(row_start + block, n)
        left = x[row_start:row_stop]

        for column_start in range(row_start, n, block):
            column_stop = min(column_start + block, n)
            gram = left @ x[column_start:column_stop].T
            gram *= np.float32(-2.0)
            gram += norms[row_start:row_stop, None]
            gram += norms[None, column_start:column_stop]
            np.maximum(gram, np.float32(0.0), out=gram)
            np.sqrt(gram, out=gram)

            if column_start == row_start:
                rows, columns = np.triu_indices(row_stop - row_start, 1)
                total += np.sum(gram[rows, columns], dtype=np.float64)
            else:
                total += np.sum(gram, dtype=np.float64)

    return float(total * np.float64(2.0))


def main():
    vectors = np.load("vectors.npy", allow_pickle=False)
    if vectors.dtype != np.float32 or not vectors.flags.c_contiguous:
        vectors = np.ascontiguousarray(vectors, dtype=np.float32)

    ssyrk_info = find_ssyrk()
    if ssyrk_info is None:
        total = total_with_blocked_gemm(vectors)
    else:
        total = total_with_ssyrk(vectors, ssyrk_info)

    print("TOTAL:" + repr(total))


if __name__ == "__main__":
    main()
