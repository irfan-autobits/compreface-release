import os
import shutil
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
matplotlib.use('TkAgg') # or 'Qt5Agg', 'Qt4Agg', etc.
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
import umap
from scipy.stats import zscore
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker

embed_dir = "facenet-plots"
# shutil.rmtree(embed_dir, ignore_errors=True)
embed_plot_path = os.path.join(embed_dir, 'plots')
embed_img_path = os.path.join(embed_dir, 'imgs')
embed_line_path = os.path.join(embed_dir, 'line')
embed_circular_path = os.path.join(embed_dir, 'circular')
os.makedirs(embed_circular_path, exist_ok=True)
os.makedirs(embed_line_path, exist_ok=True)
os.makedirs(embed_img_path, exist_ok=True)
os.makedirs(embed_plot_path, exist_ok=True)
# Example dictionary with person names and actual embeddings for insightface.Calculator@arcface-r100-msfdrop75
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

# # Function to plot embedding as an image-image-------------------------------
def plot_embedding_as_image(person, person_embedding):
    # Reshape embedding to a 16x32 grid
    grid_size = (16, 32)
    embedding_grid = person_embedding.reshape(grid_size)

    # Normalize the embedding values to range [-1, 1]
    max_abs_value = np.max(np.abs(embedding_grid))
    normalized_embedding = embedding_grid / max_abs_value

    # Create a custom colormap from blue to white to red
    cmap = plt.get_cmap('bwr')  # 'bwr' is a built-in blue-white-red colormap

    # Plot the embedding as an image
    plt.figure(figsize=(8, 4))
    plt.imshow(normalized_embedding, cmap=cmap, vmin=-1, vmax=1)
    plt.colorbar(label='Embedding Value')
    plt.title(f'Embedding Image for {person}')
    plt.axis('off')  # Hide axes for a cleaner look

    # Save the plot
    plot_path = os.path.join(embed_img_path, f'embedding_image_{person}.png')
    plt.savefig(plot_path, bbox_inches='tight')
    print(f'Saved: {plot_path}')
    plt.close()

# Function to plot embedding as a horizontal line image
def plot_embedding_as_horizontal_line(person, person_embedding):
    # Reshape embedding to a 1x512 grid for a horizontal line
    line_size = (1, 512)
    embedding_line = person_embedding.reshape(line_size)

    # Normalize the embedding values to range [-1, 1]
    max_abs_value = np.max(np.abs(embedding_line))
    normalized_embedding = embedding_line / max_abs_value

    # Create a custom colormap from blue to white to red
    cmap = plt.get_cmap('bwr')  # 'bwr' is a built-in blue-white-red colormap

    # Plot the embedding as an image
    plt.figure(figsize=(16, 2))  # Adjust figure size for a horizontal line
    plt.imshow(normalized_embedding, cmap=cmap, aspect='auto', vmin=-1, vmax=1)
    plt.colorbar(label='Embedding Value')
    plt.title(f'Embedding Line for {person}')
    plt.axis('off')  # Hide axes for a cleaner look

    # Save the plot
    plot_path = os.path.join(embed_line_path, f'embeddings_horizontal_{person}.png')
    plt.savefig(plot_path, bbox_inches='tight')
    print(f'Saved: {plot_path}')
    plt.close()

# Circular plot function with line connection
def plot_embedding_as_circular(person, person_embedding):
    # Number of dimensions (512)
    num_dimensions = len(person_embedding)
    if num_dimensions != 512:
        print(f"Embedding for {person} is not 512-dimensional. Skipping.")
        return

    # Normalize values
    min_value = np.min(person_embedding)
    max_value = np.max(person_embedding)
    
    # Scale values to range [0.5, 1] for smaller distance between min and max
    scaled_embedding = 0.5 + 0.3 * (person_embedding - min_value) / (max_value - min_value)

    # Create angles for polar coordinates
    angles = np.linspace(0, 2 * np.pi, num_dimensions, endpoint=False)

    # Close the circle by repeating the first point
    angles = np.append(angles, angles[0])
    scaled_embedding = np.append(scaled_embedding, scaled_embedding[0])

    # Plot settings
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)

    # Plot the line connecting the dots
    ax.plot(angles, scaled_embedding, color='black', linewidth=1, label='Embedding Line')

    # Customize the plot
    ax.set_yticklabels([])  # Hide radial grid labels
    ax.set_title(f'Circular Embedding Plot for {person}')

    # Save the plot
    plot_path = os.path.join(embed_circular_path, f'circular_plot_{person}.png')
    plt.savefig(plot_path, bbox_inches='tight')
    print(f'Saved: {plot_path}')
    plt.close()

def plot_embedding_with_line(person, person_embedding):
    # Number of dimensions (512)
    num_dimensions = len(person_embedding)
    if num_dimensions != 512:
        print(f"Embedding for {person} is not 512-dimensional. Skipping.")
        return

    # Normalize values
    min_value = np.min(person_embedding)
    max_value = np.max(person_embedding)
    
    # Scale values to range [0.5, 1] for smaller distance between min and max
    scaled_embedding = 0.3 * (person_embedding - min_value) / (max_value - min_value)

    # Create a range for the x-axis based on the number of dimensions
    x = np.arange(num_dimensions)

    # Plot settings
    plt.figure(figsize=(20, 5))

    # Plot the embedding as a bar chart
    # plt.bar(x, scaled_embedding, color='blue', alpha=0.6, label='Embedding Bar')

    # Overlay a line connecting the top of the bars
    plt.plot(x, scaled_embedding, color='black', linewidth=1, label='Embedding Line')

    # Customize the plot
    plt.xlabel('Dimensions')
    plt.ylabel('Values')
    plt.title(f'Embedding Plot for {person}')
    plt.xticks(rotation=90)  # Rotate x-axis labels if needed
    plt.legend()
    plt.grid(axis='y')

    # Save the plot
    plot_path = os.path.join(embed_plot_path, f'embeddings_plot_{person}.png')
    plt.savefig(plot_path, bbox_inches='tight')
    print(f'Saved: {plot_path}')
    plt.close()


# Fetch data from the database
data = get_subjects_with_embeddings()
img_plot_flags = ['plot','img','line','circle']

img_plot_flag = img_plot_flags[3]
if img_plot_flag == 'plot':
    # Process each person's embedding
    for item in data:
        person = item[0]
        person_embedding = np.array(item[1])

        # Ensure the embedding has the correct length
        if len(person_embedding) == 512:
            plot_embedding_with_line(person, person_embedding)

# img_plot_flag = img_plot_flags[1]
if img_plot_flag == 'img':
    # Process each person's embedding
    for item in data:
        person = item[0]
        person_embedding = np.array(item[1])

        # Ensure the embedding has the correct length
        if len(person_embedding) == 512:
            plot_embedding_as_image(person, person_embedding)

# img_plot_flag = img_plot_flags[2]
if img_plot_flag == 'line':
    # Process each person's embedding
    for item in data:
        person = item[0]
        person_embedding = np.array(item[1])

        # Ensure the embedding has the correct length
        if len(person_embedding) == 512:
            plot_embedding_as_horizontal_line(person, person_embedding)

# img_plot_flag = img_plot_flags[3]
if img_plot_flag == 'circle':
    # Process each person's embedding
    for item in data:
        person = item[0]
        person_embedding = np.array(item[1])

        # Ensure the embedding has the correct length
        if len(person_embedding) == 512:
            plot_embedding_as_circular(person, person_embedding)