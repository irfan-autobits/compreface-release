import logging
import subprocess
import cv2
import argparse
import time
from threading import Thread

from compreface import CompreFace
from compreface.service import RecognitionService
import numpy as np

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--api-key", help="CompreFace recognition service API key", type=str, default='7b8d9398-b95e-4e47-bc2f-d5faddd7dd30')
    parser.add_argument("--host", help="CompreFace host", type=str, default='http://localhost')
    parser.add_argument("--port", help="CompreFace port", type=str, default='8000')
    parser.add_argument("--rtsp-url", help="CompreFace port", type=str, default='rtsp://autobits:Autobits@1234@192.168.1.202:554')

    args = parser.parse_args()

    return args

class ThreadedCamera:
    def __init__(self, api_key, host, port, rtsp_url):
        self.active = True
        self.results = []
        self.start_ffmpeg(rtsp_url)

        compre_face: CompreFace = CompreFace(host, port, {
            "limit": 0,
            "det_prob_threshold": 0.8,
            "prediction_count": 1,
            "status": False
        })

        self.recognition: RecognitionService = compre_face.init_face_recognition(api_key)

        self.FPS = 1/30

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


            # if self.results:
            #     results = self.results
            #     for result in results:
            #         box = result.get('box')
            #         subjects = result.get('subjects')
            #         if box:
            #             cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
            #                           pt2=(box['x_max'], box['y_max']), color=(0, 255, 0), thickness=1)
            #             if subjects:
            #                 subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
            #                 subject = f"Subject: {subjects[0]['subject']}"
            #                 similarity = f"Similarity: {subjects[0]['similarity']}"
            #                 cv2.putText(self.frame, subject, (box['x_max'], box['y_min'] + 75),
            #                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            #                 cv2.putText(self.frame, similarity, (box['x_max'], box['y_min'] + 95),
            #                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            #             else:
            #                 subject = f"No known faces"
            #                 cv2.putText(self.frame, subject, (box['x_max'], box['y_min'] + 75),
            #                             cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)

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
        start_time = time.time()
        # data = self.recognition.recognize(byte_im)
        api_time = time.time() - start_time
        # logging.info(f"API response time: {api_time} seconds")
        print(f"API response time: {api_time} seconds")
        # self.results = data.get('result')
        


if __name__ == '__main__':
    args = parseArguments()
    threaded_camera = ThreadedCamera(args.api_key, args.host, args.port, args.rtsp_url)
    while threaded_camera.is_active():
        threaded_camera.update()