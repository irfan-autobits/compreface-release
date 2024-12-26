# final-compre/config/Paths.py
import json
import os
from pathlib import Path
import shutil
from dotenv import load_dotenv
from threading import Lock

# Load environment variables from the .env file
load_dotenv()

# Define the base directory as the directory where the script is located
BASE_DIR = Path(__file__).resolve().parent.parent

# Define other paths relative to the base directory
DATABASE_DIR = BASE_DIR / "Reports"
FACE_DIR = DATABASE_DIR / "saved_face"
DET_LOG_FILE_PATH = DATABASE_DIR / "detection_logs.txt"
CAM_STAT_LOG_FILE_PATH = DATABASE_DIR / "cam_stat_logs.txt"

# Retrieve CAMERA_SOURCES and parse it as JSON
CAMERA_SOURCES = os.getenv("CAMERA_SOURCES", "{}")
cam_sources = json.loads(CAMERA_SOURCES)

HOST = os.getenv("HOST", "http://localhost")
PORT = os.getenv("PORT", "8000")
API_KEY = os.getenv("API_KEY", "00000000-0000-0000-0000-000000000002")
FACE_DET_TH = os.getenv("FACE_DET_TH", 0.8)
FACE_REC_TH = os.getenv("FACE_REC_TH", 0.8)

# Simulating variables
database_dir = DATABASE_DIR
face_dir = FACE_DIR

# Remove the database directory and its contents
shutil.rmtree(database_dir, ignore_errors=True)

# Create the database directory
database_dir.mkdir(parents=True, exist_ok=True)
face_dir.mkdir(parents=True, exist_ok=True)

SECRET_KEY = os.getenv('SECRET_KEY', 'default_fallback_key')

# Define a global lock
frame_lock = Lock()
vs_list = dict()