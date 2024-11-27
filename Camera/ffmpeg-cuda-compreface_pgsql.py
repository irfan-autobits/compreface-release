import json
import os
import cv2
import time
import argparse
import shutil
import numpy as np
import subprocess
from threading import Thread
from compreface import CompreFace
from compreface.service import RecognitionService
from datetime import datetime
import struct
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()
FACE_DET_TH = float(os.getenv("FACE_DET_TH", 0.8))
FACE_REC_TH = float(os.getenv("FACE_REC_TH", 0.0))
API_KEY = os.getenv("API_KEY", '00000000-0000-0000-0000-000000000002')
print(f'FACE_DET_TH = {FACE_DET_TH}')
print(f'FACE_REC_TH = {FACE_REC_TH}')

os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

# postgre - - - - - - - - - - 
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
import pytz
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class RecognitionResult(Base):
    __tablename__ = 'Hathi_recognition'

    id = Column(Integer, primary_key=True, autoincrement=True)
    camera = Column(Text)
    person = Column(Text)  # Use Text for longer strings
    accuracy = Column(Text)
    Image = Column(Text)
    time = Column(DateTime(timezone=True)) 
# -------- uncmt to stop append mode---------------------------------------
# Drop the table
Base.metadata.drop_all(engine)
print("All tables have been dropped.")
# --------------------------------------------------------------------------
# Create tables in the database
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
# # # Purge all rows from the table
# # session.query(RecognitionResult).delete()
# # session.commit()
# # print("All rows deleted from the table.")
# ----------------------------------------------------
def parseArguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp-url", help="RTSP stream URL", type=str, default='0')
    parser.add_argument("--data-dir", help="Name of the Recognized Pic Dir", type=str, default='Report')
    args = parser.parse_args()
    
    return args

class ThreadedCamera:
    def __init__(self, host, port, api_key, use_rtsp, rtsp_url='0'):
        self.active = True
        self.results = []
        self.use_rtsp = use_rtsp
        self.rtsp_url = rtsp_url
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
        
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def start_ffmpeg(self, src):
        command = [
            'nice', '-n', '10',
            'ffmpeg', '-hwaccel', 'cuda', '-i', src,
            '-vf', 'scale=960:540',  # Lower resolution to reduce load
            '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-an', '-sn', '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    def update(self):
        print("Started")
        frame_width = 960
        frame_height = 540
        frame_size = frame_width * frame_height * 3  # bgr24: 3 bytes per pixel
        while True:
            if self.use_rtsp:
                if self.pipe:
                    raw_frame = self.pipe.stdout.read(frame_size)
                    if len(raw_frame) != frame_size:
                        print("Failed to grab frame from FFmpeg")
                        break
                    self.frame = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3)).copy()
            elif self.use_rtsp == False:
                if self.capture.isOpened():
                    (self.status, self.frame) = self.capture.read()
                    if not self.status or self.frame is None or self.frame.size == 0:
                        print("No frame received, skipping...")
                        time.sleep(self.FPS)
                        continue

            if self.results:
                for result in self.results:
                    self.process_recognition(result)

    def process_recognition(self, result):
        box = result.get('box')
        subjects = result.get('subjects')
        if box:
            if subjects and subjects[0]['similarity'] >= FACE_REC_TH:
                subject = f"{subjects[0]['subject']}"
                similarity = f"Similarity: {subjects[0]['similarity']}"
                color = (0, 255, 0)
                self.draw_rectangle_and_text(box, subject, similarity, color)
                self.save_image_and_data(subject, similarity, box)
            else:
                subject = "Unknown"
                color = (0, 0, 255)
                self.draw_rectangle_and_text(box, subject, "100%", color)
                self.save_image_and_data(subject, '100%', box)

    def draw_rectangle_and_text(self, box, subject, similarity, color):
        cv2.rectangle(self.frame, (box['x_min'], box['y_min']), 
                      (box['x_max'], box['y_max']), color, 1)
        cv2.putText(self.frame, subject, (box['x_min']+5, box['y_min'] - 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)
        # cv2.putText(self.frame, similarity, (box['x_min']+5, box['y_max'] + 15),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 1)

    def save_image_and_data(self, subject, similarity, box):
        timestamp = datetime.now().strftime('%y%m%d-%H:%M:%S-%f')[:-4]
        face_image = self.frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]
        face_image_name = f"{timestamp}_{subject}_({similarity})_{frame_count}.jpg"
        database_img_dir = os.path.join(database_dir, subject)
        os.makedirs(database_img_dir, exist_ok=True)
        face_image_path = os.path.join(database_img_dir, face_image_name)

        cv2.imwrite(face_image_path, face_image)
        save_to_txt(f"Saved detected face as: {face_image_name}")

        # Save to PostgreSQL
        recognition_result = RecognitionResult(
            camera=self.extract_ip_from_src(self.rtsp_url) if self.use_rtsp else 'Device_camera',
            person=subject,
            accuracy=similarity,
            Image=face_image_path,
            time=datetime.now()
        )
        session.add(recognition_result)
        session.commit()

    def extract_ip_from_src(self, src):
        ip_pattern = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        match = re.search(ip_pattern, src)
        return match.group(0) if match else None

    def show_frame(self, frame_count):
        if not hasattr(self, 'frame'):
            return

        _, im_buf_arr = cv2.imencode(".jpg", self.frame)
        byte_im = im_buf_arr.tobytes()
        try:
            data = self.recognition.recognize(byte_im)
            self.results = data.get('result')
        except json.JSONDecodeError:
            print("Failed to decode JSON response.")
            self.results = []

        cv2.imshow('Frame', self.frame)
        cv2.waitKey(self.FPS_MS)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or key == 27:
            print("Exiting...")
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

        print(f"{stream_type} Stream Info:")
        print(f"Resolution: {int(width)} x {int(height)}")
        print(f"Frame rate: {fps} FPS")
        print(f"Codec: {codec_str}")
        print("------------------------------")

# Helper functions
def save_to_txt(message):
    with open(acc_file_path, 'a') as file:
        file.write(message + '\n')
    print(message)


if __name__ == '__main__':
    host = 'http://localhost'
    port = '8000'
    api_key = API_KEY
    use_rtsp = True
    args = parseArguments()
    threaded_camera = ThreadedCamera(host, port, api_key, use_rtsp, args.rtsp_url)
    frame_count = 0

    database_dir = args.data_dir
    shutil.rmtree(database_dir, ignore_errors=True) # --------uncmt to stop append mode 
    os.makedirs(database_dir, exist_ok=True)
    acc_file_path = os.path.join(database_dir, "logs.txt")

    while True:
        threaded_camera.show_frame(frame_count)
        frame_count += 1