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

os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

# Directory to store employee images
database_dir = 'Report'
shutil.rmtree(database_dir, ignore_errors=True)
os.makedirs(database_dir, exist_ok=True)
print('Created/checked database_dir')
excel_name = 'face_recognition_results.xlsx'
excel_path = os.path.join(database_dir, excel_name)
txt_name = 'face_recognition_results.txt'
acc_file_path = os.path.join(database_dir, txt_name)

class ThreadedCamera:
    def __init__(self, host, port, api_key, use_rtsp, src='0'):
        self.active = True
        self.results = []

        if use_rtsp:
            self.start_ffmpeg(src)
        else:
            self.capture = cv2.VideoCapture(0)
            self.get_stream_info(self.capture, "Internal Camera")
        
        compre_face = CompreFace(host, port, {
            "limit": 0,
            "det_prob_threshold": 0.5,
            "prediction_count": 1,
            "status": False
        })

        self.recognition = compre_face.init_face_recognition(api_key)

        # Set desired FPS
        self.FPS = 1 / 25
        self.FPS_MS = int(self.FPS * 1000)
        
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def start_ffmpeg(self, src):
        command = [
            'ffmpeg',
            '-i', src,             
            '-f', 'rawvideo',      
            '-pix_fmt', 'bgr24',   
            '-an',                  
            '-sn',                  
            '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)


    def update(self):
        print("Started")
        while True:
            if self.pipe:
                raw_frame = self.pipe.stdout.read(1920 * 1080 * 3)  # Assuming 1920x1080 resolution
                if len(raw_frame) != 1920 * 1080 * 3:
                    print("Failed to grab frame from FFmpeg")
                    break  # Stop the loop if no frame is captured
                
                # Convert the raw bytes to a mutable NumPy array
                self.frame = np.frombuffer(raw_frame, np.uint8).reshape((1080, 1920, 3)).copy()

    def show_frame(self, frame_count):
        if not hasattr(self, 'frame'):
            return

        _, im_buf_arr = cv2.imencode(".jpg", self.frame)
        byte_im = im_buf_arr.tobytes()
        data = self.recognition.recognize(byte_im)
        self.results = data.get('result')

        if self.results:
            results = self.results
            for result in results:
                box = result.get('box')
                subjects = result.get('subjects')
                if box:
                    if subjects and subjects[0]['similarity'] >= 0.975:
                    
                        subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
                        subject = f"{subjects[0]['subject']}"
                        similarity = f"Similarity: {subjects[0]['similarity']}"
                        cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
                                pt2=(box['x_max'], box['y_max']), color=(0, 255, 0), thickness=1)
                        cv2.putText(self.frame, subject, (box['x_min']+5, box['y_min'] - 15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                        face_image_name = f"{timestamp}_{subjects[0]['subject']}_({subjects[0]['similarity']})_{frame_count}.jpg"
                        with open(acc_file_path, 'a') as file:
                                file.write(f'Saved detected face as: {face_image_name}'+ '\n')
                        print(f"detected if face as: {face_image_name}")
                    else:
                        subject = f"Unknown"
                        cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
                                pt2=(box['x_max'], box['y_max']), color=(0, 0, 255), thickness=1)
                        cv2.putText(self.frame, subject, (box['x_min']+5, box['y_min'] - 15),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                        face_image_name = f"{timestamp}_{frame_count}.jpg"
                        with open(acc_file_path, 'a') as file:
                                file.write(f'Saved detected face as: {face_image_name}'+ '\n')
                        print(f"detected face as: {face_image_name}") 
        cv2.imshow('Frame', self.frame)
        cv2.waitKey(self.FPS_MS)


    def get_stream_info(self, capture, stream_type):
        if not capture.isOpened():
            print(f"Unable to open {stream_type} stream")
            return
    
        # Retrieve and print properties
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = capture.get(cv2.CAP_PROP_FPS)
        codec = capture.get(cv2.CAP_PROP_FOURCC)

        # Unpack the codec and decode it properly
        codec_bytes = struct.unpack('4s', struct.pack('<I', int(codec)))[0]
        codec_str = codec_bytes.decode('utf-8').strip()

        print(f"{stream_type} Stream Info:")
        print(f"Resolution: {int(width)} x {int(height)}")
        print(f"Frame rate: {fps} FPS")
        print(f"Codec: {codec_str}")
        print("------------------------------")
        

if __name__ == '__main__':
    host = 'http://localhost'
    port = '8000'
    api_key = 'b32c9ed2-0a51-47c7-9eb6-6d2063834a0f'
    use_rtsp = True
    src = 'rtsp://autobits:Autobits@1234@192.168.1.202:554'
    src1 = 'rtsp://autobits:Autobits@123@192.168.1.204:554'
    
    threaded_camera = ThreadedCamera(host, port, api_key, use_rtsp, src1)
    frame_interval = 1  # Process every frame
    frame_count = 0 

    while True:
        try:
            frame_count += 1  # Increment frame counter
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')[:-4]
            threaded_camera.show_frame(frame_count)
        except AttributeError:
            pass
