import argparse
import os
import cv2
import numpy as np
import subprocess
from threading import Thread
import queue

os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

class ThreadedCamera(object):
    def __init__(self, src, frame_queue):
        self.src = src
        self.pipe = None
        self.frames = None
        self.frame_queue = frame_queue
        
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
            raw_frame = self.pipe.stdout.read(frame_size)  # Assuming 960x540 resolution
            if len(raw_frame) != frame_size:
                print("Failed to grab frame from FFmpeg")
                break
            self.frames = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))
            if self.frames is not None:
                self.frame_queue.put(self.frames)  # Send frame to the main process

    def show_frame(self):
        if self.frames is not None:
            # cv2.imshow('RTSP Stream Test', self.frames)
            cv2.waitKey(1)
        else:
            print("No frame to display")

def run_rtsp_stream(rtsp_url, frame_queue):
    """Run the Recognition-api.py script for a given RTSP URL and receive frames."""
    threaded_camera = ThreadedCamera(rtsp_url, frame_queue)
    while True:
        # Frames are being received from the thread and sent to the queue
        if not frame_queue.empty():
            frame = frame_queue.get()
            # Process the frame here in the main process (e.g., display it)
            # cv2.imshow(f"Stream from {rtsp_url}", frame)
            cv2.waitKey(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp-url", type=str, default='0')
    args = parser.parse_args()

    frame_queue = queue.Queue()  # Queue to receive frames from the child process

    try:
        run_rtsp_stream(args.rtsp_url, frame_queue)
    except Exception as e:
        print(f"Error: {e}")
