import logging
import os
import subprocess
import cv2
import argparse
import time
from threading import Thread

from compreface import CompreFace
from compreface.service import RecognitionService
from dotenv import load_dotenv
import numpy as np

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
        self.start_ffmpeg(rtsp_url)

        compre_face: CompreFace = CompreFace(host, port, {
            "limit": 0,
            "det_prob_threshold": FACE_DET_TH,
            "prediction_count": 1,
            "status": False
        })

        self.recognition: RecognitionService = compre_face.init_face_recognition(api_key)

        self.FPS = 1/25

        # Start frame retrieval thread
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()

    def start_ffmpeg(self, src):
        command = [
            'nice', '-n', '10',    # Lower priority
            'ffmpeg',
            '-i', src, 
            '-vf', 'scale=960:540',
            '-f', 'rawvideo',      
            '-pix_fmt', 'bgr24',   
            '-an',                  
            '-sn',                  
            '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)
        
    def show_frame(self):
        print("Started")
        while True:
            raw_frame = self.pipe.stdout.read(960 * 540 * 3)  # Assuming 1920x1080 resolution
            self.frame = np.frombuffer(raw_frame, np.uint8).reshape((540, 960, 3)).copy()


            if self.results:
                results = self.results
                for result in results:
                    box = result.get('box')
                    subjects = result.get('subjects')
                    if box:
                        cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
                                      pt2=(box['x_max'], box['y_max']), color=(0, 255, 0), thickness=1)
                        if subjects:
                            subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
                            subject = f"Subject: {subjects[0]['subject']}"
                            similarity = f"Similarity: {subjects[0]['similarity']}"
                            cv2.putText(self.frame, subject, (box['x_max'], box['y_min'] + 75),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            cv2.putText(self.frame, similarity, (box['x_max'], box['y_min'] + 95),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                        else:
                            subject = f"No known faces"
                            cv2.putText(self.frame, subject, (box['x_max'], box['y_min'] + 75),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

            cv2.imshow('CompreFace demo', self.frame)
            time.sleep(self.FPS)

            if cv2.waitKey(1) & 0xFF == 27:
                self.capture.release()
                cv2.destroyAllWindows()
                self.active=False

    def is_active(self):
        return self.active

    def update(self):
        if not hasattr(self, 'frame'):
            return

        _, im_buf_arr = cv2.imencode(".jpg", self.frame)
        byte_im = im_buf_arr.tobytes()
        # start_time = time.time()
        data = self.recognition.recognize(byte_im)
        # api_time = time.time() - start_time
        # logging.info(f"API response time: {api_time} seconds")
        # print(f"API response time: {api_time} seconds")
        self.results = data.get('result')
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp-url", type=str, default='0')
    parser.add_argument("--data-dir", type=str, default='Report')
    args = parser.parse_args()
    frame_count = 0 
    host = 'http://localhost'
    port = '8000'
    api_key = API_KEY
    use_rtsp = args.rtsp_url != '0'


    # Append database directory to the camera name
    camera_name = f"{args.data_dir}"
    threaded_camera = ThreadedCamera(host, port, api_key, use_rtsp, camera_name ,args.rtsp_url, args.data_dir)
    while threaded_camera.is_active():
        if frame_count % 1 ==0:
            threaded_camera.update()
        frame_count+=1
