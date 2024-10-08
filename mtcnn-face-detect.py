import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display
import cv2
import argparse
import time
import shutil
import numpy as np
from threading import Thread
import pandas as pd
from datetime import datetime
import mediapipe as mp
from mtcnn import MTCNN

# Generate the timestamp
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
# Directory to store employee images
database_dir = 'Report'
# Create the main database directory if it doesn't exist
shutil.rmtree(database_dir, ignore_errors=True)
os.makedirs(database_dir, exist_ok=True)
print('created/checked database_dir')
excel_name = 'face_recognition_results.xlsx'
excel_path = os.path.join(database_dir, excel_name)
txt_name = 'face_recognition_results.txt'
acc_file_path = os.path.join(database_dir, txt_name)

detector = MTCNN()

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--api-key", help="CompreFace recognition service API key", type=str, default='88910b39-ac74-4fea-afcd-cfc446de2e6e')
    parser.add_argument("--host", help="CompreFace host", type=str, default='http://localhost')
    parser.add_argument("--port", help="CompreFace port", type=str, default='8000')
    parser.add_argument("--rtsp", help="Use RTSP stream (True/False)", type=str, default='False')
    parser.add_argument("--rtsp-url", help="RTSP stream URL", type=str, default='rtsp://autobits:Autobits@123@192.168.1.204:554')

    args = parser.parse_args()
    args.rtsp = args.rtsp.lower() == 'true'
    return args
class ThreadedCamera:
    def __init__(self, api_key, host, port, use_rtsp, rtsp_url):
        self.active = True
        self.results = None  # Store the face landmarks results
        self.faces = []
        if use_rtsp:
            self.capture = cv2.VideoCapture(rtsp_url)
        else:
            self.capture = cv2.VideoCapture(0)

        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        self.FPS = 1 / 30
        self.FPS_MS = int(self.FPS * 1000)

        # Start frame retrieval and display thread
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()

    def show_frame(self):
        print("Started")
        while self.capture.isOpened():
            start_time = time.time()
            (status, frame_raw) = self.capture.read()
            # if not status or frame_raw is None or frame_raw.size == 0:
            #     print("No frame received, skipping...")
            #     time.sleep(self.FPS)
            #     continue  # Skip the rest of the loop if no frame

            # self.frame = cv2.flip(frame_raw, 1)
            self.frame = frame_raw
            # self.faces = detector.detect_faces(self.frame)
            # Draw bounding boxes
            for face in self.faces:
                x, y, width, height = face['box']
                cv2.rectangle(self.frame, (x, y), (x + width, y + height), (0, 255, 0), 2)

            cv2.imshow('Face Detection', self.frame)
            time.sleep(self.FPS)
            cv2.waitKey(self.FPS_MS)

            if cv2.waitKey(1) & 0xFF == 27 or 0xFF == ord('q'):
                self.capture.release()
                cv2.destroyAllWindows()
                self.active = False

    def is_active(self):
        return self.active

    def update(self, frame_count):
        if not hasattr(self, 'frame'):
            return
        
        # Detect faces
        self.faces = detector.detect_faces(self.frame)



# Main execution
if __name__ == '__main__':
    args = parseArguments()
    threaded_camera = ThreadedCamera(args.api_key, args.host, args.port, args.rtsp, args.rtsp_url)
    frame_interval = 1  # Process every frame
    frame_count = 0 

    while threaded_camera.is_active():
        frame_count += 1
        threaded_camera.update(frame_count)



    
