import os
import cv2
import numpy as np
import subprocess
from threading import Thread

os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

class ThreadedCamera(object):
    def __init__(self, src='rtsp://autobits:Autobits@1234@192.168.1.202:554'):
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
        # Command to launch FFmpeg to read RTSP stream and output as raw video frames
        command = [
            'ffmpeg',
            '-i', self.src,             # Input RTSP stream
            '-f', 'rawvideo',           # Output format
            '-pix_fmt', 'bgr24',        # Pixel format for OpenCV
            '-an',                       # Disable audio
            '-sn',                       # Disable subtitles
            '-tune', 'zerolatency',     # Tune for low latency
            '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    def update(self):
        while True:
            # Read raw frames from FFmpeg
            raw_frame = self.pipe.stdout.read(1920 * 1080 * 3)  # Assuming 1920x1080 resolution
            if len(raw_frame) != 1920 * 1080 * 3:
                print("Failed to grab frame from FFmpeg")
                break  # Stop the loop if no frame is captured
            
            # Convert the raw bytes to a NumPy array
            self.frames = np.frombuffer(raw_frame, np.uint8).reshape((1080, 1920, 3))

    def show_frame(self):
        if self.frames is not None:
            cv2.imshow('RTSP Stream Test', self.frames)
            cv2.waitKey(1)  # Adjust the wait time as necessary
        else:
            print("No frame to display")

if __name__ == '__main__':
    src = 'rtsp://autobits:Autobits%401234@192.168.1.202:554'
    try:
        threaded_camera = ThreadedCamera(src)
        while True:
            threaded_camera.show_frame()
    except Exception as e:
        print(f"Error: {e}")
