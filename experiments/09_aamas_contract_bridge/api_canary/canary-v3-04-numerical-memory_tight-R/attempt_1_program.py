additions, roundoff error is at most $1024 \times 2^{-53} \approx 10^{-13}$ relative error.
$\|x_i - x_j\|^2 = \|x_i\|^2 + \|x_j\|^2 - 2 x_i \cdot x_j$.
If $\|x_i - x_j\| \ge 0.01$, relative error is negligible (less than $10^{-10}$).
Wait! What if the vectors in `vectors.npy` are normalized embeddings (e.g. unit vectors)?
Unit vectors have $\|x_i\|^2 = 1$.
Then $\|x_i - x_j\|^2 = 2 - 2 \cos \
