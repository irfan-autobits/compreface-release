# video_feed_test/Recognition-api.py
import argparse
import os
import cv2
import numpy as np
import subprocess
from threading import Thread



os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

class ThreadedCamera(object):
    def __init__(self, src):
        self.src = src
        self.pipe = None
        self.frames = None

        # Start FFmpeg process to read the RTSP stream
        self.start_ffmpeg()
        
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def start_ffmpeg(self):
        command = [
            'ffmpeg',
            '-i', self.src,                     # Input RTSP stream
            '-vf', 'scale=960:540',
            '-f', 'rawvideo',                   # Output format
            '-pix_fmt', 'bgr24',                # Pixel format for OpenCV
            '-an',
            '-sn',                              # Disable subtitles
            '-tune', 'zerolatency',             # Tune for low latency
            '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    def update(self):
        frame_width = 960
        frame_height = 540
        frame_size = frame_width * frame_height * 3



        while True:
            raw_frame = self.pipe.stdout.read(frame_size)  # Assuming 1920x1080 resolution
            if len(raw_frame) != frame_size:
                print("Failed to grab frame from FFmpeg")
                break
            self.frames = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))
    
    def get_frame(self):
        if self.frames is not None:
            # Encode frame as JPEG
            _, jpeg = cv2.imencode('.jpg', self.frames)
            return jpeg.tobytes()
        return None

    def show_frame(self):
        if self.frames is not None:
            # cv2.imshow('RTSP Stream Test', self.frames)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                print("Exiting...")
                self.active = False
                cv2.destroyAllWindows()            
        else:
            print("No frame to display")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp-url", type=str, default='0')
    parser.add_argument("--data-dir", type=str, default='Report')
    parser.add_argument("--cam-id", type=str, default='0')
    args = parser.parse_args()

    try:
        threaded_camera = ThreadedCamera(args.rtsp_url)
        while True:
            threaded_camera.show_frame()
    except Exception as e:
        print(f"Error: {e}")