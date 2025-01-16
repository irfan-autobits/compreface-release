import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
# from app.models.model import subject_table, session, embedding_table
from config.Paths import DATABASE_DIR
# from sqlalchemy import select

# stmt = select(subject_table)
# results = session.execute(stmt)
# subjects = [dict(row) for row in results]

service = "autobits"
model= "facenet"
image_path = DATABASE_DIR / f'embeddings_{service}_{model}_pca_2d_plot.png'
# Function to get subjects and embeddings from the database
def get_subjects_with_embeddings():
    global subject_table, embedding_table, session
    # Join the subject and embedding tables on the subject_id
    results = (
        session.query(subject_table.c.subject_name, embedding_table.c.embedding)
        .join(embedding_table, subject_table.c.id == embedding_table.c.subject_id)
        .all()
    )
    # Close the session
    session.close()
    return results

def visulize(faltu):

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
    plt.figure(figsize=(15, 7.5))

    # PCA without scaling
    plt.subplot(1, 2, 1)
    plt.scatter(embeddings_pca[:, 0], embeddings_pca[:, 1], c='blue')
    for i, name in enumerate(names):
        plt.text(embeddings_pca[i, 0], embeddings_pca[i, 1], name, fontsize=9)
    plt.title('PCA of Face Embeddings (Unscaled)')

    # # Invert the vertical axis if needed
    # plt.gca().invert_yaxis()
    # plt.gca().invert_xaxis()

    # PCA with scaling
    plt.subplot(1, 2, 2)
    plt.scatter(embeddings_pca_scaled[:, 0], embeddings_pca_scaled[:, 1], c='blue')
    for i, name in enumerate(names):
        plt.text(embeddings_pca_scaled[i, 0], embeddings_pca_scaled[i, 1], name, fontsize=9)
    plt.title('PCA of Face Embeddings (Scaled)')

    # Invert the vertical axis if needed
    plt.gca().invert_yaxis()
    plt.gca().invert_xaxis()

    # Save the plot to a file
    plt.savefig(str(image_path))
