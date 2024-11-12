import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Configure the matplotlib backend
matplotlib.use('TkAgg')  # Change to your preferred backend if needed

# Database configuration
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"

# Create a database engine and reflect the existing database schema
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Load the existing tables
subject_table = Table('subject', metadata, autoload_with=engine)
embedding_table = Table('embedding', metadata, autoload_with=engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Function to get subjects and embeddings from the database
def get_subjects_with_embeddings():
    # Join the subject and embedding tables on the subject_id
    results = (
        session.query(subject_table.c.subject_name, embedding_table.c.embedding)
        .join(embedding_table, subject_table.c.id == embedding_table.c.subject_id)
        .all()
    )
    # Close the session
    session.close()
    return results

# Fetch data from the database
data = get_subjects_with_embeddings()

# Extract names and embeddings
names = [item[0] for item in data]
embeddings = np.array([item[1] for item in data])

# Perform dimensionality reduction using PCA
pca = PCA(n_components=2)
embeddings_pca = pca.fit_transform(embeddings)

# Optionally scale embeddings before applying PCA
scaler = StandardScaler()
scaled_embeddings = scaler.fit_transform(embeddings)
embeddings_pca_scaled = pca.fit_transform(scaled_embeddings)

# Plotting the results
plt.ion() 
plt.figure(figsize=(10, 5))

# PCA without scaling
plt.subplot(1, 2, 1)
plt.scatter(embeddings_pca[:, 0], embeddings_pca[:, 1], c='blue')
for i, name in enumerate(names):
    plt.text(embeddings_pca[i, 0], embeddings_pca[i, 1], name, fontsize=8)
plt.title('PCA of Face Embeddings (Unscaled)')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.axis("equal")  # Make the aspect ratio equal

# # Invert the vertical axis if needed
# plt.gca().invert_yaxis()
# plt.gca().invert_xaxis()

# PCA with scaling
plt.subplot(1, 2, 2)
plt.scatter(embeddings_pca_scaled[:, 0], embeddings_pca_scaled[:, 1], c='blue')
for i, name in enumerate(names):
    plt.text(embeddings_pca_scaled[i, 0], embeddings_pca_scaled[i, 1], name, fontsize=8)
plt.title('PCA of Face Embeddings (Scaled)')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.axis("equal")  # Make the aspect ratio equal

# Invert the vertical axis if needed
# plt.gca().invert_yaxis()
plt.gca().invert_xaxis()

# Save the plot to a file
plt.savefig('embeddings-insight-face_pca_plot.png')

# Display the plot
plt.show()

# # Extract embeddings and names
# names = list(embeddings_dict.keys())
# embeddings = np.array(list(embeddings_dict.values()))
