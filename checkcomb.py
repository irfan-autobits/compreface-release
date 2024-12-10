from flask import Flask, request, jsonify, abort
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
import threading
import os
import logging
import jwt
import time
from datetime import datetime
import cv2

# Flask app and logging configuration
app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# Database and JWT Setup
# Get environment variables for database connection
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
# REC_TABLE = os.getenv("REC_TABLE")
# Construct the database URL
logger.debug(f"""POSTGRES_USER={POSTGRES_USER}, 
             POSTGRES_PASSWORD={POSTGRES_PASSWORD}, 
             POSTGRES_DB={POSTGRES_DB}, 
             POSTGRES_HOST={POSTGRES_HOST}""")

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
# DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
metadata = MetaData()

# JWT secret key
SECRET_KEY = os.getenv("SECRET_KEY","top_secret")

def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        abort(401, "Token expired")
    except jwt.InvalidTokenError:
        abort(401, "Invalid token")


@app.before_request
def before_request():
    # Check if API key or JWT is provided
    if request.headers.get('Authorization'):
        token = request.headers['Authorization']
        decode_jwt(token)

@app.route('/endpoint/<table_name>', methods=['GET', 'POST'])
def handle_request(table_name):
    if request.method == 'POST':
        data = request.json
        app.logger.info("POST request received")
        logger.debug(f"""Response:
            "massagio": "POST request received",
            "data_received": {data} """)
        return jsonify({
            "message": "POST request received",
            "data_received": data
        })

    elif request.method == 'GET':
        # Fetch data from the database
        try:
            # Define the recognition table
            recognition_table = Table(table_name, metadata, autoload_with=engine)
            session = Session()
            query = session.query(recognition_table).all()
            results = [row._asdict() for row in query]
            session.close()
            response = results
        except Exception as e:
            app.logger.error("Error fetching data from database", exc_info=True)
            response = {
                "message": "Error fetching data from database",
                "error": str(e)
            }

        logger.debug(f"Response: {table_name} retreved Successfully")
        return jsonify(response)

@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    method = request.method
    app.logger.info(f"{method} request received on /{path}")
    response = {
        "message": f"{method} request received on /{path}",
        "method": method,
        "path": path
    }

    if method == 'POST':
        response["data_received"] = request.json  # Add posted data to response if available
    logger.debug(f"Response: {response}")
    return jsonify(response)

@app.route('/start', methods=['POST'])
def start_recognition():
    if recognition_thread.is_alive():
        return jsonify({"status": "Recognition is already running"}), 200

    main_app.start_recognition()
    return jsonify({"status": "Recognition started"}), 200

@app.route('/stop', methods=['POST'])
def stop_recognition():
    main_app.stop()
    recognition_thread.join()
    return jsonify({"status": "Recognition stopped"}), 200

# MainApp Implementation
class MainApp:
    def __init__(self, api_key, use_rtsp, rtsp_url=None):
        self.camera_manager = CameraManager(use_rtsp, rtsp_url)
        self.recognition_manager = RecognitionManager(api_key)
        self.database_manager = DatabaseManager()
        self.active = True

    def start_recognition(self):
        self.active = True
        threading.Thread(target=self._run).start()

    def _run(self):
        while self.active:
            frame = self.camera_manager.get_frame()
            if frame is not None:
                results = self.recognition_manager.recognize_face(frame)
                if results:
                    for result in results:
                        result['camera'] = "Device Camera"
                        result['image'] = self.save_image(result)
                    threading.Thread(target=self.database_manager.save_results, args=(results,)).start()
            time.sleep(1)

    def save_image(self, result):
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        subject = result['subjects'][0]['subject']
        face_image_path = f"images/{subject}_{timestamp}.jpg"
        cv2.imwrite(face_image_path, result['face_image'])
        return face_image_path

    def stop(self):
        self.active = False
        self.camera_manager.release()
        self.database_manager.close()

# Initialize MainApp and Start Flask App
api_key = "your_api_key"
use_rtsp = True
rtsp_url = "rtsp://camera_url"
main_app = MainApp(api_key, use_rtsp, rtsp_url)
recognition_thread = threading.Thread(target=main_app._run)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

