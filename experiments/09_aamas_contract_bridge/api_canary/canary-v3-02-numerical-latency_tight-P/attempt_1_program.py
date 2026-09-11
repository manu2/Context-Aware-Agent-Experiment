!
For 8000 diagonal elements, 8000 * 0.003 = 25! That would be an error!
The diagonal elements MUST be zero!
`np.fill_diagonal(G, 0)`!
YES! Setting the diagonal to 0 is crucial!
`np.fill_diagonal(G, 0)` completely eliminates any diagonal error!

Wait, what about off-diagonal elements where $x_i \approx x_j$?
In random vectors or typical embeddings of dimension 1024, what is the distance between two random vectors?
In 1024 dimensions, random vectors are almost orthogonal. $\|x_i - x_j\|^2 \approx \|x_i\|^2
