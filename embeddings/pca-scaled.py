import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

# Example dictionary with person names and actual embeddings
embeddings_dict = {
    'Person1': np.array([-0.00702074707347583, -0.00339671646636909, ..., -0.0169261722930381]),
    'Person2': np.array([-0.12345, 0.23456, ..., -0.01234]),
    'Person3': np.array([0.11111, -0.33333, ..., 0.98765]),
}

# Extract embeddings and names
names = list(embeddings_dict.keys())
embeddings = np.array(list(embeddings_dict.values()))

# Optionally scale embeddings (e.g., zero mean and unit variance)
scaler = StandardScaler()
scaled_embeddings = scaler.fit_transform(embeddings)

# Perform dimensionality reduction (PCA or t-SNE)
# Use PCA for fast computation
pca = PCA(n_components=2)  # reduce to 2 dimensions
embeddings_pca = pca.fit_transform(scaled_embeddings)

# Optionally, use t-SNE for better visualization
tsne = TSNE(n_components=2, perplexity=30, n_iter=300)
embeddings_tsne = tsne.fit_transform(scaled_embeddings)

# Plot the embeddings with PCA
plt.figure(figsize=(10, 5))
plt.subplot(1, 2, 1)
plt.scatter(embeddings_pca[:, 0], embeddings_pca[:, 1], c='blue')
for i, name in enumerate(names):
    plt.text(embeddings_pca[i, 0], embeddings_pca[i, 1], name)
plt.title('PCA of Face Embeddings')

# Plot the embeddings with t-SNE
plt.subplot(1, 2, 2)
plt.scatter(embeddings_tsne[:, 0], embeddings_tsne[:, 1], c='red')
for i, name in enumerate(names):
    plt.text(embeddings_tsne[i, 0], embeddings_tsne[i, 1], name)
plt.title('t-SNE of Face Embeddings')

plt.show()
