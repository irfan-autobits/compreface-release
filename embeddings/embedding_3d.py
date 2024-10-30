import os
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # New import for 3D plotting
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

import plotly.graph_objects as go
# Configure the matplotlib backend
matplotlib.use('TkAgg')  # Change to your preferred backend if needed

# Database configuration
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"

model = 'insightface'
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

# Perform dimensionality reduction using PCA to 3 components
pca = PCA(n_components=3)
embeddings_pca = pca.fit_transform(embeddings)

# Optionally scale embeddings before applying PCA
scaler = StandardScaler()
scaled_embeddings = scaler.fit_transform(embeddings)
embeddings_pca_scaled = pca.fit_transform(scaled_embeddings)

# Plotting the results in 3D
plt.ion()
fig = plt.figure(figsize=(15, 7))

# PCA without scaling
ax1 = fig.add_subplot(1, 2, 1, projection='3d')
ax1.scatter(embeddings_pca[:, 0], embeddings_pca[:, 1], embeddings_pca[:, 2], c='blue')
for i, name in enumerate(names):
    ax1.text(embeddings_pca[i, 0], embeddings_pca[i, 1], embeddings_pca[i, 2], name, fontsize=8)
ax1.set_title('PCA of Face Embeddings (Unscaled)')
ax1.set_xlabel('PCA 1')
ax1.set_ylabel('PCA 2')
ax1.set_zlabel('PCA 3')



# PCA with scaling
ax2 = fig.add_subplot(1, 2, 2, projection='3d')
ax2.scatter(embeddings_pca_scaled[:, 0], embeddings_pca_scaled[:, 1], embeddings_pca_scaled[:, 2], c='blue')
for i, name in enumerate(names):
    ax2.text(embeddings_pca_scaled[i, 0], embeddings_pca_scaled[i, 1], embeddings_pca_scaled[i, 2], name, fontsize=8)
ax2.set_title('PCA of Face Embeddings (Scaled)')
ax2.set_xlabel('PCA 1')
ax2.set_ylabel('PCA 2')
ax2.set_zlabel('PCA 3')

# Save the plot to a file
plt.savefig(f'embeddings-{model}-face_pca_3d_plot.png')

# Convert embeddings to 3D interactive plot using Plotly
fig = go.Figure(data=[go.Scatter3d(
    x=embeddings_pca[:, 0],
    y=embeddings_pca[:, 1],
    z=embeddings_pca[:, 2],
    mode='markers+text',
    text=names,
    textposition="top center",
    marker=dict(size=5, color='blue')
)])

fig.update_layout(
    title="PCA of Face Embeddings (Unscaled)",
    scene=dict(
        xaxis_title="PCA 1",
        yaxis_title="PCA 2",
        zaxis_title="PCA 3"
    )
)

# Save the interactive plot as an HTML file
fig.write_html(f"3d_embeddings_{model}_plot(Unscaled).html")

# Convert embeddings to 3D interactive plot using Plotly
fig = go.Figure(data=[go.Scatter3d(
    x=embeddings_pca_scaled[:, 0],
    y=embeddings_pca_scaled[:, 1],
    z=embeddings_pca_scaled[:, 2],
    mode='markers+text',
    text=names,
    textposition="top center",
    marker=dict(size=5, color='blue')
)])

fig.update_layout(
    title="PCA of Face Embeddings (Scaled)",
    scene=dict(
        xaxis_title="PCA 1",
        yaxis_title="PCA 2",
        zaxis_title="PCA 3"
    )
)

# Save the interactive plot as an HTML file
fig.write_html(f"3d_embeddings_{model}_plot(Scaled).html")

# Display the plot and keep the window open
plt.show(block=True)