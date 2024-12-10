from flask import Flask, Response, request, jsonify, abort
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.orm import sessionmaker
import threading
import os
import logging
import jwt
import time
from datetime import datetime
import cv2
from dotenv import load_dotenv
from Cam_Manager import CameraManager
from Data_Manager import DatabaseManager
from Recog_Manager import RecognitionManager

# Flask app and logging configuration
app = Flask(__name__)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

load_dotenv()
FACE_DET_TH = float(os.getenv("FACE_DET_TH", 0.8))
FACE_REC_TH = float(os.getenv("FACE_REC_TH", 0.0))
API_KEY = os.getenv("API_KEY", '00000000-0000-0000-0000-000000000002')

print(f'FACE_DET_TH = {FACE_DET_TH}',type(FACE_DET_TH))
print(f'FACE_REC_TH = {FACE_REC_TH}',type(FACE_REC_TH))
print(f'API_KEY = {API_KEY}',type(API_KEY))

os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Database and JWT Setup
# Get environment variables for database connection
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("postgres_port", "6432")

# REC_TABLE = os.getenv("REC_TABLE")
# Construct the database URL
logger.debug(f"""POSTGRES_USER={POSTGRES_USER}, 
             POSTGRES_PASSWORD={POSTGRES_PASSWORD}, 
             POSTGRES_DB={POSTGRES_DB}, 
             POSTGRES_HOST={POSTGRES_HOST}""")

# DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"


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
            response = {
                "message": "GET request received",
                "data": results
            }
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

@app.route('/add_camera', methods=['POST'])
def add_camera():
    """Add a new camera."""
    data = request.json
    camera_id = data.get("camera_id")
    rtsp_url = data.get("rtsp_url")

    if not camera_id:
        return jsonify({"error": "camera_id is required"}), 400

    try:
        main_app.add_camera(camera_id, rtsp_url)
        return jsonify({"status": f"Camera {camera_id} added successfully"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/start/<camera_id>', methods=['POST'])
def start_camera_recognition(camera_id):
    """Start recognition for a specific camera."""
    try:
        main_app.start_recognition(camera_id)
        return jsonify({"status": f"Recognition started for camera {camera_id}"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/stop/<camera_id>', methods=['POST'])
def stop_camera_recognition(camera_id):
    """Stop recognition for a specific camera."""
    try:
        main_app.stop_recognition(camera_id)
        return jsonify({"status": f"Recognition stopped for camera {camera_id}"}), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

@app.route('/stop_all', methods=['POST'])
def stop_all_cameras():
    """Stop all cameras."""
    main_app.stop_all()
    return jsonify({"status": "All cameras stopped"}), 200

@app.route('/list_cameras', methods=['GET'])
def list_cameras():
    """List all cameras and their statuses."""
    cameras = []
    for camera_id, camera_manager in main_app.cameras.items():
        cameras.append({
            "camera_id": camera_id,
            "status": "running" if camera_manager.is_running() else "stopped"
        })
    return jsonify({"cameras": cameras}), 200

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    def generate_frames():
        while True:
            if camera_id in main_app.cameras:
                frame = main_app.cameras[camera_id].get_frame()
                if frame is not None:
                    _, buffer = cv2.imencode('.jpg', frame)
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.1)

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# MainApp Implementation
class MainApp:
    def __init__(self, api_key, face_det_th, face_rec_th):
        self.recognition_manager = RecognitionManager(api_key, face_det_th, face_rec_th)
        self.database_manager = DatabaseManager()
        self.cameras = {}  # Dictionary to manage multiple cameras
        self.active = True

    def add_camera(self, camera_id, rtsp_url=None):
        """Add a new camera to the system."""
        if camera_id in self.cameras:
            raise ValueError(f"Camera with ID {camera_id} already exists.")
        self.cameras[camera_id] = CameraManager(camera_id, rtsp_url)

    def start_recognition(self, camera_id):
        """Start recognition for a specific camera."""
        if camera_id not in self.cameras:
            raise ValueError(f"Camera with ID {camera_id} not found.")
        camera_manager = self.cameras[camera_id]
        threading.Thread(target=self._run, args=(camera_id, camera_manager)).start()

    def _run(self, camera_id, camera_manager):
        """Recognition loop for a specific camera."""
        while self.active:
            frame = camera_manager.get_frame()
            if frame is not None:
                results = self.recognition_manager.recognize_face(frame)
                if results:
                    for result in results:
                        # Add bounding box and label to the frame
                        box = result.get('box')
                        subject = result['subjects'][0]['subject']
                        color = (0, 255, 0)
                        # cv2.rectangle(frame, (box['x_min'], box['y_min']), 
                        #               (box['x_max'], box['y_max']), color, 1)
                        # cv2.putText(frame, subject, (box['x_min']+5, box['y_min'] - 15),
                        #             cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
                        # result['image'] = self.save_image(result, camera_id)
    
                    # Update the frame in CameraManager for streaming
                    # camera_manager.update_frame(frame)
    
                # Save results asynchronously
                threading.Thread(target=self.database_manager.save_results, args=(results,)).start()
                cv2.imshow('Frame', frame)
            # time.sleep(1)
    
    def save_image(self, result, camera_id):
        """Save the captured face image."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        subject = result['subjects'][0]['subject']
        face_image_path = f"images/{camera_id}_{subject}_{timestamp}.jpg"
        cv2.imwrite(face_image_path, result['face_image'])
        return face_image_path

    def stop_recognition(self, camera_id):
        """Stop recognition for a specific camera."""
        if camera_id not in self.cameras:
            raise ValueError(f"Camera with ID {camera_id} not found.")
        self.cameras[camera_id].release()
        del self.cameras[camera_id]

    def stop_all(self):
        """Stop all cameras."""
        self.active = False
        for camera_manager in self.cameras.values():
            camera_manager.release()
        self.database_manager.close()

    def is_running(self):
        return self.running

# Initialize MainApp and Start Flask App
main_app = MainApp(API_KEY, FACE_DET_TH, FACE_REC_TH)
recognition_thread = threading.Thread(target=main_app._run)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
