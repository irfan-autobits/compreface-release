import os
import shutil
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

matplotlib.use('TkAgg')  # Set the backend for interactive plotting

# Directory setup
embed_dir = "facenet-plots"
# shutil.rmtree(embed_dir, ignore_errors=True)
embed_circular_path = os.path.join(embed_dir, 'circular')
os.makedirs(embed_circular_path, exist_ok=True)

# Database configuration
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"
engine = create_engine(DATABASE_URL)
metadata = MetaData()
metadata.reflect(bind=engine)

# Load tables and create a session
subject_table = Table('subject', metadata, autoload_with=engine)
embedding_table = Table('embedding', metadata, autoload_with=engine)
Session = sessionmaker(bind=engine)
session = Session()

# Fetch embeddings from the database
def get_subjects_with_embeddings():
    results = (
        session.query(subject_table.c.subject_name, embedding_table.c.embedding)
        .join(embedding_table, subject_table.c.id == embedding_table.c.subject_id)
        .all()
    )
    session.close()
    return results

# Circular plot function
def plot_embedding_as_circular(person, person_embedding):
    # Number of dimensions (512)
    num_dimensions = len(person_embedding)
    if num_dimensions != 512:
        print(f"Embedding for {person} is not 512-dimensional. Skipping.")
        return

    # Normalize values
    max_abs_value = np.max(np.abs(person_embedding))
    normalized_embedding = person_embedding / max_abs_value

    # Create angles for polar coordinates
    angles = np.linspace(0, 2 * np.pi, num_dimensions, endpoint=False)

    # Plot settings
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    # Plot each value as a point in the circular space
    ax.scatter(angles, normalized_embedding, color='blue', s=20, label='Embedding Value')

    # Customize the plot
    ax.set_yticklabels([])  # Hide radial grid labels
    ax.set_title(f'Circular Embedding Plot for {person}')
    ax.grid(True)

    # Save the plot
    plot_path = os.path.join(embed_circular_path, f'circular_plot_{person}.png')
    plt.savefig(plot_path, bbox_inches='tight')
    print(f'Saved: {plot_path}')
    plt.close()

# Main execution
data = get_subjects_with_embeddings()
for item in data:
    person = item[0]
    person_embedding = np.array(item[1])

    # Plot circular embeddings
    plot_embedding_as_circular(person, person_embedding)
