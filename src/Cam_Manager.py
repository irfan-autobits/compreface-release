import cv2
import subprocess
import threading
import numpy as np

class CameraManager:
    def __init__(self,camera_id, rtsp_url=None):
        self.use_rtsp = True
        self.capture = None
        self.pipe = None
        self.frame = None
        self.lock = threading.Lock()
        self.start_ffmpeg(rtsp_url)
        self.camera_id = camera_id
        # if use_rtsp:
        #     self.start_ffmpeg(rtsp_url)
        # else:
        #     self.capture = cv2.VideoCapture(0)
        
        self.frame_width = 960
        self.frame_height = 540

    def start_ffmpeg(self, rtsp_url):
        command = [
            'nice', '-n', '10',    # Lower priority
            'ffmpeg',
            '-i', rtsp_url,  
            '-vf', 'scale=960:540',           
            '-f', 'rawvideo',      
            '-pix_fmt', 'bgr24',   
            '-an',                  
            '-sn',                  
            '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    def get_frame(self):
        if self.use_rtsp and self.pipe:
            frame_size = self.frame_width * self.frame_height * 3
            raw_frame = self.pipe.stdout.read(frame_size)
            if len(raw_frame) != frame_size:
                print("Failed to grab frame from FFmpeg")

                return None
            with self.lock:
                self.frame = np.frombuffer(raw_frame, np.uint8).reshape((self.frame_height, self.frame_width, 3))
        elif self.capture.isOpened():
            with self.lock:
                ret, frame = self.capture.read()
                if ret:
                    self.frame = frame
        return self.frame

    def release(self):
        if self.pipe:
            self.pipe.terminate()
        if self.capture:
            self.capture.release()

    def update_frame(self, frame):
        self.current_frame = frame