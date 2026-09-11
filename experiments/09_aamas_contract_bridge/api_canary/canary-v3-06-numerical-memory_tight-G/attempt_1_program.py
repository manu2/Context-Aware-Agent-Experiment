FLOPs (100 GFLOPs).
Wait, why does GEMM do $2 \times 8000 \times 8000 \times 1024 \approx 1.3 \times 10^{11}$ FLOPs?
Because GEMM is $\|x\|^2 + \|y\|^2 - 2 x \cdot y$.
Wait! In GEMM, BLAS runs at peak hardware speed (e.g. 200-400 GFLOPs/s with AVX/FMA).
In direct distance:
Can NumPy do direct Euclidean distance using BLAS?
No, NumPy does NOT have a built-in BLAS routine for pairwise Euclidean distance!
`scipy
