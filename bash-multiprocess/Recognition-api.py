# bash-multiprocess/ffmpeg-cuda-batch-compreface.py
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
from sqlalchemy import QueuePool, create_engine, Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
import re
from multiprocessing import Queue
# Load environment variables from .env file
load_dotenv()
FACE_DET_TH = float(os.getenv("FACE_DET_TH", 0.8))
FACE_REC_TH = float(os.getenv("FACE_REC_TH", 0.0))
API_KEY = os.getenv("API_KEY", '00000000-0000-0000-0000-000000000002')
print(f'FACE_DET_TH = {FACE_DET_TH}')
print(f'FACE_REC_TH = {FACE_REC_TH}')

os.environ['QT_QPA_PLATFORM'] = 'xcb'

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
        self.start_time = time.time()
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

    def start_ffmpeg(self, src):
        command = [
            'nice', '-n', '10',
            'ffmpeg', 
            # '-hwaccel', 'cuda', 
            '-i', src,
            '-vf', 'scale=960:540',
            '-f', 'rawvideo', 
            '-pix_fmt', 'bgr24', 
            # '-pix_fmt', 'nv12', 
            # '-pix_fmt', 'yuv420p',
            '-an', '-sn', '-'
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

    def show_frame(self, frame_count, frame_queue: Queue):
        if self.frame is None:
            return
    
        with self.lock:
            display_frame = self.frame.copy()
    
        cv2.imshow('Frame', display_frame)
    
        # Check if queue is full to avoid blocking
        if not frame_queue.full():
            frame_queue.put(display_frame)
        else:
            print("Frame queue is full!")  # Debug print
    
        key = cv2.waitKey(self.FPS_MS) & 0xFF
        if key == ord('q') or key == 27:
            print("Exiting..................................................")
            self.active = False
            cv2.destroyAllWindows()

import signal
import sys

def signal_handler(sig, frame):
    print("Interrupt received. Cleaning up...")
    print("Exiting..................................................")
    cv2.destroyAllWindows()
    sys.exit(0)

# Attach the handler
signal.signal(signal.SIGINT, signal_handler)

# Main entry point
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp-url", type=str, default='0')
    parser.add_argument("--data-dir", type=str, default='Report')
    parser.add_argument("--frame-queue", type=str, default='0')
    args = parser.parse_args()
    frame_count = 0 
    host = 'http://localhost'
    port = '8000'
    api_key = API_KEY
    use_rtsp = args.rtsp_url != '0'

    frame_queue = Queue()
    print(f"frame_queue initialized: {frame_queue}")


    # Append database directory to the camera name
    camera_name = f"{args.data_dir}"
    
    threaded_camera = ThreadedCamera(host, port, api_key, use_rtsp, camera_name ,args.rtsp_url, args.data_dir)
    database_dir = args.data_dir

    while threaded_camera.active:
        try :
            # if frame_count % 2 == 0:
            threaded_camera.show_frame(frame_count, frame_queue)
            frame_count+=1
        except KeyboardInterrupt:
            # This ensures that pressing Ctrl+C will exit cleanly
            signal_handler(None, None)
            break
