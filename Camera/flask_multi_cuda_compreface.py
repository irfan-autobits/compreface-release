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

from flask import Flask, Response
import threading

app = Flask(__name__)

# Dictionary to store ThreadedCamera instances
cameras = {}

# Thread lock for thread safety
lock = threading.Lock()

# Load environment variables from .env file
load_dotenv()
FACE_DET_TH = float(os.getenv("FACE_DET_TH", 0.8))
FACE_REC_TH = float(os.getenv("FACE_REC_TH", 0.0))
API_KEY = os.getenv("API_KEY", '00000000-0000-0000-0000-000000000002')
print(f'FACE_DET_TH = {FACE_DET_TH}')
print(f'FACE_REC_TH = {FACE_REC_TH}')

os.environ['QT_QPA_PLATFORM'] = 'xcb'

# Database setup
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

class RecognitionResult(Base):
    __tablename__ = 'Hathi_recognition'
    id = Column(Integer, primary_key=True, autoincrement=True)
    camera = Column(Text)
    person = Column(Text)
    accuracy = Column(Text)
    image = Column(Text)
    time = Column(DateTime(timezone=True))
# -------- uncmt to stop append mode---------------------------------------
# Drop the table
# Base.metadata.drop_all(engine)
# print("All tables have been dropped.")
# --------------------------------------------------------------------------
# Create tables in the database
Base.metadata.create_all(engine)
# Regular session setup (no async)
Session = sessionmaker(engine)

class ThreadedCamera:
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
            if camera.results:
                camera.save_to_database(camera.results)
                camera.results = []
                # time.sleep(1)  # Batch save every n seconds

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
                    # batch.append({
                    #     "camera": self.camera_name,
                    #     "person": subjects[0]['subject'],
                    #     "accuracy": f"{subjects[0]['similarity'] * 100:.0f}%",
                    #     "image": self.save_image(subjects[0]['subject'], subjects[0]['similarity'], box, False),
                    #     "time": datetime.now()
                    # })
                    self.save_image(subjects[0]['subject'], subjects[0]['similarity'], box, False)
                    color = (0, 255, 0)
                    self.draw_rectangle_and_text(box, subjects[0]['subject'], color)
                else:
                    # batch.append({
                    #     "camera": self.camera_name,
                    #     "person": "Unknown",
                    #     "accuracy": f"{(1 - subjects[0]['similarity']) * 100:.0f}%",
                    #     "image": self.save_image(f"Unknown_{subjects[0]['subject']}", f"{subjects[0]['similarity']}", box, True),
                    #     "time": datetime.now()
                    # })
                    self.save_image(f"Unknown_{subjects[0]['subject']}", f"{subjects[0]['similarity']}", box, True)
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

    def save_to_txt(self, message):
        with open(self.acc_file_path, 'a') as file:
            file.write(message + '\n')
        print(message)

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

def extract_ip_from_src(src):
    ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
    match = re.search(ip_pattern, src)
    return match.group(0) if match else None

def generate_frames(camera_id):
    """Generate video frames for a specific camera."""
    while cameras[camera_id].active:
        with lock:
            if cameras[camera_id].frame is None:
                continue
            _, buffer = cv2.imencode('.jpg', cameras[camera_id].frame)
            frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed/<camera_id>')
def video_feed(camera_id):
    """Stream video for a specific camera."""
    if camera_id not in cameras:
        return f"Camera {camera_id} not found!", 404
    return Response(generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask():
    """Start the Flask server."""
    app.run(host='0.0.0.0', port=5001, threaded=True)

if __name__ == '__main__':
    # Camera configuration: {camera_id: rtsp_url}
    camera_config = {
        "c4": "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c4/s0/live",
        "c5": "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c5/s0/live"
    }

    # Initialize ThreadedCamera instances
    for camera_id, rtsp_url in camera_config.items():
        cameras[camera_id] = ThreadedCamera(
            host='http://localhost', 
            port='8000', 
            api_key=API_KEY, 
            use_rtsp=True, 
            camera_name=camera_id, 
            rtsp_url=rtsp_url,
            data_dir=f"Test_{camera_id}"
        )

    # Start the Flask server in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Keep processing frames for all cameras
    while any(camera.active for camera in cameras.values()):
        for camera in cameras.values():
            camera.show_frame()