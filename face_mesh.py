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

# initialize facemesh
mp_face_mesh = mp.solutions.face_mesh.FaceMesh()

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
            # image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            # self.results = mp_face_mesh.process(image)  
            # If results are available from update(), draw landmarks
            if self.results and self.results.multi_face_landmarks:
                for landmarks in self.results.multi_face_landmarks:
                    # Draw landmarks on the frame
                    mp.solutions.drawing_utils.draw_landmarks(
                                                                 self.frame, landmarks, mp.solutions.face_mesh.FACEMESH_CONTOURS
                                                             )

            cv2.imshow('CompreFace demo', self.frame)
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

        # Process the frame to detect landmarks
        image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        self.results = mp_face_mesh.process(image)  # Store the results
        if self.results:
            print('got result')

# Main execution
if __name__ == '__main__':
    args = parseArguments()
    threaded_camera = ThreadedCamera(args.api_key, args.host, args.port, args.rtsp, args.rtsp_url)
    frame_interval = 1  # Process every frame
    frame_count = 0 

    while threaded_camera.is_active():
        frame_count += 1
        # if frame_count % frame_interval != 0:
        #     continue
        threaded_camera.update(frame_count)



    
