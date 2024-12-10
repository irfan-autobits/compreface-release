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

import json
import os
import sys
import cv2
import time
import argparse
import shutil
import numpy as np
import subprocess
from threading import Thread, Lock
from compreface import CompreFace
from datetime import datetime
import struct
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re

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

class MainApp:
    def __init__(self, host, port, api_key, use_rtsp, camera_name,rtsp_url='0', data_dir='Report'):
        self.active = True
        self.results = []
        self.lock = Lock()
        self.use_rtsp = use_rtsp
        self.rtsp_url = rtsp_url
        self.database_dir = data_dir
        self.camera_name = camera_name
        self.acc_file_path = os.path.join(self.database_dir, "logs.txt")
        # shutil.rmtree(self.database_dir, ignore_errors=True)
        os.makedirs(self.database_dir, exist_ok=True)

        if use_rtsp:
            self.start_ffmpeg(rtsp_url)
        else:
            self.capture = cv2.VideoCapture(0)
            self.get_stream_info(self.capture, "Internal Camera")
        
        compre_face = CompreFace(host, port, {
            "limit": 0,
            "det_prob_threshold": FACE_DET_TH,
            "prediction_count": 1,
            "status": False
        })
        self.recognition = compre_face.init_face_recognition(api_key)

        self.FPS = 1 / 25
        self.FPS_MS = int(self.FPS * 1000)
        self.frame = None

        # Start the capture thread for continuous frame fetching
        recognition_thread = threading.Thread(target=main_app._run)

        self.capture_thread = Thread(target=self.update, args=())
        self.capture_thread.daemon = True
        self.capture_thread.start()
        self.detection_history = []  # Store history of detections
        self.max_history = 10  # Keep track of the last 10 detections
        self.repeat_threshold = 5  # Number of repeated detections to consider stuck

    def check_repeated_detections(self, new_subject, new_similarity):
        timestamp = time.time()
        self.detection_history.append((new_subject, new_similarity, timestamp))

        # Keep the history limited to the last `max_history` detections
        if len(self.detection_history) > self.max_history:
            self.detection_history.pop(0)

        # Check if the same subject and similarity repeat
        repeated_detections = [
            entry for entry in self.detection_history
            if entry[0] == new_subject and abs(entry[1] - new_similarity) < 0.0001
        ]

        if len(repeated_detections) >= self.repeat_threshold:
            print("Detection stuck detected! Resetting...")
            return True
        return False
    
    def start_ffmpeg(self, src):
        command = [
            'nice', '-n', '10',
            'ffmpeg', '-hwaccel', 'cuda', '-i', src,
            '-vf', 'scale=960:540',
            '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-an', '-sn', '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    def update(self):
        frame_width = 960
        frame_height = 540
        frame_size = frame_width * frame_height * 3
        while self.active:
            if self.use_rtsp and self.pipe:
                raw_frame = self.pipe.stdout.read(frame_size)
                if len(raw_frame) != frame_size:
                    print("Failed to grab frame from FFmpeg")
                    break
                with self.lock:
                    self.frame = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3)).copy()
            elif self.capture.isOpened():
                with self.lock:
                    self.status, self.frame = self.capture.read()
                if not self.status or self.frame is None:
                    time.sleep(self.FPS)
                    continue
            # Batch process the results every n seconds (synchronously)
            if threaded_camera.results:
                threaded_camera.save_to_database(threaded_camera.results)
                threaded_camera.results = []
                # time.sleep(1)  # Batch save every n seconds
            
    # def reset_stream(self):
    #     self.active = False
    #     time.sleep(1)  # Allow resources to release
    #     if self.use_rtsp and self.pipe:
    #         self.pipe.terminate()
    #     elif self.capture:
    #         self.capture.release()

    #     print("Restarting stream...")
    #     self.__init__(self.host, self.port, self.api_key, self.use_rtsp, self.rtsp_url, self.database_dir)

    def restart_script(self):
        print("Restarting script...")
        python = sys.executable
        os.execl(python, python, *sys.argv)
    

    def save_to_database(self, results):
        # Save the results to the database (non-async)
        session = Session()
        try:
            batch = []
            for result in results:
                box = result.get('box')
                subjects = result.get('subjects')
                if not box:
                    continue

                if self.check_repeated_detections(subjects[0]['subject'], subjects[0]['similarity']):
                    # self.reset_stream()  # Or 
                    self.restart_script()
                    return  # Exit early to reset
                
                if subjects and subjects[0]['similarity'] >= FACE_REC_TH:
                    batch.append({
                        "camera": self.camera_name,
                        "person": subjects[0]['subject'],
                        "accuracy": f"{subjects[0]['similarity'] * 100:.0f}%",
                        "image": self.save_image(subjects[0]['subject'], subjects[0]['similarity'], box, False),
                        "time": datetime.now()
                    })
                    color = (0, 255, 0)
                    self.draw_rectangle_and_text(box, subjects[0]['subject'], color)
                else:
                    batch.append({
                        "camera": self.camera_name,
                        "person": "Unknown",
                        "accuracy": f"{(1 - subjects[0]['similarity']) * 100:.0f}%",
                        "image": self.save_image(f"Unknown_{subjects[0]['subject']}", f"{subjects[0]['similarity']}", box, True),
                        "time": datetime.now()
                    })
                    color = (0, 0, 255)
                    self.draw_rectangle_and_text(box, "Unknown", color)

            session.bulk_insert_mappings(RecognitionResult, batch)
            session.commit()
            session.close()
        except Exception as e:
            session.rollback()
            print(f"Error saving to database: {e}")
        finally:
            session.close()

    def draw_rectangle_and_text(self, box, subject, color):
        cv2.rectangle(self.frame, (box['x_min'], box['y_min']), 
                      (box['x_max'], box['y_max']), color, 1)
        cv2.putText(self.frame, subject, (box['x_min']+5, box['y_min'] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, color, 1)
    def save_image(self, subject, similarity, box, flag):
        timestamp = datetime.now().strftime('%y%m%d-%H:%M:%S-%f')[:-4]
        with self.lock:
            face_image = self.frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]
        face_image_name = f"{similarity}_{subject}_{timestamp}_.jpg"
        if flag:
            subject_dir = os.path.join(self.database_dir, "Unknown")
        else:
            subject_dir = os.path.join(self.database_dir, subject)
        os.makedirs(subject_dir, exist_ok=True)
        face_image_path = os.path.join(subject_dir, face_image_name)
        cv2.imwrite(face_image_path, face_image)
        self.save_to_txt(f"Saved detected face as: {face_image_name}")

        return face_image_path

    def show_frame(self):
        if self.frame is None:
            return

        with self.lock:
            display_frame = self.frame.copy()

        _, im_buf_arr = cv2.imencode(".jpg", display_frame)
        byte_im = im_buf_arr.tobytes()
        try:
            data = self.recognition.recognize(byte_im)
            self.results = data.get('result', [])
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
            self.results = []

        cv2.imshow('Frame', display_frame)
        key = cv2.waitKey(self.FPS_MS) & 0xFF
        if key == ord('q') or key == 27:
            print("Exiting...")
            self.active = False
            cv2.destroyAllWindows()

    def get_stream_info(self, capture, stream_type):
        if not capture.isOpened():
            print(f"Unable to open {stream_type} stream")
            return
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = capture.get(cv2.CAP_PROP_FPS)
        codec = capture.get(cv2.CAP_PROP_FOURCC)
        codec_bytes = struct.unpack('4s', struct.pack('<I', int(codec)))[0]
        codec_str = codec_bytes.decode('utf-8').strip()
        print(f"{stream_type} Stream Info:\nResolution: {int(width)} x {int(height)}\nFrame rate: {fps} FPS\nCodec: {codec_str}")

    def save_to_txt(self, message):
        with open(self.acc_file_path, 'a') as file:
            file.write(message + '\n')
        print(message)

def extract_ip_from_src(src):
    ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    match = re.search(ip_pattern, src)
    return match.group(0) if match else None

# Initialize MainApp and Start Flask App
main_app = MainApp(API_KEY, FACE_DET_TH, FACE_REC_TH)

# Main entry point
if __name__ == '__main__':
    host = 'http://localhost'
    port = '8000'
    api_key = API_KEY
    use_rtsp = True
    rtsp_url = "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c12/s0/live"

    # Append database directory to the camera name
    camera_name = f"Report_c12"
    data_dir = camera_name
    database_dir = f"Report_c12"

    app.run(host='0.0.0.0', port=5001, debug=True)

    threaded_camera = MainApp(host, port, api_key, use_rtsp, camera_name ,rtsp_url, data_dir)
    while threaded_camera.active:
        threaded_camera.show_frame()


