import os
import shutil
# Directory to store employee images
database_dir = 'Report'
# Create the main database directory if it doesn't exist
shutil.rmtree(database_dir, ignore_errors=True)
os.makedirs(database_dir, exist_ok=True)